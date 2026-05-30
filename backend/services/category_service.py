from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, Category, ProductCategory

def get_categories(page=1, per_page=10):
    query = Category.query

    per_page = min(per_page, 10)

    return query.order_by(Category.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def get_category_by_id(category_id):
    return db.session.get(Category, category_id)


def create_category(data):
    name = data.get("name")

    if name is None or str(name).strip() == "":
        return None, {
            "message": "El nombre de la categoria es obligatorio"
        }, 400
    
    clean_name = name.strip()

    existing_category = Category.query.filter(
        func.lower(Category.name) == clean_name.lower() 
    ).first()

    if existing_category:
        return None, {
            "message": "Ya existe una categoría con ese nombre"
        }, 409
    
    category = Category(name=clean_name)

    try:

        db.session.add(category)
        db.session.commit()

        return category, None, 201
    
    except IntegrityError:

        db.session.rollback()

        return None, {
            "message": "No se pudo crear la categoria por una restricción de integridad"
        }, 409
    
    except SQLAlchemyError as error:

        db.session.rollback()

        return None, {
            "message": "Error al crear la categoria",
            "error": str(error)
        }, 500
    

def update_category(category_id, data):
    category = get_category_by_id(category_id)

    if category is None:
        return None, {
            "message": "Categoría no encontrada"
        }, 404
    
    if "name" in data:
        name = data.get("name")

        if name is None or str(name).strip() == "":  # strip() con paréntesis: llama al método, no compara el objeto
            return None, {
                "message": "El nombre de la categoría no puede estar vacío"
            }, 400

        clean_name = name.strip()

        existing_category = Category.query.filter(
            func.lower(Category.name) == clean_name.lower(),
            Category.categoryId != category.categoryId
        ).first()

        if existing_category:
            return None, {
                "message": "Ya existe otra categoría con ese nombre"
            }, 409
        
        category.name = clean_name

        try:
            db.session.commit()

            return category, None, 200
    
        except IntegrityError:

            db.session.rollback()

            return None, {
                "message": "No se pudo actualizar la categoría por una restricción de integridad"
            }, 409
        
        except SQLAlchemyError as error:

            db.session.rollback()

            return None, {
                "message": "Error al actualizar categoría",
                "error":  str(error)
            }, 500


def delete_category(category_id):
    category = get_category_by_id(category_id)

    if category is None:
        return None, {
            "message": "Categoría no encontrada"
        }, 404
    
    product_using_category = ProductCategory.query.filter_by(categoryId=category_id).first()

    if product_using_category:
        return None, {
            "message": "No se puede eliminar la categoría porque tiene productos asociados"
        }, 409
    
    try:

        db.session.delete(category)
        db.session.commit()

        return category, None, 200
    
    except SQLAlchemyError as error:

        db.session.rollback()

        return None, {
            "message": "Error al eliminar la categoría",
            "error": str(error)
        }, 500