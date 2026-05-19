from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.shopping_list_service import (
    get_user_shopping_lists,
    get_shopping_list_by_id,
    create_shopping_list,
    update_shopping_list,
    delete_shopping_list
)


shopping_list_bp = Blueprint("shopping_lists", __name__)


@shopping_list_bp.route("/", methods=["GET"])
def list_shopping_lists():
    user_id = int(get_jwt_identity())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("perPage", 10, type=int)

    pagination = get_user_shopping_lists(
        user_id=user_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        "success": True,
        "data": [
            shopping_list.to_dict()
            for shopping_list in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages
        }
    }), 200


@shopping_list_bp.route("/<int:shopping_list_id>", methods=["GET"])
@jwt_required()
def find_shopping_list(shopping_list_id):
    user_id = int(get_jwt_identity())

    shopping_list = get_shopping_list_by_id(
        shopping_list_id=shopping_list_id,
        user_id=user_id
    )

    if shopping_list is None:
        return jsonify({
            "success": False,
            "message": "Lista de compras no encontrada"
        }), 404

    return jsonify({
        "success": True,
        "data": shopping_list.to_dict()
    }), 200


@shopping_list_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    shopping_list, error, status_code = create_shopping_list(
        user_id=user_id,
        data=data
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Lista de compras creada correctamente",
        "data": shopping_list.to_dict()
    }), status_code


@shopping_list_bp.route("/<int:shopping_list_id>", methods=["PUT"])
@jwt_required()
def update(shopping_list_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    shopping_list, error, status_code = update_shopping_list(
        shopping_list_id=shopping_list_id,
        user_id=user_id,
        data=data
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Lista de compras actualizada correctamente",
        "data": shopping_list.to_dict()
    }), status_code


@shopping_list_bp.route("/<int:shopping_list_id>", methods=["DELETE"])
@jwt_required()
def delete(shopping_list_id):
    user_id = int(get_jwt_identity())

    shopping_list, error, status_code = delete_shopping_list(
        shopping_list_id=shopping_list_id,
        user_id=user_id
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Lista de compras eliminada correctamente"
    }), status_code