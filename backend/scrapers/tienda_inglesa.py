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
    Offer,
    Product,
    ProductCategory,
    StoreProduct,
    PriceSnapshot,
    Store,
    StoreChain,
)
from datetime import datetime
from sqlalchemy import literal, func
from utils import normalize_brand, jaccard_similarity, same_size, ean13_valido

STORE_CHAIN_NAME = "Tienda Inglesa"
TI_BASE = "https://www.tiendainglesa.com.uy"


TI_CATEGORIAS = [
    {"url": "https://www.tiendainglesa.com.uy/supermercado/categoria/almacen/78",    "nombre": "Almacén"},
    {"url": "https://www.tiendainglesa.com.uy/supermercado/categoria/bebidas/1001",  "nombre": "Bebidas"},
    {"url": "https://www.tiendainglesa.com.uy/supermercado/categoria/frescos/1894",  "nombre": "Frescos"},
    {"url": "https://www.tiendainglesa.com.uy/supermercado/categoria/limpieza/1895", "nombre": "Limpieza"},
    {"url": "https://www.tiendainglesa.com.uy/supermercado/categoria/congelados/181","nombre": "Congelados"},
]


def _extraer_ean_cascada(page):
    """Cascada de 4 niveles para extraer EAN-13 válido desde página de producto TI."""
    # Nivel 1: JSON-LD gtin13 o gtin
    try:
        for el in page.query_selector_all("script[type='application/ld+json']"):
            data = json.loads(el.inner_text())
            raw = data.get("gtin13") or data.get("gtin")
            if ean13_valido(raw):
                return raw
    except Exception:
        pass

    # Nivel 2: meta tag retailer_item_id
    try:
        el = page.query_selector("meta[property='product:retailer_item_id']")
        if el:
            raw = el.get_attribute("content")
            if ean13_valido(raw):
                return raw
    except Exception:
        pass

    # Nivel 3: tabla de ficha técnica "Código de Barras"
    try:
        for row in page.query_selector_all("tr"):
            text = row.inner_text()
            if "barras" in text.lower() or "ean" in text.lower():
                match = re.search(r'\b(\d{13})\b', text)
                if match and ean13_valido(match.group(1)):
                    return match.group(1)
    except Exception:
        pass

    # Nivel 4: regex en scripts GTM — solo 773xxxxxxxxxx con checksum
    try:
        for sc in page.query_selector_all("script:not([src])"):
            for match in re.finditer(r'\b(773\d{10})\b', sc.inner_text()):
                if ean13_valido(match.group(1)):
                    return match.group(1)
    except Exception:
        pass

    return None


def extraer_datos_producto(page, product_url):
    try:
        page.goto(product_url, wait_until="domcontentloaded", timeout=10000)
        ean = _extraer_ean_cascada(page)
        brand, sku = None, None
        try:
            el = page.query_selector("script[type='application/ld+json']")
            if el:
                data = json.loads(el.inner_text())
                brand = data.get("brand", {}).get("name")
                sku = data.get("offers", {}).get("sku") or data.get("sku")
        except Exception:
            pass
        return {"ean": ean, "brand": brand, "sku": sku}
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

                precio_lista = None
                precio_lista_el = c.query_selector("span.wTxtProductPriceBefore")
                if precio_lista_el:
                    try:
                        precio_lista = float(
                            precio_lista_el.inner_text().strip()
                            .replace("$", "").replace(".", "").replace(",", ".").strip()
                        )
                    except Exception:
                        precio_lista = None

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
                        "precio_lista": precio_lista,
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
                if product:
                    sim = jaccard_similarity(p["nombre_externo"], product.normalizedName)
                    if sim < 0.3:
                        print(f"  [EAN-ZOMBIE] EAN {p['ean']} descartado: '{p['nombre_externo']}' vs '{product.name}'")
                        product = None

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

            # Fallback 4: token overlap (Jaccard ≥ 0.5) dentro de misma marca
            if not product:
                brand_norm = normalize_brand(p.get("brand") or "")
                if brand_norm:
                    candidates = Product.query.join(Brand).filter(
                        Brand.normalizedName == brand_norm
                    ).limit(100).all()
                    best_score, best_candidate = 0.0, None
                    for candidate in candidates:
                        if not same_size(p["nombre_externo"], candidate.normalizedName):
                            continue
                        score = jaccard_similarity(p["nombre_externo"], candidate.normalizedName)
                        if score > best_score:
                            best_score, best_candidate = score, candidate
                    if best_score >= 0.6:
                        product = best_candidate

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

            # Detectar y registrar oferta cuando hay precio de lista mayor al precio actual
            precio_lista = p.get("precio_lista")
            if precio_lista:
                oferta_existente = Offer.query.filter_by(
                    storeProductId=store_product.storeProductId,
                    offerType="DESCUENTO"
                ).first()

                if p["precio"] < precio_lista:
                    if oferta_existente:
                        oferta_existente.offerPrice = precio_lista
                        oferta_existente.isActive = True
                        oferta_existente.updatedAt = datetime.now()
                    else:
                        db.session.add(Offer(
                            storeProductId=store_product.storeProductId,
                            offerType="DESCUENTO",
                            offerPrice=precio_lista,
                            currency="UYU",
                            isActive=True,
                            updatedAt=datetime.now(),
                        ))
                elif oferta_existente and oferta_existente.isActive:
                    oferta_existente.isActive = False
                    oferta_existente.updatedAt = datetime.now()

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
    import argparse
    _nombres_cats = [c["nombre"] for c in TI_CATEGORIAS]
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Scrapea solo 1 categoría, 1 página")
    parser.add_argument("--categoria", choices=_nombres_cats, help="Scrapea solo esta categoría")
    args = parser.parse_args()

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
        if args.test:
            print("[TEST MODE] categoría: Almacén, 1 página")
        elif args.categoria:
            print(f"[CATEGORIA] solo: {args.categoria}")
        try:
            if args.test:
                cats = [c for c in TI_CATEGORIAS if c["nombre"] == "Almacén"]
            elif args.categoria:
                cats = [c for c in TI_CATEGORIAS if c["nombre"] == args.categoria]
            else:
                cats = TI_CATEGORIAS
            for cat in cats:
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
                            print(f"  ✓ {i}/{total}: {prod['nombre_externo'][:45]} (DB)")
                        else:
                            if prod.get("product_url"):
                                datos = extraer_datos_producto(page, prod["product_url"])
                                prod["ean"] = datos["ean"]
                                prod["brand"] = datos["brand"]
                                prod["sku"] = datos["sku"]
                            if prod.get("ean"):
                                print(f"  ✓ {i}/{total}: {prod['nombre_externo'][:50]} → {prod['ean']}")
                            else:
                                print(f"  ✗ {i}/{total}: {prod['nombre_externo'][:55]}")
                            time.sleep(0.05)

                    guardar_en_db(productos, cat["nombre"])
                    pagina += 1
                    if args.test:
                        break
                    time.sleep(0.3)
        finally:
            context.close()
            browser.close()

    with app.app_context():
        sin_ean = (
            db.session.query(Product)
            .join(StoreProduct, StoreProduct.productId == Product.productId)
            .join(Store, Store.storeId == StoreProduct.storeId)
            .join(StoreChain, StoreChain.storeChainId == Store.storeChainId)
            .filter(StoreChain.name == STORE_CHAIN_NAME, Product.ean == None)
            .count()
        )
        print(f"\n=== Resumen final ===")
        print(f"Productos Tienda Inglesa sin EAN en DB: {sin_ean}")
