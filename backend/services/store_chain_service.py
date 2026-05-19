from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, StoreChain

def get_store_chains(page=1, per_page=10):
    query = StoreChain.query

    per_page = min(per_page, 10)

    return query.order_by(StoreChain.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def get_store_chain_by_id(store_chain_id):
    return db.session.get(StoreChain, store_chain_id)


def create_store_chain(data):
    name = data.get("name")

    if name is None or str(name).strip() == "":
        return None, {
            "message": "El nombre de la cadena es obligatorio"
        }, 400

    clean_name = name.strip()

    existing_store_chain = StoreChain.query.filter(
        func.lower(StoreChain.name) == clean_name.lower()
    ).first()

    if existing_store_chain:
        return None, {
            "message": "Ya existe una cadena con ese nombre"
        }, 409

    store_chain = StoreChain(
        name=clean_name,
        isActive=data.get("isActive", True)
    )

    try:
        db.session.add(store_chain)
        db.session.commit()

        return store_chain, None, 201

    except IntegrityError as error:
        db.session.rollback()

        return None, {
            "message": "No se pudo crear la cadena por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al crear cadena",
            "error": str(error)
        }, 500


def update_store_chain(store_chain_id, data):
    store_chain = get_store_chain_by_id(store_chain_id)

    if store_chain is None:
        return None, {
            "message": "Cadena no encontrada"
        }, 404

    if "name" in data:
        name = data.get("name")

        if name is None or str(name).strip() == "":
            return None, {
                "message": "El nombre de la cadena no puede estar vacío"
            }, 400

        clean_name = name.strip()

        existing_store_chain = StoreChain.query.filter(
            func.lower(StoreChain.name) == clean_name.lower(),
            StoreChain.storeChainId != store_chain.storeChainId
        ).first()

        if existing_store_chain:
            return None, {
                "message": "Ya existe otra cadena con ese nombre"
            }, 409

        store_chain.name = clean_name

    if "isActive" in data:
        store_chain.isActive = data["isActive"]

    try:
        db.session.commit()

        return store_chain, None, 200

    except IntegrityError as error:
        db.session.rollback()

        return None, {
            "message": "No se pudo actualizar la cadena por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al actualizar cadena",
            "error": str(error)
        }, 500


def deactivate_store_chain(store_chain_id):
    store_chain = get_store_chain_by_id(store_chain_id)

    if store_chain is None:
        return None, {
            "message": "Cadena no encontrada"
        }, 404

    try:
        store_chain.isActive = False
        db.session.commit()

        return store_chain, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al desactivar cadena",
            "error": str(error)
        }, 500