from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, StoreProduct, Store, StoreChain, Product


def get_store_products(
    search=None,
    store_id=None,
    product_id=None,
    is_available=None,
    page=1,
    per_page=10
):
    query = StoreProduct.query

    if search:
        search_pattern = f"%{search.strip()}%"

        query = query.join(Product).join(Store).join(StoreChain).filter(
            or_(
                StoreProduct.externalSku.ilike(search_pattern),
                StoreProduct.externalName.ilike(search_pattern),
                StoreProduct.externalBrand.ilike(search_pattern),
                Product.name.ilike(search_pattern),
                Product.normalizedName.ilike(search_pattern),
                Store.address.ilike(search_pattern),
                StoreChain.name.ilike(search_pattern)
            )
        )

    if store_id:
        query = query.filter(StoreProduct.storeId == store_id)

    if product_id:
        query = query.filter(StoreProduct.productId == product_id)

    if is_available is not None:
        is_available_value = is_available.lower() == "true"
        query = query.filter(StoreProduct.isAvailable == is_available_value)

    per_page = min(per_page, 10)

    return query.order_by(StoreProduct.storeProductId.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


def get_store_product_by_id(store_product_id):
    return db.session.get(StoreProduct, store_product_id)


def create_store_product(data):
    required_fields = ["storeId", "productId"]

    missing_fields = []

    for field in required_fields:
        if data.get(field) is None or str(data.get(field)).strip() == "":
            missing_fields.append(field)

    if missing_fields:
        return None, {
            "message": "Faltan campos obligatorios",
            "fields": missing_fields
        }, 400

    store = db.session.get(Store, data["storeId"])

    if store is None:
        return None, {
            "message": "La tienda indicada no existe"
        }, 404

    product = db.session.get(Product, data["productId"])

    if product is None:
        return None, {
            "message": "El producto indicado no existe"
        }, 404

    existing_store_product = StoreProduct.query.filter_by(
        storeId=data["storeId"],
        productId=data["productId"]
    ).first()

    if existing_store_product:
        return None, {
            "message": "Este producto ya está asociado a esta tienda"
        }, 409

    try:
        store_product = StoreProduct(
            storeId=data["storeId"],
            productId=data["productId"],
            externalSku=data.get("externalSku"),
            externalName=data.get("externalName"),
            externalBrand=data.get("externalBrand"),
            isAvailable=data.get("isAvailable", True)
        )

        db.session.add(store_product)
        db.session.commit()

        return store_product, None, 201

    except IntegrityError as error:
        db.session.rollback()

        return None, {
            "message": "No se pudo crear el producto de tienda por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al crear producto de tienda",
            "error": str(error)
        }, 500


def update_store_product(store_product_id, data):
    store_product = get_store_product_by_id(store_product_id)

    if store_product is None:
        return None, {
            "message": "Producto de tienda no encontrado"
        }, 404

    try:
        new_store_id = data.get("storeId", store_product.storeId)
        new_product_id = data.get("productId", store_product.productId)

        if "storeId" in data:
            store = db.session.get(Store, data["storeId"])

            if store is None:
                return None, {
                    "message": "La tienda indicada no existe"
                }, 404

        if "productId" in data:
            product = db.session.get(Product, data["productId"])

            if product is None:
                return None, {
                    "message": "El producto indicado no existe"
                }, 404

        if new_store_id != store_product.storeId or new_product_id != store_product.productId:
            existing_store_product = StoreProduct.query.filter(
                StoreProduct.storeId == new_store_id,
                StoreProduct.productId == new_product_id,
                StoreProduct.storeProductId != store_product.storeProductId
            ).first()

            if existing_store_product:
                return None, {
                    "message": "Ya existe este producto asociado a esta tienda"
                }, 409

        if "storeId" in data:
            store_product.storeId = data["storeId"]

        if "productId" in data:
            store_product.productId = data["productId"]

        if "externalSku" in data:
            store_product.externalSku = data["externalSku"]

        if "externalName" in data:
            store_product.externalName = data["externalName"]

        if "externalBrand" in data:
            store_product.externalBrand = data["externalBrand"]

        if "isAvailable" in data:
            store_product.isAvailable = data["isAvailable"]

        db.session.commit()

        return store_product, None, 200

    except IntegrityError as error:
        db.session.rollback()

        return None, {
            "message": "No se pudo actualizar el producto de tienda por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al actualizar producto de tienda",
            "error": str(error)
        }, 500


def deactivate_store_product(store_product_id):
    store_product = get_store_product_by_id(store_product_id)

    if store_product is None:
        return None, {
            "message": "Producto de tienda no encontrado"
        }, 404

    try:
        store_product.isAvailable = False
        db.session.commit()

        return store_product, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al desactivar producto de tienda",
            "error": str(error)
        }, 500