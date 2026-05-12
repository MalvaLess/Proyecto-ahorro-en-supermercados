from flask import Blueprint, jsonify, request

from services.user_service import (
    get_users,
    get_user_by_id,
    create_user,
    update_user,
    deactivate_user
)

user_bp = Blueprint("users", __name__)

@user_bp.route("/", methods=["GET"])
def list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("perPage", 10, type=int)

    pagination = get_users(
        page=page,
        per_page=per_page
    )

    return jsonify({
        "success": True,
        "data": [user.to_dict() for user in pagination.items],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages
        }
    }), 200

@user_bp.route("/<int:user_id>", methods=["GET"])
def find_user(user_id):
    user = get_user_by_id(user_id)

    if user is None:
        return jsonify({
            "success": False,
            "message": "Usuario no encontrado"
        }), 404

    return jsonify({
        "success": True,
        "data": user.to_dict()
    }), 200

    

@user_bp.route("/", methods=(["POST"]))
def create():
    data = request.get_json(silent=True) or {}

    user, error, status_code = create_user(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code
    
    return jsonify({
        "success": True,
        "message": "Usuario creado correctamente",
        "data": user.to_dict()
    }), status_code


@user_bp.route("/<int:user_id>", methods=["DELETE"])
def delete(user_id):
    user, error, status_code = deactivate_user(user_id)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code
    
    return jsonify({
        "success": True,
        "message": "Usuario desactivado correctamente"
    }), status_code