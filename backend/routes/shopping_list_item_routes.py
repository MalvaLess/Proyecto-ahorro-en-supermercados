from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.shopping_list_item_service import (
    get_items_by_shopping_list,
    add_item_to_shopping_list,
    update_shopping_list_item,
    remove_item_from_shopping_list
)


shopping_list_item_bp = Blueprint("shopping_list_items", __name__)


@shopping_list_item_bp.route("/<int:shopping_list_id>/items", methods=["GET"])
@jwt_required()
def list_items(shopping_list_id):
    user_id = int(get_jwt_identity())

    items, error, status_code = get_items_by_shopping_list(
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
        "data": [
            item.to_dict()
            for item in items
        ]
    }), status_code


@shopping_list_item_bp.route("/<int:shopping_list_id>/items", methods=["POST"])
@jwt_required()
def add_item(shopping_list_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    item, error, status_code = add_item_to_shopping_list(
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
        "message": "Producto agregado a la lista correctamente",
        "data": item.to_dict()
    }), status_code


@shopping_list_item_bp.route(
    "/<int:shopping_list_id>/items/<int:item_id>",
    methods=["PUT"]
)
@jwt_required()
def update_item(shopping_list_id, item_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    item, error, status_code = update_shopping_list_item(
        shopping_list_id=shopping_list_id,
        item_id=item_id,
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
        "message": "Producto de la lista actualizado correctamente",
        "data": item.to_dict()
    }), status_code


@shopping_list_item_bp.route(
    "/<int:shopping_list_id>/items/<int:item_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_item(shopping_list_id, item_id):
    user_id = int(get_jwt_identity())

    item, error, status_code = remove_item_from_shopping_list(
        shopping_list_id=shopping_list_id,
        item_id=item_id,
        user_id=user_id
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Producto eliminado de la lista correctamente"
    }), status_code