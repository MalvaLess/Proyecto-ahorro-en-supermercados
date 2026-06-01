from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, Brand, Product

def get_brands(page=1, per_page=10):
    query = Brand.query

    per_page = min(per_page, 10)

    return query.order_by(Brand.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def get_brand_by_id(brand_id):
    return db.session.get(Brand, brand_id)

def create_brand(data):
    name = data.get("name")

    if name is None or str(name).strip() == "":
        return None, {
            "message": "El nombre de la marca es obligatorio"
        }, 400
    
    clean_name = name.strip()

    existing_brand = Brand.query.filter(
        func.lower(Brand.name) == clean_name.lower()
    ).first()

    if existing_brand:
        return None, {
            "message": "Ya existe una marca con ese nombre"
        }, 409
    
    brand = Brand(name=clean_name)

    try:
        db.session.add(brand)
        db.session.commit()

        return brand, None, 201
    
    except IntegrityError:
        db.session.rollback()

        return None, {
            "message": "No se pudo crear la marca por una restricción de integridad"
        }, 409
    
    except SQLAlchemyError as error:
        db.session.rollback()

        return None, {
            "message": "Error al crear la marca",
            "error": str(error)
        }, 500
    

def update_brand(brand_id, data):
    brand = get_brand_by_id(brand_id)

    if brand is None:
        return None, {
            "message": "Marca no encontrada"
        }, 404
    
    if "name" in data:
        name = data.get("name")

        if name is None or str(name).strip() == "":  # strip() con paréntesis: llama al método, no compara el objeto
            return None, {
                "message": "El nombre de la marca no puede estar vacío"
            }, 400
        
        clean_name = name.strip()

        existing_brand = Brand.query.filter(
            func.lower(Brand.name) == clean_name.lower(),
            Brand.brandId != brand.brandId
        ).first()

        if existing_brand:
            return None, {
                "message": "Ya existe otra marca con ese nombre"
            }, 409
        
        brand.name = clean_name
    
    try:
        db.session.commit()

        return brand, None, 200
    
    except IntegrityError:

        db.session.rollback()

        return None, {
            "message": "No se pudo actualizar la marca por una restricción de integridad"
        }, 409
    
    except SQLAlchemyError as error:

        db.session.rollback()

        return None, {
            "message": "Error al actualizar marca",
            "error":  str(error)
        }, 500

def delete_brand(brand_id):
    brand = get_brand_by_id(brand_id)

    if brand is None:
        return None, {
            "message": "Marca no encontrada"
        }, 404
    
    product_using_brand = Product.query.filter_by(brandId=brand_id).first()

    if product_using_brand:
        return None, {
            "message": "No se puede eliminar la marca porque tiene productos asociados"
        }, 409
    
    try:

        db.session.delete(brand)
        db.session.commit()

        return brand, None, 200
    
    except SQLAlchemyError as error:

        db.session.rollback()

        return None, {
            "message": "Error al eliminar la marca",
            "error": str(error)
        }, 500