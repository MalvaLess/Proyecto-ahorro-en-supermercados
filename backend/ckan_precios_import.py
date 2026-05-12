import sys
import os

sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv()

import csv
from datetime import datetime
from app.app import app
from models.models import db, Store, Product, StoreProduct, PriceSnapshot

PRECIOS_CSV = os.path.join(os.path.dirname(__file__), "CKAN", "precios_2026.csv")
CHUNK_SIZE = 10000


def importar_precios():
    with app.app_context():
        # Cargar en memoria los IDs que nos interesan
        print("Cargando stores válidas...")
        stores = Store.query.filter(Store.externalIdSipc.isnot(None)).all()
        store_map = {s.externalIdSipc: s.storeId for s in stores}
        print(f"  {len(store_map)} stores encontradas")

        print("Cargando productos válidos...")
        products = Product.query.filter(Product.externalIdCkan.isnot(None)).all()
        product_map = {p.externalIdCkan: p.productId for p in products}
        print(f"  {len(product_map)} productos encontrados")

        # Procesar CSV en chunks
        # Primero encontrar el precio más reciente por (producto, store)
        print("Procesando CSV...")
        precios_recientes = {}  # {(storeId, productId): {precio, fecha}}

        with open(PRECIOS_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            chunk = []
            total = 0

            for row in reader:
                chunk.append(row)
                if len(chunk) >= CHUNK_SIZE:
                    procesar_chunk(chunk, store_map, product_map, precios_recientes)
                    total += len(chunk)
                    print(f"  Procesadas {total} filas...")
                    chunk = []

            # Procesar el último chunk
            if chunk:
                procesar_chunk(chunk, store_map, product_map, precios_recientes)
                total += len(chunk)
                print(f"  Procesadas {total} filas en total")

        # Insertar los precios más recientes en la DB
        print(f"Insertando {len(precios_recientes)} precios en la base de datos...")
        contador = 0
        for (store_id, product_id), datos in precios_recientes.items():
            # Buscar o crear store_product
            store_product = StoreProduct.query.filter_by(
                storeId=store_id, productId=product_id
            ).first()
            if not store_product:
                store_product = StoreProduct(
                    storeId=store_id,
                    productId=product_id,
                    isAvailable=True,
                    updatedAt=datetime.now(),
                )
                db.session.add(store_product)
                db.session.flush()

            # Insertar precio
            snapshot = PriceSnapshot(
                storeProductId=store_product.storeProductId,
                price=datos["precio"],
                currency="UYU",
                capturedAt=datos["fecha"],
                source="CKAN",
            )
            db.session.add(snapshot)
            contador += 1

            # Commit cada 1000 para no saturar la sesión
            if contador % 1000 == 0:
                db.session.commit()
                print(f"  Insertados {contador} precios...")

        db.session.commit()
        print(f"Importación completada. {contador} precios insertados.")


def procesar_chunk(chunk, store_map, product_map, precios_recientes):
    for row in chunk:
        try:
            establecimiento_id = int(row["Establecimiento"])
            producto_id = int(row["Presentacion_Producto"])
            precio = float(row["Precio"])
            fecha = datetime.strptime(row["Fecha"], "%Y-%m-%d")
        except (ValueError, KeyError):
            continue

        # Solo procesar si la store y el producto existen en nuestra DB
        store_id = store_map.get(establecimiento_id)
        product_id = product_map.get(producto_id)

        if not store_id or not product_id:
            continue

        clave = (store_id, product_id)

        # Guardar solo el precio más reciente
        if clave not in precios_recientes or fecha > precios_recientes[clave]["fecha"]:
            precios_recientes[clave] = {
                "precio": precio,
                "fecha": fecha,
            }


if __name__ == "__main__":
    importar_precios()
