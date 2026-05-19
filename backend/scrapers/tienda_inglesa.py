import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from playwright.sync_api import sync_playwright
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

STORE_CHAIN_NAME = "Tienda Inglesa"
BASE_URL = "https://www.tiendainglesa.com.uy/supermercado/busqueda?0,0,{termino},0,0,0,,,false,,,,{pagina}"
TI_BASE = "https://www.tiendainglesa.com.uy"

TERMINOS = [
    "aceite",
    "leche",
    "arroz",
    "azucar",
    "harina",
    "fideos",
    "pan",
    "yerba",
    "cafe",
    "te",
    "agua",
    "jugo",
    "gaseosa",
    "cerveza",
    "vino",
    "carne",
    "pollo",
    "pescado",
    "huevo",
    "queso",
    "yogur",
    "manteca",
    "margarina",
    "mayonesa",
    "ketchup",
    "sal",
    "pimienta",
    "detergente",
    "jabon",
    "papel",
]


def extraer_ean(page, product_url):
    try:
        page.goto(product_url, wait_until="domcontentloaded", timeout=10000)
        el = page.query_selector("span#TXTPRODUCTBARCODE")
        if el:
            ean = el.inner_text().strip()
            if ean:
                return ean
    except Exception:
        pass
    return None


def scrape_pagina(page, termino, pagina_num, _retry=0):
    url = BASE_URL.format(termino=termino, pagina=pagina_num)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_selector("div.card-product-container", timeout=10000)
        except Exception:
            return []

        contenedores = page.query_selector_all("div.card-product-container")
        if not contenedores:
            return []

        resultado = []
        for c in contenedores:
            try:
                nombre_el = c.query_selector("span.card-product-name")
                precio_el = c.query_selector("span.ProductPrice")
                if not nombre_el or not precio_el:
                    continue

                nombre = nombre_el.inner_text().strip()
                precio_text = precio_el.inner_text().strip()
                precio = float(
                    precio_text.replace("$", "").replace(".", "").replace(",", ".").strip()
                )

                imagen_el = c.query_selector("img.card-product-img")
                imagen = imagen_el.get_attribute("src") if imagen_el else None

                link_el = c.query_selector("a[href]")
                product_url = None
                if link_el:
                    href = link_el.get_attribute("href")
                    if href:
                        product_url = href if href.startswith("http") else TI_BASE + href

                cashback_el = c.query_selector("span.ProductSpecialPrice")
                cashback = None
                if cashback_el:
                    try:
                        cashback_text = cashback_el.inner_text().strip()
                        cashback = float(
                            cashback_text.replace("$", "")
                            .replace(".", "")
                            .replace(",", ".")
                            .strip()
                        )
                    except Exception:
                        cashback = None

                resultado.append(
                    {
                        "nombre_externo": nombre,
                        "precio": precio,
                        "imagen": imagen,
                        "cashback": cashback,
                        "disponible": True,
                        "product_url": product_url,
                        "ean": None,
                    }
                )
            except Exception:
                continue

        return resultado
    except Exception as e:
        if "Cannot find context" in str(e) and _retry < 2:
            time.sleep(2)
            return scrape_pagina(page, termino, pagina_num, _retry + 1)
        return []


def guardar_en_db(productos):
    with app.app_context():
        cadena = StoreChain.query.filter_by(name=STORE_CHAIN_NAME).first()
        if not cadena:
            print(f"Error: no se encontró '{STORE_CHAIN_NAME}'. Corré el seed primero.")
            return

        store = Store.query.filter_by(storeChainId=cadena.storeChainId).first()
        if not store:
            print(f"Error: no hay tienda para '{STORE_CHAIN_NAME}'.")
            return

        store_id = store.storeId

        for p in productos:
            product = None

            if p.get("ean"):
                product = Product.query.filter_by(ean=p["ean"]).first()

            if not product:
                product = Product.query.filter_by(
                    normalizedName=p["nombre_externo"].lower()
                ).first()

            if not product:
                brand = Brand.query.filter_by(name=STORE_CHAIN_NAME).first()
                if not brand:
                    brand = Brand(name=STORE_CHAIN_NAME, updatedAt=datetime.now())
                    db.session.add(brand)
                    db.session.flush()

                product = Product(
                    brandId=brand.brandId,
                    name=p["nombre_externo"],
                    normalizedName=p["nombre_externo"].lower(),
                    ean=p.get("ean"),
                    unit="un",
                    imageURL=p["imagen"],
                    updatedAt=datetime.now(),
                )
                db.session.add(product)
                db.session.flush()
            elif p.get("ean") and not product.ean:
                product.ean = p["ean"]

            store_product = StoreProduct.query.filter_by(
                storeId=store_id, productId=product.productId
            ).first()
            if not store_product:
                store_product = StoreProduct(
                    storeId=store_id,
                    productId=product.productId,
                    externalName=p["nombre_externo"],
                    isAvailable=p["disponible"],
                    updatedAt=datetime.now(),
                )
                db.session.add(store_product)
                db.session.flush()
            else:
                store_product.isAvailable = p["disponible"]

            snapshot = PriceSnapshot(
                storeProductId=store_product.storeProductId,
                price=p["precio"],
                currency="UYU",
                capturedAt=datetime.now(),
                source="SCRAPER",
            )
            db.session.add(snapshot)

        db.session.commit()
        print(f"Guardados {len(productos)} productos")


def obtener_eans_existentes(nombres):
    with app.app_context():
        resultado = {}
        for nombre in nombres:
            prod = Product.query.filter_by(normalizedName=nombre.lower()).first()
            if prod and prod.ean:
                resultado[nombre.lower()] = prod.ean
        return resultado


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="es-UY",
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = context.new_page()
        try:
            for termino in TERMINOS:
                pagina = 0
                nombres_pagina_anterior = None
                print(f"\n=== Término: {termino} ===")
                while True:
                    print(f"Scrapeando '{termino}' página {pagina}...")
                    productos = scrape_pagina(page, termino, pagina)
                    if not productos:
                        print("Sin productos. Fin.")
                        break

                    nombres_actuales = {prod["nombre_externo"] for prod in productos}
                    if nombres_actuales == nombres_pagina_anterior:
                        print("Mismos productos que página anterior. Fin de paginación.")
                        break
                    nombres_pagina_anterior = nombres_actuales

                    # A: fetch EANs already in DB to skip page visits
                    eans_db = obtener_eans_existentes(
                        [p["nombre_externo"] for p in productos]
                    )
                    for prod in productos:
                        cached = eans_db.get(prod["nombre_externo"].lower())
                        if cached:
                            prod["ean"] = cached

                    total = len(productos)
                    for i, prod in enumerate(productos, 1):
                        if prod.get("ean"):
                            print(f"  EAN {i}/{total}: {prod['nombre_externo'][:45]} (DB)")
                        else:
                            print(f"  EAN {i}/{total}: {prod['nombre_externo'][:50]}")
                            if prod.get("product_url"):
                                prod["ean"] = extraer_ean(page, prod["product_url"])
                            time.sleep(0.1)  # C: reduced from 0.5

                    guardar_en_db(productos)
                    pagina += 1
                    time.sleep(0.8)  # C: reduced from 2
        finally:
            context.close()
            browser.close()
