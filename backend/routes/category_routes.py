from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from services.category_service import (
    get_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category
)

category_bp = Blueprint("categories", __name__)

@category_bp.route("/", methods=["GET"])
def list_categories():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = get_categories(
        page=page,
        per_page=per_page
    )

    return jsonify({
        "success": True,
        "data": [category.to_dict() for category in pagination.items],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages
        }
    }), 200 


@category_bp.route("/<int:category_id>", methods=["GET"])
def find_category(category_id):
    category = get_category_by_id(category_id)

    if category is None:
        return jsonify({
            "success": False,
            "message": "Categoría no encontrada"
        }), 404
    
    return jsonify({
        "success": True,
        "data": category.to_dict()
    }), 200


@category_bp.route("/", methods=["POST"])
def create():
    data = request.get_json(silent=True) or {}

    category, error, status_code = create_category(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code
    
    return jsonify({
        "success": True,
        "message": "Marca creada correctamente",
        "data": category.to_dict()
    }), status_code
 

@category_bp.route("/<int:category_id>", methods=["PUT"])
def update(category_id):
    data = request.get_json(silent=True) or {}

    category, error, status_code = update_category(category_id, data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code
    
    return jsonify({
        "success": True,
        "message": "Categoría actualizada correctamente",
        "data": category.to_dict()
    }), status_code


@category_bp.route("/<int:category_id>", methods=["DELETE"])
def delete(category_id):
    category, error, status_code = delete_category(category_id)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Categoría eliminada correctamente"
    }), status_code

