from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, User

def get_users(page=1, per_page=10):

    query = User.query

    per_page = min(per_page, 10)

    return query.order_by(User.userId.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


def get_user_by_id(user_id):
    return db.session.get(User, user_id)

def create_user(data):
    required_fields = ["firstName", "lastName", "email", "password"]

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

    if len(password) < 6:
        return None, {
            "message": "La contraseña debe tener al menos 6 caracteres"
        }, 400
    
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return None, {
            "message": "Ya existe un usuario registrado con ese email"
        }, 409
    
    user = User(
        firstName = data["firstName"].strip(),
        lastName = data["lastName"].strip(),
        email = email
    )

    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        return user, None, 201
    except IntegrityError:
        db.session.rollback()
        return None, {
            "message": "No se pudo crear el usuario por una restricción de integridad"
        }, 409
    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al crear el usuario",
            "error": str(error)
        }, 500
    
def update_user(user_id, data):
    user = get_user_by_id(user_id)

    if user is None:
        return None, {
            "message": "Usuario no encontrado"
        }, 404
    
    if "firstName" in data:
        user.firstName = data["firstName"].strip()
    
    if "lastName" in data:
        user.lastName = data["lastName"].strip()

    # corregido: validación y actualización de email movidas a su propio bloque
    if "email" in data:
        new_email = data["email"].strip().lower()
        existing_user = User.query.filter(
            User.email == new_email,
            User.userId != user.userId
        ).first()
        if existing_user:
            return None, {
                "message": "Ya existe otro usuario con ese email"
            }, 409
        user.email = new_email

    if "password" in data:
        password = data["password"]

        if len(password) < 6:
            return None, {
                "message": "La contraseña debe tener al menos 6 caracteres"
            }, 400

        user.set_password(password)

    if "isActive" in data:  # corregido: ya no contiene lógica de email ni el commit
        user.isActive = data["isActive"]

    try:
        db.session.commit()
        return user, None, 200
    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al actualizar el usuario",
            "error": str(error)
        }, 500
        
def deactivate_user(user_id):
    user = get_user_by_id(user_id)

    if user is None:
        return None, {
            "message": "Usuario no encontrado"
        }, 404
    
    user.deactivate()

    try:
        db.session.commit()
        return user, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al desactivar usuario",
            "error": str(error)
        }, 500
    


