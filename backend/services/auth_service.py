from flask import current_app
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import SQLAlchemyError
from models.models import db, User

def login_user(data):
    required_fields = ["email", "password"]

    missing_fields = []

    for field in required_fields:
        if data.get(field) is None or str(data.get(field)).strip() == "":
            missing_fields.append(field)

    if missing_fields:
        return None, {
            "message": "Faltan campos obligatorios",
            "fields": missing_fields
        }, 400
    
    email = data["email"].strip().lower()
    password = data["password"]
    
    user = User.query.filter_by(email=email).first()

    if User is None:
        return None, {
            "message": "Credenciales inválidas"
        }, 401
    
    if not user.isActive:
        return None, {
            "message": "El usuario se encuentra desactivado"
        }, 403
    
    if not user.check_password(password):
        return None, {
            "message": "Credenciales inválidas"
        }, 401
    
    try:
        user.lastLoginAt = datetime.now(timezone.utc)
        db.session.commit()

        access_token = create_access_token(
            identity = str(user.userId),
            additional_claims = {
                "email": user.email
            }
        )

        expires_delta = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        expires_in = int(expires_delta.total_seconds())

        return {
            "user": user.to_dict(),
            "token_type": "Bearer",
            "access_token": access_token,
            "expiresIn": expires_in
        }, None, 200
    
    except SQLAlchemyError as error:

        db.session.rollback()

        return None, {
            "message": "Error al iniciar sesión",
            "error": str(error)
        }, 500