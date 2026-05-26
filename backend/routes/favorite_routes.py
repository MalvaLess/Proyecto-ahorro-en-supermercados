from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.favorite_service import (
    get_user_favorites,
    add_favorite,
    remove_favorite_by_product
)


favorite_bp = Blueprint("favorites", __name__)


@favorite_bp.route("/", methods=["GET"])
@jwt_required()
def list_favorites():
    user_id = int(get_jwt_identity())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("perPage", 10, type=int)

    pagination = get_user_favorites(
        user_id=user_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        "success": True,
        "data": [
            favorite.to_dict()
            for favorite in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages
        }
    }), 200


@favorite_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    favorite, error, status_code = add_favorite(
        user_id=user_id,
        data=data
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    message = "Producto agregado a favoritos"

    if status_code == 200:
        message = "El producto ya estaba en favoritos"

    return jsonify({
        "success": True,
        "message": message,
        "data": favorite.to_dict()
    }), status_code


@favorite_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_by_product(product_id):
    user_id = int(get_jwt_identity())

    favorite, error, status_code = remove_favorite_by_product(
        user_id=user_id,
        product_id=product_id
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Producto eliminado de favoritos"
    }), status_code