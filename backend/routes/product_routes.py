from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from urllib.parse import urlencode

from services.product_service import (
    get_products,
    get_product_by_id,
    create_product,
    update_product,
    deactivate_product
)

def build_pagination_links(pagination):
    query_params = request.args.to_dict()

    query_params["perPage"] = pagination.per_page

    current_params = query_params.copy()
    current_params["page"] = pagination.page

    current_page_url = f"{request.base_url}?{urlencode(current_params)}"

    previous_page_url = None

    if pagination.has_prev:
        previous_params = query_params.copy()
        previous_params["page"] = pagination.prev_num
        previous_page_url = f"{request.base_url}?{urlencode(previous_params)}"

    next_page_url = None

    if pagination.has_next:
        next_params = query_params.copy()
        next_params["page"] = pagination.next_num
        next_page_url = f"{request.base_url}?{urlencode(next_params)}"

    return {
        "currentPage": current_page_url,
        "previousPage": previous_page_url,
        "nextPage": next_page_url
    }

product_bp = Blueprint("products", __name__)


@product_bp.route("/products", methods=["GET"])
def list_products():
    search = request.args.get("q", type=str)
    brand_id = request.args.get("brandId", type=int)
    category_id = request.args.get("categoryId", type=int)
    is_active = request.args.get("isActive")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("perPage", 40, type=int)

    pagination = get_products(
        search=search,
        brand_id=brand_id,
        category_id=category_id,
        is_active=is_active,
        page=page,
        per_page=per_page
    )

    pagination_links = build_pagination_links(pagination)

    return jsonify({
        "success": True,
        "data": [product.to_dict() for product in pagination.items],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages,
            "currentPage": pagination_links["currentPage"],
            "previousPage": pagination_links["previousPage"],
            "nextPage": pagination_links["nextPage"]
        }
    }), 200


@product_bp.route("/products/<int:product_id>", methods=["GET"])
def find_product(product_id):
    product = get_product_by_id(product_id)

    if product is None:
        return jsonify({
            "success": False,
            "message": "Producto no encontrado"
        }), 404

    return jsonify({
        "success": True,
        "data": product.to_dict()
    }), 200


@product_bp.route("/products", methods=["POST"])
@jwt_required()
def create():
    data = request.get_json(silent=True) or {}

    product, error, status_code = create_product(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Producto creado correctamente",
        "data": product.to_dict()
    }), status_code


@product_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
def update(product_id):
    data = request.get_json(silent=True) or {}

    product, error, status_code = update_product(product_id, data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Producto actualizado correctamente",
        "data": product.to_dict()
    }), status_code


@product_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete(product_id):
    product, error, status_code = deactivate_product(product_id)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Producto desactivado correctamente"
    }), status_code