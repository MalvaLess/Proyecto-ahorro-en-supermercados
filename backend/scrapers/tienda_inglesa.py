import sys
import os
import time
import json
import re

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from playwright.sync_api import sync_playwright
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

STORE_CHAIN_NAME = "Tienda Inglesa"
TI_BASE = "https://www.tiendainglesa.com.uy"

TI_CATEGORIAS = [
    {"url": "https://www.tiendainglesa.com.uy/supermercado/categoria/almacen/78",    "nombre": "Almacén"},
    {"url": "https://www.tiendainglesa.com.uy/supermercado/categoria/bebidas/1001",  "nombre": "Bebidas"},
    {"url": "https://www.tiendainglesa.com.uy/supermercado/categoria/frescos/1894",  "nombre": "Frescos"},
    {"url": "https://www.tiendainglesa.com.uy/supermercado/categoria/limpieza/1895", "nombre": "Limpieza"},
    {"url": "https://www.tiendainglesa.com.uy/supermercado/categoria/congelados/181","nombre": "Congelados"},
]


def extraer_datos_producto(page, product_url):
    try:
        page.goto(product_url, wait_until="domcontentloaded", timeout=10000)
        el = page.query_selector("script[type='application/ld+json']")
        if el:
            data = json.loads(el.inner_text())
            return {
                "ean": data.get("gtin13"),
                "brand": data.get("brand", {}).get("name"),
                "sku": data.get("offers", {}).get("sku") or data.get("sku"),
            }
    except Exception:
        pass
    return {"ean": None, "brand": None, "sku": None}


def scrape_pagina(page, categoria_url, pagina_num, _retry=0):
    if pagina_num == 0:
        url = categoria_url
    else:
        cat_id = categoria_url.rstrip("/").split("/")[-1]
        parent_url = categoria_url.rstrip("/").rsplit("/", 1)[0]
        url = f"{parent_url}/busqueda?0,0,*%3A*,{cat_id},0,0,,,false,,,,{pagina_num}"
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
                        "brand": None,
                        "sku": None,
                    }
                )
            except Exception:
                continue

        return resultado
    except Exception as e:
        if "Cannot find context" in str(e) and _retry < 2:
            time.sleep(2)
            return scrape_pagina(page, categoria_url, pagina_num, _retry + 1)
        return []


def guardar_en_db(productos, categoria_nombre=None):
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

            # Fallback: nombre scraper empieza con normalizedName CKAN + misma marca
            # Valida que lo que sigue al prefijo sea la marca o un número (no otro calificador de producto)
            if not product:
                brand_norm = normalize_brand(p.get("brand") or "")
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

            # Si encontró producto CKAN sin EAN, enriquecerlo con el EAN scrapeado
            if product and p.get("ean") and not product.ean:
                product.ean = p["ean"]

            if not product:
                brand_name = p.get("brand") or STORE_CHAIN_NAME
                brand = Brand.query.filter_by(normalizedName=normalize_brand(brand_name)).first()
                if not brand:
                    brand = Brand(name=brand_name, normalizedName=normalize_brand(brand_name), updatedAt=datetime.now())
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
                    externalSku=p.get("sku"),
                    externalName=p["nombre_externo"],
                    externalBrand=p.get("brand"),
                    isAvailable=p["disponible"],
                    updatedAt=datetime.now(),
                )
                db.session.add(store_product)
                db.session.flush()
            else:
                store_product.isAvailable = p["disponible"]
                if p.get("sku") and not store_product.externalSku:
                    store_product.externalSku = p.get("sku")
                if p.get("brand") and not store_product.externalBrand:
                    store_product.externalBrand = p.get("brand")

            # Asignar categoría si se conoce
            if categoria_nombre:
                categoria = Category.query.filter_by(name=categoria_nombre).first()
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
            for cat in TI_CATEGORIAS:
                pagina = 0
                nombres_pagina_anterior = None
                print(f"\n=== Categoría: {cat['nombre']} ===")
                while True:
                    print(f"Scrapeando '{cat['nombre']}' página {pagina}...")
                    productos = scrape_pagina(page, cat["url"], pagina)
                    if not productos:
                        print("Sin productos. Fin.")
                        break

                    nombres_actuales = {prod["nombre_externo"] for prod in productos}
                    if nombres_actuales == nombres_pagina_anterior:
                        print("Mismos productos que página anterior. Fin de paginación.")
                        break
                    nombres_pagina_anterior = nombres_actuales

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
                                datos = extraer_datos_producto(page, prod["product_url"])
                                prod["ean"] = datos["ean"]
                                prod["brand"] = datos["brand"]
                                prod["sku"] = datos["sku"]
                            time.sleep(0.1)

                    guardar_en_db(productos, cat["nombre"])
                    pagina += 1
                    time.sleep(0.8)
        finally:
            context.close()
            browser.close()
