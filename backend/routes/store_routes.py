from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from services.store_service import (
    get_stores,
    get_store_by_id,
    create_store,
    update_store,
    deactivate_store
)


store_bp = Blueprint("stores", __name__)


@store_bp.route("/", methods=["GET"])
def list_stores():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("perPage", 10, type=int)

    pagination = get_stores(
        page=page,
        per_page=per_page
    )

    return jsonify({
        "success": True,
        "data": [
            store.to_dict()
            for store in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages
        }
    }), 200


@store_bp.route("/<int:store_id>", methods=["GET"])
def find_store(store_id):
    store = get_store_by_id(store_id)

    if store is None:
        return jsonify({
            "success": False,
            "message": "Tienda no encontrada"
        }), 404

    return jsonify({
        "success": True,
        "data": store.to_dict()
    }), 200


@store_bp.route("/", methods=["POST"])
def create():
    data = request.get_json(silent=True) or {}

    store, error, status_code = create_store(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Tienda creada correctamente",
        "data": store.to_dict()
    }), status_code


@store_bp.route("/<int:store_id>", methods=["PUT"])
def update(store_id):
    data = request.get_json(silent=True) or {}

    store, error, status_code = update_store(store_id, data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Tienda actualizada correctamente",
        "data": store.to_dict()
    }), status_code


@store_bp.route("/<int:store_id>", methods=["DELETE"])
def delete(store_id):
    store, error, status_code = deactivate_store(store_id)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Tienda desactivada correctamente"
    }), status_code