from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, Offer, StoreProduct


def parse_decimal(value, field_name):
    if value is None or str(value).strip() == "":
        raise ValueError(f"El campo {field_name} es obligatorio")

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"El campo {field_name} debe ser numérico")


def get_offers(
    store_product_id=None,
    offer_type=None,
    is_active=None,
    page=1,
    per_page=10
):
    query = Offer.query

    if store_product_id:
        query = query.filter(Offer.storeProductId == store_product_id)

    if offer_type:
        query = query.filter(Offer.offerType == offer_type)

    if is_active is not None:
        is_active_value = is_active.lower() == "true"
        query = query.filter(Offer.isActive == is_active_value)

    per_page = min(per_page, 10)

    return query.order_by(Offer.offerId.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


def get_offer_by_id(offer_id):
    return db.session.get(Offer, offer_id)


def create_offer(data):
    required_fields = ["storeProductId", "offerType", "offerPrice"]

    missing_fields = []

    for field in required_fields:
        if data.get(field) is None or str(data.get(field)).strip() == "": 
            missing_fields.append(field)
    
    if missing_fields:
        return None, {
            "message": "Faltan campos obligatorios",
            "fields": missing_fields
        }, 400

    store_product = db.session.get(StoreProduct, data["storeProductId"])

    if store_product is None:
        return None, {
            "message": "Producto de tienda no encontrado"
        }, 404

    offer_type = data["offerType"].strip().upper()

    allowed_offer_types = ["NORMAL", "WEEKLY_DAY"]

    if offer_type not in allowed_offer_types:
        return None, {
            "message": "offerType debe ser NORMAL o WEEKLY_DAY"
        }, 400

    try:
        offer = Offer(
            storeProductId=data["storeProductId"],
            offerType=offer_type,
            offerPrice=parse_decimal(data.get("offerPrice"), "offerPrice"),
            currency=data.get("currency", "CLP"),
            isActive=data.get("isActive", True)
        )

        db.session.add(offer)
        db.session.commit()

        return offer, None, 201

    except ValueError as error:
        db.session.rollback()
        return None, {"message": str(error)}, 400

    except IntegrityError as error:
        db.session.rollback()
        return None, {
            "message": "No se pudo crear la oferta por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al crear oferta",
            "error": str(error)
        }, 500


def update_offer(offer_id, data):
    offer = get_offer_by_id(offer_id)

    if offer is None:
        return None, {
            "message": "Oferta no encontrada"
        }, 404

    try:
        if "storeProductId" in data:
            store_product = db.session.get(StoreProduct, data["storeProductId"])

            if store_product is None:
                return None, {
                    "message": "Producto de tienda no encontrado"
                }, 404

            offer.storeProductId = data["storeProductId"]

        if "offerType" in data:
            offer_type = data["offerType"].strip().upper()

            if offer_type not in ["NORMAL", "WEEKLY_DAY"]:
                return None, {
                    "message": "offerType debe ser NORMAL o WEEKLY_DAY"
                }, 400

            offer.offerType = offer_type

        if "offerPrice" in data:
            offer.offerPrice = parse_decimal(data.get("offerPrice"), "offerPrice")

        if "currency" in data:
            offer.currency = data["currency"]

        if "isActive" in data:
            offer.isActive = data["isActive"]

        db.session.commit()

        return offer, None, 200

    except ValueError as error:
        db.session.rollback()
        return None, {"message": str(error)}, 400

    except IntegrityError as error:
        db.session.rollback()
        return None, {
            "message": "No se pudo actualizar la oferta por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al actualizar oferta",
            "error": str(error)
        }, 500


def deactivate_offer(offer_id):
    offer = get_offer_by_id(offer_id)

    if offer is None:
        return None, {
            "message": "Oferta no encontrada"
        }, 404

    try:
        offer.isActive = False
        db.session.commit()

        return offer, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al desactivar oferta",
            "error": str(error)
        }, 500