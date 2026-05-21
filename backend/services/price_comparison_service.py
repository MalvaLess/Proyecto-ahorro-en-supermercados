from models.models import db, Product, StoreProduct, PriceSnapshot, Offer


def parse_store_ids(store_ids_raw):
    if store_ids_raw is None or store_ids_raw.strip() == "":
        return None, None

    try:
        store_ids = []

        stores_raw_list = store_ids_raw.split(",")

        for store_id in stores_raw_list:
            clean_store_id = store_id.strip()

            if clean_store_id != "":
                store_ids.append(int(clean_store_id))

        return store_ids, None

    except ValueError:
        return None, {
            "message": "storeIds debe ser una lista de números separados por coma. Ejemplo: storeIds=1,2,3"
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

def compare_product_prices(product_id, store_ids=None):
    product = db.session.get(Product, product_id)

    if product is None:
        return None, {
            "message": "Producto no encontrado"
        }, 404

    query = StoreProduct.query.filter(
        StoreProduct.productId == product_id,
        StoreProduct.isAvailable == True
    )

    if store_ids:
        query = query.filter(StoreProduct.storeId.in_(store_ids))

    store_products = query.all()

    items = []

    for store_product in store_products:
        latest_price = get_latest_price(store_product.storeProductId)
        active_offer = get_active_offer(store_product.storeProductId)

        normal_price = latest_price.price if latest_price else None
        offer_price = active_offer.offerPrice if active_offer else None

        final_price = offer_price if offer_price is not None else normal_price

        items.append({
            "storeProductId": store_product.storeProductId,
            "storeId": store_product.storeId,
            "storeName": store_product.store.chain.name if store_product.store and store_product.store.chain else None,
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