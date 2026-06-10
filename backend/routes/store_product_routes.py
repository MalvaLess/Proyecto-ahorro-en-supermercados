from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from services.store_product_service import (
    get_store_products,
    get_store_product_by_id,
    create_store_product,
    update_store_product,
    deactivate_store_product
)


store_product_bp = Blueprint("store_products", __name__)


@store_product_bp.route("/", methods=["GET"])
def list_store_products():
    search = request.args.get("q", type=str)
    store_id = request.args.get("storeId", type=int)
    product_id = request.args.get("productId", type=int)
    is_available = request.args.get("isAvailable")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("perPage", 10, type=int)

    pagination = get_store_products(
        search=search,
        store_id=store_id,
        product_id=product_id,
        is_available=is_available,
        page=page,
        per_page=per_page
    )

    return jsonify({
        "success": True,
        "data": [
            store_product.to_dict()
            for store_product in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages
        }
    }), 200


@store_product_bp.route("/<int:store_product_id>", methods=["GET"])
def find_store_product(store_product_id):
    store_product = get_store_product_by_id(store_product_id)

    if store_product is None:
        return jsonify({
            "success": False,
            "message": "Producto de tienda no encontrado"
        }), 404

    return jsonify({
        "success": True,
        "data": store_product.to_dict()
    }), 200


@store_product_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    data = request.get_json(silent=True) or {}

    store_product, error, status_code = create_store_product(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Producto asociado correctamente a la tienda",
        "data": store_product.to_dict()
    }), status_code


@store_product_bp.route("/<int:store_product_id>", methods=["PUT"])
@jwt_required()
def update(store_product_id):
    data = request.get_json(silent=True) or {}

    store_product, error, status_code = update_store_product(
        store_product_id,
        data
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Producto de tienda actualizado correctamente",
        "data": store_product.to_dict()
    }), status_code


@store_product_bp.route("/<int:store_product_id>", methods=["DELETE"])
@jwt_required()
def delete(store_product_id):
    store_product, error, status_code = deactivate_store_product(
        store_product_id
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Producto de tienda desactivado correctamente"
    }), status_code