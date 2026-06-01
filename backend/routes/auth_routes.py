from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.models import db, User
from services.auth_service import login_user

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

