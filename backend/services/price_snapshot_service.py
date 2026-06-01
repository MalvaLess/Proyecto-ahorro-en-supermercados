from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, PriceSnapshot, StoreProduct


def parse_decimal(value, field_name):
    if value is None or str(value).strip() == "":  # strip() con paréntesis: llama al método, no compara el objeto
        raise ValueError(f"El campo {field_name} es obligatorio")
    
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"El campo {field_name} debe ser númerico")

def get_price_snapshots(
        store_product_id=None,
        page=1,
        per_page=10
): 
    query = PriceSnapshot.query

    if store_product_id:
        query = query.filter(PriceSnapshot.storeProductId == store_product_id)

    per_page = min(per_page, 10)

    return query.order_by(PriceSnapshot.capturedAt.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def get_price_snapshot_by_id(price_snapshot_id):
    return db.session.get(PriceSnapshot, price_snapshot_id)


def get_latest_price_by_store_product(store_product_id):
    store_product = db.session.get(StoreProduct, store_product_id)

    if store_product is None:
        return None, {
            "message": "Producto de tienda no encontrado"
        }, 404
    
    price_snapshot = PriceSnapshot.query.filter_by(
        storeProductId = store_product_id
    ).order_by(
        PriceSnapshot.capturedAt.desc()
    ).first()

    if price_snapshot is None:
        return None, {
            "message": "No existen precios registrados para este producto de tienda"
        }, 404
    
    return price_snapshot, None, 200

def create_price_snapshot(data):
    required_fields = ["storeProductId", "price"]

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
            "message": "El producto de tienda indicado no existe"
        }, 404
    
    try:
        price_snapshot = PriceSnapshot(
            storeProductId = data["storeProductId"],
            price = parse_decimal(data.get("price"), "price")
        )
    
        db.session.add(price_snapshot)
        db.session.commit()

        return price_snapshot, None, 201
    
    except ValueError as error:
        db.session.rollback()
        return None, {
            "message": str(error)
        }, 400
    
    except IntegrityError as error:
        db.session.rollback()
        return None, {
            "message": "No se pudo crear el registro de precio por una restricción de integridad"
        }, 409
    
    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al crear registro de precio",
            "error": str(error)
        }, 500


def delete_price_snapshot(price_snapshot_id):
    price_snapshot = get_price_snapshot_by_id(price_snapshot_id)

    if price_snapshot is None:
        return None, {
            "message": "Registro de precio no encontrado"
        }, 404

    try:
        db.session.delete(price_snapshot)
        db.session.commit()

        return price_snapshot, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al eliminar registro de precio",
            "error": str(error)
        }, 500