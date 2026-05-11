import requests
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from app.app import app
from models.models import (
    db,
    Brand,
    Product,
    StoreProduct,
    PriceSnapshot,
    Store,
    StoreChain,
)
from datetime import datetime

ENDPOINT = "https://www.tata.com.uy/api/graphql"
STORE_CHAIN_NAME = "Ta-Ta"

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


def scrape_categoria(termino="", pagina=0, cantidad=50):
    payload = {
        "operationName": "ProductsQuery",
        "variables": {
            "first": cantidad,
            "after": str(pagina * cantidad),
            "sort": "score_desc",
            "term": termino,
            "selectedFacets": [
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

            if not product:
                # No está en catálogo CKAN, crear producto nuevo con nombre de Ta-Ta
                brand = Brand.query.filter_by(name=p["marca_externa"]).first()
                if not brand:
                    brand = Brand(name=p["marca_externa"], updatedAt=datetime.now())
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
    productos = scrape_categoria(termino="leche")
    guardar_en_db(productos)
