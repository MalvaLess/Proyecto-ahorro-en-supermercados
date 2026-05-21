import requests
import time
import sys
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from app.app import app
from models.models import (
    db,
    Brand,
    Category,
    Product,
    ProductCategory,
    StoreProduct,
    PriceSnapshot,
    Store,
    StoreChain,
)
from datetime import datetime
from sqlalchemy import literal, func
from utils import normalize_brand

ENDPOINT = "https://www.tata.com.uy/api/graphql"
STORE_CHAIN_NAME = "Ta-Ta"

TATA_CATEGORIAS = {
    "congelados": "Congelados",
    "bebidas":    "Bebidas",
    "limpieza":   "Limpieza",
    "frescos":    "Frescos",
    "almacen":    "Almacén",
}

# Mapa de categoriesIds numéricos para asignación de categoría al guardar
TATA_CATEGORIAS_IDS = {
    28:  "Congelados",
    6:   "Bebidas",
    139: "Limpieza",
    196: "Frescos",
    191: "Almacén",
}

QUERY = """
query ProductsQuery(
    $first: Int,
    $after: String,
    $sort: String,
    $term: String,
    $selectedFacets: [SelectedFacetInput]
) {
    search(
        first: $first,
        after: $after,
        sort: $sort,
        term: $term,
        selectedFacets: $selectedFacets
    ) {
        products {
            edges {
                node {
                    productId
                    sku
                    name
                    gtin
                    brand { name }
                    image { url }
                    categoriesIds
                    offers {
                        offers {
                            price
                            listPrice
                            availability
                        }
                    }
                }
            }
        }
    }
}
"""

def scrape_categoria(category_slug, pagina=0, cantidad=50):
    payload = {
        "operationName": "ProductsQuery",
        "variables": {
            "first": cantidad,
            "after": str(pagina * cantidad),
            "sort": "score_desc",
            "term": "",
            "selectedFacets": [
                {"key": "category-1", "value": category_slug},
                {
                    "key": "channel",
                    "value": '{"salesChannel":"4","regionId":"U1cjdGF0YXV5bW9udGV2aWRlbw=="}',
                },
                {"key": "locale", "value": "es-UY"},
            ],
        },
        "query": QUERY,
    }

    response = requests.post(ENDPOINT, json=payload)
    if response.status_code >= 500:
        return []
    response.raise_for_status()
    data = response.json()
    edges = data["data"]["search"]["products"]["edges"]

    resultado = []
    for edge in edges:
        p = edge["node"]
        oferta = p["offers"]["offers"][0] if p["offers"]["offers"] else None
        if not oferta:
            continue
        resultado.append(
            {
                "sku": p["sku"],
                "nombre_externo": p["name"],
                "marca_externa": p["brand"]["name"],
                "gtin": p.get("gtin"),
                "imagen": p["image"][0]["url"] if p["image"] else None,
                "precio": oferta["price"],
                "precio_lista": oferta["listPrice"],
                "disponible": oferta["availability"] == "https://schema.org/InStock",
                "categoriesIds": [int(c) for c in p.get("categoriesIds") or []],
            }
        )

    return resultado


def guardar_en_db(productos):
    with app.app_context():
        cadena = StoreChain.query.filter_by(name=STORE_CHAIN_NAME).first()
        if not cadena:
            print(f"Error: no se encontró '{STORE_CHAIN_NAME}'. Corré el seed primero.")
            return

        store = Store.query.filter_by(storeChainId=cadena.storeChainId).first()
        if not store:
            print(f"Error: no se encontró ninguna tienda para '{STORE_CHAIN_NAME}'.")
            return

        store_id = store.storeId

        for p in productos:
            # Buscar producto por GTIN en el catálogo normalizado
            product = Product.query.filter_by(ean=p["gtin"]).first()

            # Fallback 1: buscar por nombre normalizado exacto
            if not product:
                product = Product.query.filter_by(
                    normalizedName=p["nombre_externo"].lower()
                ).first()

            # Fallback 2: nombre scraper empieza con normalizedName CKAN + misma marca
            # Valida que lo que sigue al prefijo sea la marca o un número (no otro calificador de producto)
            if not product:
                brand_norm = normalize_brand(p["marca_externa"])
                if brand_norm:
                    scraper_name_lower = p["nombre_externo"].lower()
                    candidates = Product.query.join(Brand).filter(
                        literal(scraper_name_lower).op("LIKE")(func.concat(Product.normalizedName, "%")),
                        Brand.normalizedName == brand_norm
                    ).order_by(func.length(Product.normalizedName).desc()).all()
                    for candidate in candidates:
                        suffix = scraper_name_lower[len(candidate.normalizedName):].strip()
                        first_word = suffix.split()[0] if suffix else ""
                        if not first_word or first_word == brand_norm or re.match(r'^\d', first_word):
                            product = candidate
                            break

            # Si encontró producto CKAN sin EAN, enriquecerlo con el GTIN de Ta-Ta
            if product and p["gtin"] and not product.ean:
                product.ean = p["gtin"]

            if not product:
                # No existe en DB, crear producto nuevo con datos de Ta-Ta
                brand = Brand.query.filter_by(normalizedName=normalize_brand(p["marca_externa"])).first()
                if not brand:
                    brand = Brand(name=p["marca_externa"], normalizedName=normalize_brand(p["marca_externa"]), updatedAt=datetime.now())
                    db.session.add(brand)
                    db.session.flush()

                product = Product(
                    brandId=brand.brandId,
                    name=p["nombre_externo"],
                    normalizedName=p["nombre_externo"].lower(),
                    ean=p["gtin"],
                    imageURL=p["imagen"],
                    unit="un",
                    updatedAt=datetime.now(),
                )
                db.session.add(product)
                db.session.flush()

            # Buscar o crear store_product
            store_product = StoreProduct.query.filter_by(
                storeId=store_id, productId=product.productId
            ).first()
            if not store_product:
                store_product = StoreProduct(
                    storeId=store_id,
                    productId=product.productId,
                    externalSku=p["sku"],
                    externalName=p["nombre_externo"],
                    externalBrand=p["marca_externa"],
                    isAvailable=p["disponible"],
                    updatedAt=datetime.now(),
                )
                db.session.add(store_product)
                db.session.flush()
            else:
                # Actualizar disponibilidad si ya existe
                store_product.isAvailable = p["disponible"]

            # Asignar categoría padre si está en el mapa de IDs numéricos
            cat_id = next(
                (cid for cid in p.get("categoriesIds", []) if cid in TATA_CATEGORIAS_IDS),
                None
            )
            if cat_id:
                categoria = Category.query.filter_by(name=TATA_CATEGORIAS_IDS[cat_id]).first()
                if categoria:
                    existe = ProductCategory.query.filter_by(
                        productId=product.productId,
                        categoryId=categoria.categoryId
                    ).first()
                    if not existe:
                        db.session.add(ProductCategory(
                            productId=product.productId,
                            categoryId=categoria.categoryId
                        ))

            # Siempre insertar nuevo precio
            snapshot = PriceSnapshot(
                storeProductId=store_product.storeProductId,
                price=p["precio"],
                currency="UYU",
                capturedAt=datetime.now(),
                source="SCRAPER",
            )
            db.session.add(snapshot)

        db.session.commit()
        print(f"Guardados {len(productos)} productos en la base de datos")


if __name__ == "__main__":
    for slug, nombre in TATA_CATEGORIAS.items():
        pagina = 0
        print(f"\n=== Categoría: {nombre} ===")
        while True:
            print(f"Scrapeando '{nombre}' página {pagina}...")
            productos = scrape_categoria(category_slug=slug, pagina=pagina)
            if not productos:
                print("Sin productos. Fin.")
                break
            guardar_en_db(productos)
            pagina += 1
            time.sleep(1)
