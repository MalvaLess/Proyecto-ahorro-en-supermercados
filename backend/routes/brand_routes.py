from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from services.brand_service import (
    get_brands,
    get_brand_by_id,
    create_brand,
    update_brand,
    delete_brand
)

brand_bp = Blueprint("brands", __name__)

@brand_bp.route("/", methods=["GET"])
def list_brands():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = get_brands(
        page=page,
        per_page=per_page
    )

    return jsonify({
        "success": True,
        "data": [brand.to_dict() for brand in pagination.items],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages
        }
    }), 200 


@brand_bp.route("/<int:brand_id>", methods=["GET"])
def find_brand(brand_id):
    brand = get_brand_by_id(brand_id)

    if brand is None:
        return jsonify({
            "success": False,
            "message": "Marca no encontrada"
        }), 404
    
    return jsonify({
        "success": True,
        "data": brand.to_dict()
    }), 200


@brand_bp.route("/", methods=["POST"])
def create():
    data = request.get_json(silent=True) or {}

    brand, error, status_code = create_brand(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code
    
    return jsonify({
        "success": True,
        "message": "Marca creada correctamente",
        "data": brand.to_dict()
    }), status_code
 

@brand_bp.route("/<int:brand_id>", methods=["PUT"])
def update(brand_id):
    data = request.get_json(silent=True) or {}

    brand, error, status_code = update_brand(brand_id, data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code
    
    return jsonify({
        "success": True,
        "message": "Marca actualizada correctamente",
        "data": brand.to_dict()
    }), status_code


@brand_bp.route("/<int:brand_id>", methods=["DELETE"])
def delete(brand_id):
    brand, error, status_code = delete_brand(brand_id)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Marca eliminada correctamente"
    }), status_code

