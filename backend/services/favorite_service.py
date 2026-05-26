from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, Favorite, Product


def get_user_favorites(user_id, page=1, per_page=10):
    per_page = min(per_page, 10)

    return Favorite.query.filter_by(
        userId=user_id
    ).order_by(
        Favorite.favoriteId.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


def add_favorite(user_id, data):
    product_id = data.get("productId")

    if product_id is None or str(product_id).strip() == "":
        return None, {
            "message": "productId es obligatorio"
        }, 400

    product = db.session.get(Product, product_id)

    if product is None:
        return None, {
            "message": "Producto no encontrado"
        }, 404

    existing_favorite = Favorite.query.filter_by(
        userId=user_id,
        productId=product_id
    ).first()

    if existing_favorite:
        return existing_favorite, None, 200

    try:
        favorite = Favorite(
            userId=user_id,
            productId=product_id
        )

        db.session.add(favorite)
        db.session.commit()

        return favorite, None, 201

    except IntegrityError as error:
        db.session.rollback()

        return None, {
            "message": "No se pudo agregar el favorito por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al agregar favorito",
            "error": str(error)
        }, 500


def remove_favorite_by_product(user_id, product_id):
    favorite = Favorite.query.filter_by(
        userId=user_id,
        productId=product_id
    ).first()

    if favorite is None:
        return None, {
            "message": "Favorito no encontrado"
        }, 404

    try:
        db.session.delete(favorite)
        db.session.commit()

        return favorite, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al eliminar favorito",
            "error": str(error)
        }, 500