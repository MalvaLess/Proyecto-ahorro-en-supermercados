import requests
import time
import random
import sys
import os
import re
import json

from playwright.sync_api import sync_playwright

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

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
from sqlalchemy.exc import OperationalError
from utils import normalize_brand, jaccard_similarity, same_size, ean13_valido
from services.offer_service import upsert_scraper_offer, deactivate_scraper_offer, upsert_oca_offer, deactivate_oca_offer

ENDPOINT = "https://www.tata.com.uy/api/graphql"
STORE_CHAIN_NAME = "Ta-Ta"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

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
                    slug
                    brand { name }
                    image { url }
                    categoriesIds
                    offers {
                        offers {
                            price
                            listPrice
                            availability
                            measurementUnit
                            unitMultiplier
                            teasers {
                                name
                                conditions {
                                    minimumQuantity
                                }
                                effects {
                                    parameters {
                                        name
                                        value
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
"""



def _extraer_ean_tata(page):
    """Cascada de extracción EAN-13 desde página Tata hidratada por JS."""
    # Nivel 1: window.pageData (Gatsby SSR, disponible tras domcontentloaded)
    try:
        raw = page.evaluate(
            "() => { try { return window.pageData.result.serverData.product.ean; } catch(e) { return null; } }"
        )
        if ean13_valido(raw):
            return raw
    except Exception:
        pass

    # Nivel 2: JSON-LD gtin13 / gtin
    try:
        for el in page.query_selector_all("script[type='application/ld+json']"):
            data = json.loads(el.inner_text())
            raw = data.get("gtin13") or data.get("gtin")
            if ean13_valido(raw):
                return raw
    except Exception:
        pass

    # Nivel 3: regex en scripts — EANs uruguayos comienzan con 773
    try:
        for sc in page.query_selector_all("script:not([src])"):
            for match in re.finditer(r'\b(773\d{10})\b', sc.inner_text()):
                if ean13_valido(match.group(1)):
                    return match.group(1)
    except Exception:
        pass

    return None


def _parse_price_text(text):
    try:
        clean = text.strip().replace("\xa0", "").replace("$", "").replace(".", "").replace(",", ".").strip()
        return float(clean)
    except Exception:
        return None


def fetch_datos_playwright(page, slug):
    """Visita página de producto Tata. Retorna (ean, precio, precio_lista, es_por_kg, oca_price)."""
    if not slug:
        return None, None, None, False, None
    try:
        url = f"https://www.tata.com.uy/{slug}/p"
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        try:
            page.wait_for_selector("button[data-testid='buy-button']", timeout=8000)
            page.wait_for_timeout(3000)
        except Exception:
            pass

        ean = _extraer_ean_tata(page)
        precio = None
        precio_lista = None
        es_por_kg = False

        # Scopear todo al header del producto actual — evita precios de carrusel/relacionados
        product_section = page.query_selector("header[data-fs-product-details__title='true']")
        # OCA — dentro del producto actual
        oca_price = None
        if product_section:
            oca_container = product_section.query_selector("[data-oca-price='true']")
            if oca_container:
                oca_el = oca_container.query_selector("span.oca-price__value")
                if oca_el:
                    oca_price = _parse_price_text(oca_el.inner_text())

        if not product_section:
            return ean, None, None, False, oca_price

        # Producto por kg — extraer precio del paquete (no el precio/kg)
        kg_container = product_section.query_selector("[data-fs-price-unit-container='true']")
        if kg_container:
            es_por_kg = True
            price_el = product_section.query_selector("span[data-testid='price'][data-variant='spot']")
            if price_el:
                val = price_el.get_attribute("data-value")
                precio = float(val) if val else _parse_price_text(price_el.inner_text())
            return ean, precio, None, True, oca_price

        # Precio tachado (oferta) — precio_lista = precio original sin descuento
        discount_wrapper = product_section.query_selector("[data-fs-product-details__discount-wrapper='true']")
        if discount_wrapper:
            list_el = discount_wrapper.query_selector("span[data-testid='list-price']")
            if list_el:
                val = list_el.get_attribute("data-value")
                precio_lista = float(val) if val else _parse_price_text(list_el.inner_text())

        # Precio de venta actual (dentro del producto actual únicamente)
        price_el = product_section.query_selector("span[data-testid='price'][data-variant='spot']")
        if price_el:
            val = price_el.get_attribute("data-value")
            precio = float(val) if val else _parse_price_text(price_el.inner_text())

        return ean, precio, precio_lista, False, oca_price
    except Exception:
        return None, None, None, False, None


def enriquecer_playwright(page, todos):
    """Visita páginas de productos: extrae precios HTML, EAN."""
    if not todos:
        return
    total = len(todos)
    print(f"  Visitando páginas Playwright para {total} productos...")
    with app.app_context():
        for i, (product_id, store_product_id, slug) in enumerate(todos, 1):
            if not slug:
                continue
            product = db.session.get(Product, product_id)
            if not product:
                continue
            tiene_ean = bool(product.ean)
            time.sleep(random.uniform(1.5, 3.5) if tiene_ean else random.uniform(3.0, 6.0))
            ean, precio, precio_lista, es_por_kg, oca_price = fetch_datos_playwright(page, slug)

            # Persistir flag de venta por peso en StoreProduct
            store_product = db.session.get(StoreProduct, store_product_id)
            if store_product and es_por_kg:
                store_product.soldByWeight = True

            # Guardar precio desde HTML
            snapshot_price = precio_lista if precio_lista else precio
            if snapshot_price:
                snap = PriceSnapshot(
                    storeProductId=store_product_id,
                    price=snapshot_price,
                    currency="UYU",
                    capturedAt=datetime.now(),
                    source="SCRAPER",
                )
                db.session.add(snap)

            tiene_oferta = not es_por_kg and precio_lista and precio and precio < precio_lista
            if tiene_oferta:
                upsert_scraper_offer(store_product_id, precio)
            else:
                deactivate_scraper_offer(store_product_id)

            if oca_price:
                upsert_oca_offer(store_product_id, oca_price)
            else:
                deactivate_oca_offer(store_product_id)

            label_kg = " [x kg]" if es_por_kg else ""
            if tiene_oferta:
                label_precio = f" ${precio_lista} → oferta ${precio}"
            elif precio:
                label_precio = f" ${precio}"
            else:
                label_precio = " sin precio"
            label_oca = f" [OCA ${oca_price}]" if oca_price else ""
            print(f"  {'✓' if tiene_ean else '✗'} {i}/{total}: {product.name[:45]}{label_kg}{label_precio}{label_oca}")

            # EAN enrichment — solo si no tiene EAN
            if ean and not product.ean:
                existente = Product.query.filter_by(ean=ean).first()
                if existente and existente.productId != product_id:
                    print(f"  [EAN-MERGE] '{product.name}' → '{existente.name}' (EAN {ean})")
                    for sp in StoreProduct.query.filter_by(productId=product.productId).all():
                        conflicto = StoreProduct.query.filter_by(
                            storeId=sp.storeId, productId=existente.productId
                        ).first()
                        if conflicto:
                            for snap in PriceSnapshot.query.filter_by(storeProductId=sp.storeProductId).all():
                                snap.storeProductId = conflicto.storeProductId
                            for ofr in Offer.query.filter_by(storeProductId=sp.storeProductId).all():
                                ofr.storeProductId = conflicto.storeProductId
                            db.session.flush()
                            db.session.delete(sp)
                        else:
                            sp.productId = existente.productId
                    for pc in ProductCategory.query.filter_by(productId=product.productId).all():
                        existe_pc = ProductCategory.query.filter_by(
                            productId=existente.productId, categoryId=pc.categoryId
                        ).first()
                        if existe_pc:
                            db.session.delete(pc)
                        else:
                            pc.productId = existente.productId
                    if not existente.imageURL and product.imageURL:
                        existente.imageURL = product.imageURL
                    db.session.flush()
                    db.session.delete(product)
                else:
                    product.ean = ean
                print(f"  [EAN] {product.name[:50]} → {ean}")

        try:
            db.session.commit()
        except OperationalError as e:
            print(f"  [DB] Error en commit de enriquecer_playwright: {e}")
            try:
                db.session.rollback()
            except Exception:
                pass


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

    for intento in range(3):
        try:
            response = requests.post(ENDPOINT, json=payload, headers=HEADERS, timeout=30)
            if response.status_code in (403, 429):
                print(f"  [{response.status_code}] Bot detection (intento {intento+1}/3), esperando {15*(intento+1)}s...")
                if intento < 2:
                    time.sleep(15 * (intento + 1))
                    continue
                print(f"  3 intentos fallidos en página {pagina}, saltando...")
                return []
            break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"  Error red (intento {intento+1}/3): {e}")
            if intento < 2:
                time.sleep(5 * (intento + 1))
            else:
                print(f"  3 intentos fallidos en página {pagina}, saltando...")
                return []
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
                "gtin": p.get("gtin") if ean13_valido(p.get("gtin")) else None,
                "slug": p.get("slug"),
                "imagen": p["image"][0]["url"] if p["image"] else None,
                "disponible": oferta["availability"] == "https://schema.org/InStock",
                "categoriesIds": [int(c) for c in p.get("categoriesIds") or []],
            }
        )

    return resultado


def guardar_en_db(productos):
    for intento in range(2):
        try:
            return _guardar_en_db_impl(productos)
        except OperationalError as e:
            print(f"  [DB] Conexión perdida en guardar_en_db (intento {intento + 1}/2): {e}")
            try:
                db.session.rollback()
            except Exception:
                pass
            if intento < 1:
                print("  [DB] Reintentando en 5s...")
                time.sleep(5)
            else:
                print("  [DB] Error persistente, se omite este batch.")
                return []


def _guardar_en_db_impl(productos):
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
        todos = []

        for p in productos:
            # Buscar producto por GTIN en el catálogo normalizado
            product = Product.query.filter_by(ean=p["gtin"]).first() if p["gtin"] else None
            if product and p["gtin"]:
                sim = jaccard_similarity(p["nombre_externo"], product.normalizedName)
                if sim < 0.3:
                    print(f"  [EAN-ZOMBIE] EAN {p['gtin']} descartado: '{p['nombre_externo']}' vs '{product.name}'")
                    product = None

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

            # Fallback 4: token overlap (Jaccard ≥ 0.5) dentro de misma marca
            if not product:
                brand_norm = normalize_brand(p["marca_externa"])
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
            elif p["imagen"]:
                product.imageURL = p["imagen"]

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

            todos.append((product.productId, store_product.storeProductId, p.get("slug")))

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

        db.session.commit()
        print(f"Guardados {len(productos)} productos en la base de datos")
        return todos


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Scrapea solo 1 categoría, 1 página")
    parser.add_argument("--categoria", choices=list(TATA_CATEGORIAS.keys()), help="Scrapea solo esta categoría")
    args = parser.parse_args()

    categorias = list(TATA_CATEGORIAS.items())
    if args.test:
        categorias = [("almacen", "Almacén")]
        print("[TEST MODE] categoría: Almacén, 1 página")
    elif args.categoria:
        categorias = [(args.categoria, TATA_CATEGORIAS[args.categoria])]
        print(f"[CATEGORIA] solo: {TATA_CATEGORIAS[args.categoria]}")

    STATE_FILE = os.path.join(os.path.dirname(__file__), "state_montevideo.json")

    CONTEXT_KWARGS = {
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "locale": "es-UY",
    }

    def _setup_localidad(browser):
        """Abre tata.com.uy, selecciona Montevideo y guarda el storage state."""
        print("[SETUP] Configurando localidad Montevideo...")
        ctx = browser.new_context(**CONTEXT_KWARGS)
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        pg = ctx.new_page()
        pg.goto("https://www.tata.com.uy/", wait_until="domcontentloaded", timeout=30000)
        try:
            pg.wait_for_selector("select.geoLocator-select", timeout=15000)
            pg.select_option("select.geoLocator-select", "tatauymontevideo")
            print("[SETUP] Localidad seleccionada: Montevideo y Ciudad de la Costa")
            # Esperar que el botón Confirmar se habilite y clickearlo
            pg.wait_for_selector("button.geoLocator-button:not([disabled])", timeout=5000)
            pg.click("button.geoLocator-button")
            print("[SETUP] Confirmado")
            pg.wait_for_timeout(4000)
        except Exception as e:
            print(f"[SETUP] Error configurando localidad: {e}")
        ctx.storage_state(path=STATE_FILE)
        print(f"[SETUP] Estado guardado en {STATE_FILE}")
        ctx.close()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )

        if not os.path.exists(STATE_FILE):
            _setup_localidad(browser)

        context = browser.new_context(
            **CONTEXT_KWARGS,
            storage_state=STATE_FILE,
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = context.new_page()

        try:
            for slug, nombre in categorias:
                pagina = 0
                print(f"\n=== Categoría: {nombre} ===")
                while True:
                    print(f"Scrapeando '{nombre}' página {pagina}...")
                    productos = scrape_categoria(category_slug=slug, pagina=pagina)
                    if not productos:
                        print("Sin productos. Fin.")
                        break
                    todos = guardar_en_db(productos)
                    enriquecer_playwright(page, todos)
                    pagina += 1
                    if args.test:
                        break
                    time.sleep(random.uniform(8.0, 15.0))
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
        print(f"Productos Ta-Ta sin EAN en DB: {sin_ean}")
