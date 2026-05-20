from models.models import db, Product, StoreProduct, PriceSnapshot, Store


def parse_chain_ids(chain_ids_raw):
    if chain_ids_raw is None or chain_ids_raw.strip() == "":
        return None, None

    try:
        chain_ids = []

        for part in chain_ids_raw.split(","):
            clean = part.strip()
            if clean:
                chain_ids.append(int(clean))

        return chain_ids, None

    except ValueError:
        return None, {
            "message": "storeChainIds debe ser una lista de números separados por coma. Ejemplo: storeChainIds=1,2,3"
        }


def get_latest_price(store_product_id):
    return PriceSnapshot.query.filter_by(
        storeProductId=store_product_id
    ).order_by(
        PriceSnapshot.capturedAt.desc(),
        PriceSnapshot.priceSnapshotId.desc()
    ).first()


def compare_product_prices(product_id, chain_ids=None):
    product = db.session.get(Product, product_id)

    if product is None:
        return None, {
            "message": "Producto no encontrado"
        }, 404

    # Incluir variantes scraped del mismo producto base (ej: "aceite de girasol optimo 900ml")
    related_ids = [product_id]
    if product.normalizedName:
        variantes = Product.query.filter(
            Product.normalizedName.ilike(f"{product.normalizedName} %"),
            Product.productId != product_id
        ).all()
        related_ids += [p.productId for p in variantes]

    query = StoreProduct.query.filter(
        StoreProduct.productId.in_(related_ids),
        StoreProduct.isAvailable == True
    )

    if chain_ids:
        store_ids_for_chains = [
            s.storeId for s in Store.query.filter(Store.storeChainId.in_(chain_ids)).all()
        ]
        query = query.filter(StoreProduct.storeId.in_(store_ids_for_chains))

    store_products = query.all()

    # Agrupar por cadena: preferir precio SCRAPER, sino mínimo CKAN
    cadenas = {}

    for store_product in store_products:
        latest_price = get_latest_price(store_product.storeProductId)
        if not latest_price:
            continue

        chain = store_product.store.chain if store_product.store else None
        chain_id = chain.storeChainId if chain else None
        chain_name = chain.name if chain else None
        price_val = float(latest_price.price)
        source = latest_price.source

        candidate = {
            "storeProductId": store_product.storeProductId,
            "storeId": store_product.storeId,
            "storeName": chain_name,
            "storeAddress": store_product.store.address if store_product.store else None,
            "externalSku": store_product.externalSku,
            "externalName": store_product.externalName,
            "externalBrand": store_product.externalBrand,
            "price": price_val,
            "currency": latest_price.currency,
            "capturedAt": latest_price.capturedAt.isoformat() if latest_price.capturedAt else None,
            "source": source,
        }

        existing = cadenas.get(chain_id)
        if not existing:
            cadenas[chain_id] = candidate
        else:
            # SCRAPER gana sobre CKAN; entre mismo source, precio más bajo
            existing_scraper = existing["source"] == "SCRAPER"
            new_scraper = source == "SCRAPER"
            if new_scraper and not existing_scraper:
                cadenas[chain_id] = candidate
            elif not new_scraper and existing_scraper:
                pass
            elif price_val < existing["price"]:
                cadenas[chain_id] = candidate

    items = list(cadenas.values())

    items.sort(
        key=lambda item: (
            item["price"] is None,
            item["price"] if item["price"] is not None else 0
        )
    )

    result = {
        "product": {
            "productId": product.productId,
            "name": product.name,
            "normalizedName": product.normalizedName,
            "brand": {
                "brandId": product.brand.brandId,
                "name": product.brand.name
            } if product.brand else None
        },
        "items": items
    }

    return result, None, 200