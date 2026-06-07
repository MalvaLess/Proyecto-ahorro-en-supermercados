from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.models import db, User
from services.auth_service import login_user, forgot_password, reset_password, google_login

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    result, error, status_code = login_user(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code
    
    return jsonify({
        "success": True,
        "message": "Inicio de sesión exitoso",
        "data": result
    }), status_code

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)  # API moderna SQLAlchemy 2.x: reemplaza User.query.get() deprecado

    if user is None:
        return jsonify({
            "success": False,
            "message": "Usuario no encontrado"
        }), 404
    
    return jsonify({
        "success": True,
        "data": user.to_dict()
    }), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password_route():
    data = request.get_json(silent=True) or {}

    result, error, status_code = forgot_password(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        **result
    }), status_code


@auth_bp.route("/google", methods=["POST"])
def google_login_route():
    data = request.get_json(silent=True) or {}

    result, error, status_code = google_login(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Inicio de sesión con Google exitoso",
        "data": result
    }), status_code


@auth_bp.route("/reset-password/<string:token>", methods=["POST"])
def reset_password_route(token):
    data = request.get_json(silent=True) or {}

    result, error, status_code = reset_password(token, data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        **result
    }), status_code
