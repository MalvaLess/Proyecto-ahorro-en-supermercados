from flask import current_app
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from sqlalchemy.exc import SQLAlchemyError
from models.models import db, User
from extensions import mail
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

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

    if user is None:  # corregido: era "User" (la clase) en vez de "user" (la instancia)
        return None, {
            "message": "Credenciales inválidas"
        }, 401
    
    if not user.isActive:
        return None, {
            "message": "El usuario se encuentra desactivado"
        }, 403
    
    """ if user.passwordHash is None:
        return None, {
            "message": "Esta cuenta usa Google Sign-In. Iniciá sesión con Google."
        }, 401 """

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


def _get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def forgot_password(data):
    email = data.get("email", "").strip().lower()

    if not email:
        return None, {"message": "El email es obligatorio"}, 400

    user = User.query.filter_by(email=email).first()

    # Respuesta idéntica exista o no el email — evita enumerar usuarios registrados
    response = {"message": "Si el email está registrado, recibirás un enlace de recuperación"}

    if user is None or not user.isActive:
        return response, None, 200

    token = _get_serializer().dumps(user.email, salt="password-reset")
    frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
    reset_url = f"{frontend_url}/reset-password/{token}"

    try:
        msg = Message(
            subject="Recuperación de contraseña - SmartMarket",
            recipients=[user.email],
            body=(
                f"Hola {user.firstName},\n\n"
                f"Recibimos una solicitud para restablecer tu contraseña.\n\n"
                f"Hacé clic en el siguiente enlace (válido por 30 minutos):\n\n"
                f"{reset_url}\n\n"
                f"Si no solicitaste este cambio, ignorá este correo."
            )
        )
        mail.send(msg)
    except Exception:
        return None, {"message": "Error al enviar el correo. Intentá más tarde."}, 500

    return response, None, 200


def reset_password(token, data):
    new_password = data.get("newPassword", "")

    if not new_password or len(str(new_password).strip()) < 6:
        return None, {"message": "La contraseña debe tener al menos 6 caracteres"}, 400

    try:
        email = _get_serializer().loads(token, salt="password-reset", max_age=1800)
    except SignatureExpired:
        return None, {"message": "El enlace ha expirado. Solicitá uno nuevo."}, 400
    except BadSignature:
        return None, {"message": "El enlace es inválido."}, 400

    user = User.query.filter_by(email=email).first()

    if user is None or not user.isActive:
        return None, {"message": "Usuario no encontrado"}, 404

    try:
        user.set_password(new_password)
        db.session.commit()
        return {"message": "Contraseña actualizada correctamente"}, None, 200
    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {"message": "Error al actualizar la contraseña", "error": str(error)}, 500


def google_login(data):
    token = data.get("token", "").strip()

    if not token:
        return None, {"message": "Token de Google requerido"}, 400

    try:
        client_id = current_app.config.get("GOOGLE_CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)

        google_id = idinfo["sub"]
        email = idinfo["email"].lower()
        first_name = idinfo.get("given_name", "")
        last_name = idinfo.get("family_name", "") or first_name

    except ValueError:
        return None, {"message": "Token de Google inválido"}, 401

    try:
        user = User.query.filter_by(googleId=google_id).first()

        if user is None:
            user = User.query.filter_by(email=email).first()
            if user:
                user.googleId = google_id
            else:
                user = User(
                    firstName=first_name,
                    lastName=last_name,
                    email=email,
                    googleId=google_id
                )
                db.session.add(user)
                db.session.flush()

        if not user.isActive:
            return None, {"message": "El usuario se encuentra desactivado"}, 403

        user.lastLoginAt = datetime.now(timezone.utc)
        db.session.commit()

        access_token = create_access_token(
            identity=str(user.userId),
            additional_claims={"email": user.email}
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
        return None, {"message": "Error al iniciar sesión", "error": str(error)}, 500