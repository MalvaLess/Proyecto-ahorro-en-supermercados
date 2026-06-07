import math
from sqlalchemy import func, and_
from models.models import db, Product, Store, StoreProduct, PriceSnapshot, Offer


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
    return Offer.query.filter(
        Offer.storeProductId == store_product_id,
        Offer.isActive == True,
        Offer.offerType.in_(["NORMAL", "WEEKLY_DAY"])
    ).order_by(
        Offer.offerId.desc()
    ).first()

def get_active_oca_offer(store_product_id):
    return Offer.query.filter_by(
        storeProductId=store_product_id,
        offerType="OCA",
        isActive=True
    ).order_by(
        Offer.offerId.desc()
    ).first()

def build_price_comparison_item(store_product):
    latest_price = get_latest_price(store_product.storeProductId)
    active_offer = get_active_offer(store_product.storeProductId)
    oca_offer = get_active_oca_offer(store_product.storeProductId)

    normal_price = latest_price.price if latest_price else None
    offer_price = active_offer.offerPrice if active_offer else None
    oca_price = oca_offer.offerPrice if oca_offer else None

    final_price = offer_price if offer_price is not None else normal_price

    return {
        "storeProductId": store_product.storeProductId,
        "storeId": store_product.storeId,
        "storeChainId": store_product.store.chain.storeChainId if store_product.store and store_product.store.chain else None,
        "storeChainName": store_product.store.chain.name if store_product.store and store_product.store.chain else None,
        "storeAddress": store_product.store.address if store_product.store else None,
        "externalSku": store_product.externalSku,
        "externalName": store_product.externalName,
        "externalBrand": store_product.externalBrand,
        "price": float(normal_price) if normal_price is not None else None,
        "hasOffer": active_offer is not None,
        "offer": {
            "offerId": active_offer.offerId,
            "offerType": active_offer.offerType,
            "offerPrice": float(active_offer.offerPrice) if active_offer.offerPrice is not None else None,
            "currency": active_offer.currency,
            "isActive": active_offer.isActive
        } if active_offer else None,
        "ocaPrice": float(oca_price) if oca_price is not None else None,
        "finalPrice": float(final_price) if final_price is not None else None,
        "currency": (
            active_offer.currency
            if active_offer
            else latest_price.currency if latest_price else None
        ),
        "capturedAt": latest_price.capturedAt.isoformat() if latest_price and latest_price.capturedAt else None
    }

def compare_product_prices(product_id, chain_ids=None):
    product = db.session.get(Product, product_id)

    if product is None:
        return None, {
            "message": "Producto no encontrado"
        }, 404

    query = StoreProduct.query.join(
        Store,
        StoreProduct.storeId == Store.storeId
    ).filter(
        StoreProduct.productId == product_id,
        StoreProduct.isAvailable == True
    )

    if chain_ids:
        query = query.filter(
            Store.storeChainId.in_(chain_ids)
        )

    store_products = query.all()

    best_item_by_chain = {}

    for store_product in store_products:
        item = build_price_comparison_item(store_product)

        store_chain_id = item["storeChainId"]

        if store_chain_id is None:
            continue

        current_best_item = best_item_by_chain.get(store_chain_id)

        if current_best_item is None:
            best_item_by_chain[store_chain_id] = item
            continue

        current_price = current_best_item["finalPrice"]
        new_price = item["finalPrice"]

        if current_price is None and new_price is not None:
            best_item_by_chain[store_chain_id] = item
            continue

        if current_price is not None and new_price is not None and new_price < current_price:
            best_item_by_chain[store_chain_id] = item

    items = list(best_item_by_chain.values())

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


def get_top_discounts(limit=10):
    # Subquery: latest priceSnapshotId por storeProductId (ID autoincremental es más confiable que capturedAt)
    latest_price_subq = (
        db.session.query(
            PriceSnapshot.storeProductId,
            func.max(PriceSnapshot.priceSnapshotId).label("max_id")
        )
        .group_by(PriceSnapshot.storeProductId)
        .subquery()
    )

    rows = (
        db.session.query(Offer, StoreProduct, Product, PriceSnapshot)
        .join(StoreProduct, Offer.storeProductId == StoreProduct.storeProductId)
        .join(Product, StoreProduct.productId == Product.productId)
        .outerjoin(latest_price_subq, latest_price_subq.c.storeProductId == StoreProduct.storeProductId)
        .outerjoin(PriceSnapshot, PriceSnapshot.priceSnapshotId == latest_price_subq.c.max_id)
        .filter(
            Offer.isActive == True,
            Offer.offerPrice.isnot(None),
            Offer.offerPrice > 0,
            Product.isActive == True,
            StoreProduct.soldByWeight == False
        )
        .all()
    )

    seen = {}
    for offer, store_product, product, price_snapshot in rows:
        offer_price = float(offer.offerPrice)
        pid = product.productId

        if price_snapshot and float(price_snapshot.price) > offer_price:
            normal_price = float(price_snapshot.price)
            discount_pct = round((normal_price - offer_price) / normal_price * 100, 1)
            currency = price_snapshot.currency
        else:
            # Sin precio normal comparable — descuento desconocido, prioridad mínima
            normal_price = None
            discount_pct = 0.0
            currency = "UYU"

        if pid not in seen or discount_pct > seen[pid]["discountPct"]:
            seen[pid] = {
                "productId": product.productId,
                "name": product.name,
                "imageURL": product.imageURL,
                "brand": product.brand.name if product.brand else None,
                "normalPrice": round(normal_price, 2) if normal_price else None,
                "offerPrice": round(offer_price, 2),
                "discountPct": discount_pct,
                "currency": currency
            }

    sorted_results = sorted(seen.values(), key=lambda x: x["discountPct"], reverse=True)

    return sorted_results[:limit]


def get_offers_paginated(page=1, per_page=40):
    from sqlalchemy.orm import joinedload

    product_ids_subq = (
        db.session.query(Product.productId)
        .join(StoreProduct, StoreProduct.productId == Product.productId)
        .join(Offer, Offer.storeProductId == StoreProduct.storeProductId)
        .filter(
            Offer.isActive == True,
            Offer.offerPrice.isnot(None),
            Offer.offerPrice > 0,
            Offer.offerType.in_(["NORMAL", "WEEKLY_DAY"]),
            Product.isActive == True,
            StoreProduct.soldByWeight == False
        )
        .distinct()
        .subquery()
    )

    total = db.session.query(func.count(product_ids_subq.c.productId)).scalar()

    paginated_ids = (
        db.session.query(product_ids_subq.c.productId)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    ids = [row[0] for row in paginated_ids]
    if not ids:
        return {"data": [], "pagination": {"page": page, "perPage": per_page, "totalItems": total, "totalPages": 0}}

    # Bulk load products
    products = {
        p.productId: p
        for p in Product.query.options(joinedload(Product.brand)).filter(Product.productId.in_(ids)).all()
    }

    # Bulk load store products with store+chain in one query
    store_products = (
        StoreProduct.query
        .options(joinedload(StoreProduct.store).joinedload(Store.chain))
        .filter(StoreProduct.productId.in_(ids), StoreProduct.isAvailable == True)
        .all()
    )

    sp_ids = [sp.storeProductId for sp in store_products]

    # Bulk load latest price snapshot per storeProductId
    latest_subq = (
        db.session.query(
            PriceSnapshot.storeProductId,
            func.max(PriceSnapshot.priceSnapshotId).label("max_id")
        )
        .filter(PriceSnapshot.storeProductId.in_(sp_ids))
        .group_by(PriceSnapshot.storeProductId)
        .subquery()
    )
    latest_prices = {
        ps.storeProductId: ps
        for ps in db.session.query(PriceSnapshot)
        .join(latest_subq, PriceSnapshot.priceSnapshotId == latest_subq.c.max_id)
        .all()
    }

    # Bulk load active offers (keep highest offerId per storeProductId)
    active_offers = {}
    for offer in (
        Offer.query
        .filter(Offer.storeProductId.in_(sp_ids), Offer.isActive == True, Offer.offerType.in_(["NORMAL", "WEEKLY_DAY"]))
        .order_by(Offer.offerId.desc())
        .all()
    ):
        active_offers.setdefault(offer.storeProductId, offer)

    oca_offers = {}
    for offer in (
        Offer.query
        .filter(Offer.storeProductId.in_(sp_ids), Offer.isActive == True, Offer.offerType == "OCA")
        .order_by(Offer.offerId.desc())
        .all()
    ):
        oca_offers.setdefault(offer.storeProductId, offer)

    # Group store products by productId
    by_product = {}
    for sp in store_products:
        by_product.setdefault(sp.productId, []).append(sp)

    data = []
    for pid in ids:
        product = products.get(pid)
        if not product:
            continue

        items = []
        for sp in by_product.get(pid, []):
            latest_price = latest_prices.get(sp.storeProductId)
            active_offer = active_offers.get(sp.storeProductId)
            oca_offer = oca_offers.get(sp.storeProductId)

            normal_price = latest_price.price if latest_price else None
            offer_price = active_offer.offerPrice if active_offer else None
            oca_price = oca_offer.offerPrice if oca_offer else None
            final_price = offer_price if offer_price is not None else normal_price

            chain = sp.store.chain if sp.store else None
            items.append({
                "storeProductId": sp.storeProductId,
                "storeChainId": chain.storeChainId if chain else None,
                "storeChainName": chain.name if chain else None,
                "price": float(normal_price) if normal_price is not None else None,
                "finalPrice": float(final_price) if final_price is not None else None,
                "hasOffer": active_offer is not None,
                "offer": {
                    "offerPrice": float(active_offer.offerPrice) if active_offer and active_offer.offerPrice else None,
                    "currency": active_offer.currency,
                } if active_offer else None,
                "ocaPrice": float(oca_price) if oca_price is not None else None,
                "currency": (
                    active_offer.currency if active_offer
                    else latest_price.currency if latest_price else None
                ),
            })

        best_by_chain = {}
        for item in items:
            chain_id = item["storeChainId"]
            if chain_id is None:
                continue
            current = best_by_chain.get(chain_id)
            if current is None:
                best_by_chain[chain_id] = item
            elif (
                (current["finalPrice"] is None and item["finalPrice"] is not None) or
                (current["finalPrice"] is not None and item["finalPrice"] is not None
                 and item["finalPrice"] < current["finalPrice"])
            ):
                best_by_chain[chain_id] = item

        sorted_items = sorted(
            best_by_chain.values(),
            key=lambda x: (x["finalPrice"] is None, x["finalPrice"] or 0)
        )

        data.append({
            "productId": product.productId,
            "name": product.name,
            "imageURL": product.imageURL,
            "brand": product.brand.name if product.brand else None,
            "items": sorted_items,
        })

    total_pages = math.ceil(total / per_page) if per_page > 0 else 1

    return {
        "data": data,
        "pagination": {
            "page": page,
            "perPage": per_page,
            "totalItems": total,
            "totalPages": total_pages,
        }
    }