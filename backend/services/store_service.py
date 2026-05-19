from decimal import Decimal, InvalidOperation

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, Store, StoreChain

def parse_decimal(value, field_name):
    if value is None or str(value).strip() == "":
        raise ValueError(f"El campo {field_name} es obligatorio")

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"El campo {field_name} debe ser numérico")
    

def get_stores(page=1, per_page=10):
    query = Store.query

    per_page = min(per_page, 10)

    return query.order_by(Store.storeId.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def get_store_by_id(store_id):
    return db.session.get(Store, store_id)


def create_store(data):
    required_fields = ["storeChainId", "address", "latitude", "longitude"]

    missing_fields = []

    for field in required_fields:
        if data.get(field) is None or str(data.get(field)).strip() == "":
            missing_fields.append(field)

    if missing_fields:
        return None, {
            "message": "Faltan campos obligatorios",
            "fields": missing_fields
        }, 400

    store_chain = db.session.get(StoreChain, data["storeChainId"])

    if store_chain is None:
        return None, {
            "message": "La cadena indicada no existe"
        }, 404

    try:
        store = Store(
            storeChainId=data["storeChainId"],
            address=data["address"].strip(),
            latitude=parse_decimal(data.get("latitude"), "latitude"),
            longitude=parse_decimal(data.get("longitude"), "longitude"),
            isActive=data.get("isActive", True)
        )

        db.session.add(store)
        db.session.commit()

        return store, None, 201

    except ValueError as error:
        db.session.rollback()
        return None, {"message": str(error)}, 400

    except IntegrityError as error:
        db.session.rollback()
        return None, {
            "message": "No se pudo crear la tienda por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al crear tienda",
            "error": str(error)
        }, 500


def update_store(store_id, data):
    store = get_store_by_id(store_id)

    if store is None:
        return None, {
            "message": "Tienda no encontrada"
        }, 404

    try:
        if "storeChainId" in data:
            store_chain = db.session.get(StoreChain, data["storeChainId"])

            if store_chain is None:
                return None, {
                    "message": "La cadena indicada no existe"
                }, 404

            store.storeChainId = data["storeChainId"]

        if "address" in data:
            if data["address"] is None or str(data["address"]).strip() == "":
                return None, {
                    "message": "La dirección no puede estar vacía"
                }, 400

            store.address = data["address"].strip()

        if "latitude" in data:
            store.latitude = parse_decimal(data.get("latitude"), "latitude")

        if "longitude" in data:
            store.longitude = parse_decimal(data.get("longitude"), "longitude")

        if "isActive" in data:
            store.isActive = data["isActive"]

        db.session.commit()

        return store, None, 200

    except ValueError as error:
        db.session.rollback()
        return None, {"message": str(error)}, 400

    except IntegrityError as error:
        db.session.rollback()
        return None, {
            "message": "No se pudo actualizar la tienda por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al actualizar tienda",
            "error": str(error)
        }, 500


def deactivate_store(store_id):
    store = get_store_by_id(store_id)

    if store is None:
        return None, {
            "message": "Tienda no encontrada"
        }, 404

    try:
        store.isActive = False
        db.session.commit()

        return store, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al desactivar tienda",
            "error": str(error)
        }, 500