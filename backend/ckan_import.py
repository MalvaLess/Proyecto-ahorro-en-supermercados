import sys
import os

sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv()

import csv
from app.app import app
from models.models import db, Brand, Product
from datetime import datetime
from utils import normalize_brand

PRODUCTOS_CSV = os.path.join(os.path.dirname(__file__), "CKAN", "productos.csv")


def importar_productos():
    with app.app_context():
        with open(PRODUCTOS_CSV, encoding="latin-1") as f:
            reader = csv.DictReader(f, delimiter=";")
            contador = 0
            for row in reader:
                nombre = row["producto"].strip()
                marca_nombre = row["marca"].strip()
                ean = row["id.producto"].strip()
                especificacion = (
                    row["especificacion"].strip() if row["especificacion"] else None
                )

                # Buscar o crear marca
                brand = Brand.query.filter_by(normalizedName=normalize_brand(marca_nombre)).first()
                if not brand:
                    brand = Brand(name=marca_nombre, normalizedName=normalize_brand(marca_nombre), updatedAt=datetime.now())
                    db.session.add(brand)
                    db.session.flush()

                # Buscar o crear producto por EAN
                product = Product.query.filter_by(externalIdCkan=int(ean)).first()
                if not product:
                    product = Product(
                        brandId=brand.brandId,
                        name=nombre,
                        normalizedName=nombre.lower(),
                        externalIdCkan=int(row["id.producto"]),
                        description=especificacion,
                        unit="un",
                        updatedAt=datetime.now(),
                    )
                    db.session.add(product)
                    contador += 1

            db.session.commit()
            print(f"Importados {contador} productos de CKAN")


if __name__ == "__main__":
    importar_productos()
