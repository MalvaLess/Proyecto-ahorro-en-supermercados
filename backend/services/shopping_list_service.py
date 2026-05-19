from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, ShoppingList


def get_user_shopping_lists(user_id, page=1, per_page=10):
    per_page = min(per_page, 10)

    return ShoppingList.query.filter_by(
        userId=user_id
    ).order_by(
        ShoppingList.shoppingListId.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


def get_shopping_list_by_id(shopping_list_id, user_id):
    return ShoppingList.query.filter_by(
        shoppingListId=shopping_list_id,
        userId=user_id
    ).first()


def create_shopping_list(user_id, data):
    name = data.get("name")

    if name is None or str(name).strip() == "":
        return None, {
            "message": "El nombre de la lista es obligatorio"
        }, 400

    try:
        shopping_list = ShoppingList(
            userId=user_id,
            name=name.strip(),
            subTotal=0,
            total=0
        )

        db.session.add(shopping_list)
        db.session.commit()

        return shopping_list, None, 201

    except IntegrityError as error:
        db.session.rollback()

        return None, {
            "message": "No se pudo crear la lista por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al crear lista de compras",
            "error": str(error)
        }, 500


def update_shopping_list(shopping_list_id, user_id, data):
    shopping_list = get_shopping_list_by_id(shopping_list_id, user_id)

    if shopping_list is None:
        return None, {
            "message": "Lista de compras no encontrada"
        }, 404

    if "name" in data:
        name = data.get("name")

        if name is None or str(name).strip() == "":
            return None, {
                "message": "El nombre de la lista no puede estar vacío"
            }, 400

        shopping_list.name = name.strip()

    try:
        db.session.commit()

        return shopping_list, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al actualizar lista de compras",
            "error": str(error)
        }, 500


def delete_shopping_list(shopping_list_id, user_id):
    shopping_list = get_shopping_list_by_id(shopping_list_id, user_id)

    if shopping_list is None:
        return None, {
            "message": "Lista de compras no encontrada"
        }, 404

    try:
        db.session.delete(shopping_list)
        db.session.commit()

        return shopping_list, None, 200

    except IntegrityError as error:
        db.session.rollback()

        return None, {
            "message": "No se puede eliminar la lista porque tiene datos asociados",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al eliminar lista de compras",
            "error": str(error)
        }, 500