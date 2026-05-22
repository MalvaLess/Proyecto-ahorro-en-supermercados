from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, Offer, StoreProduct


def get_offers(store_product_id=None, offer_type=None):
    query = Offer.query

    if store_product_id is not None:
        query = query.filter(Offer.storeProductId == store_product_id)

    if offer_type is not None:
        query = query.filter(Offer.offerType == offer_type)

    return query.order_by(Offer.offerId.desc()).all()


def create_offer(data):
    required_fields = ["storeProductId", "offerType"]
    missing = [f for f in required_fields if data.get(f) is None]
    if missing:
        return None, {"message": "Faltan campos obligatorios", "fields": missing}, 400

    store_product = db.session.get(StoreProduct, data["storeProductId"])
    if store_product is None:
        return None, {"message": "El store product indicado no existe"}, 404

    try:
        offer = Offer(
            storeProductId=data["storeProductId"],
            offerType=data["offerType"],
            offerPrice=data.get("offerPrice"),
            currency=data.get("currency", "UYU"),
            isActive=data.get("isActive", True),
            updatedAt=datetime.now(),
        )
        db.session.add(offer)
        db.session.commit()
        return offer, None, 201

    except (IntegrityError, SQLAlchemyError) as e:
        db.session.rollback()
        return None, {"message": "Error al crear oferta", "error": str(e)}, 500


def update_offer(store_product_id, data):
    offer = Offer.query.filter_by(storeProductId=store_product_id).first()
    if offer is None:
        return None, {"message": "Oferta no encontrada para ese store product"}, 404

    try:
        if "offerType" in data:
            offer.offerType = data["offerType"]
        if "offerPrice" in data:
            offer.offerPrice = data["offerPrice"]
        if "currency" in data:
            offer.currency = data["currency"]
        if "isActive" in data:
            offer.isActive = data["isActive"]
        offer.updatedAt = datetime.now()
        db.session.commit()
        return offer, None, 200

    except (IntegrityError, SQLAlchemyError) as e:
        db.session.rollback()
        return None, {"message": "Error al actualizar oferta", "error": str(e)}, 500


def delete_offer(store_product_id):
    offer = Offer.query.filter_by(storeProductId=store_product_id).first()
    if offer is None:
        return None, {"message": "Oferta no encontrada para ese store product"}, 404

    try:
        offer.isActive = False
        offer.updatedAt = datetime.now()
        db.session.commit()
        return offer, None, 200

    except (IntegrityError, SQLAlchemyError) as e:
        db.session.rollback()
        return None, {"message": "Error al desactivar oferta", "error": str(e)}, 500
