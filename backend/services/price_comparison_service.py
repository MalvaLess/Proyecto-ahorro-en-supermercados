from models.models import db, Product, StoreProduct, PriceSnapshot, Offer


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

def get_active_offer(store_product_id):
    return Offer.query.filter_by(
        storeProductId=store_product_id,
        isActive=True
    ).order_by(
        Offer.offerId.desc()
    ).first()

def compare_product_prices(product_id, chain_ids=None):
    product = db.session.get(Product, product_id)

    if product is None:
        return None, {
            "message": "Producto no encontrado"
        }, 404

    query = StoreProduct.query.filter(
        StoreProduct.productId == product_id,
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
        active_offer = get_active_offer(store_product.storeProductId)

        normal_price = latest_price.price if latest_price else None
        offer_price = active_offer.offerPrice if active_offer else None

        final_price = offer_price if offer_price is not None else normal_price

        items.append({
            "storeProductId": store_product.storeProductId,
            "storeId": store_product.storeId,
            "storeName": chain_name,
            "storeAddress": store_product.store.address if store_product.store else None,
            "externalSku": store_product.externalSku,
            "externalName": store_product.externalName,
            "externalBrand": store_product.externalBrand,
            "price": float(latest_price.price) if latest_price else None,
            "hasOffer": active_offer is not None,
            "offer": {
                "offerId": active_offer.offerId,
                "offerType": active_offer.offerType,
                "offerPrice": float(active_offer.offerPrice) if active_offer.offerPrice is not None else None,
                "currency": active_offer.currency,
                "isActive": active_offer.isActive
            } if active_offer else None,
            "finalPrice": float(final_price) if final_price is not None else None,
            "currency": latest_price.currency if latest_price else None,
            "capturedAt": latest_price.capturedAt.isoformat() if latest_price and latest_price.capturedAt else None
        })

    items.sort(
        key=lambda item: (
            item["finalPrice"] is None,
            item["finalPrice"] if item["finalPrice"] is not None else 0
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