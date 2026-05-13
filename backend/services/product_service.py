import re
import unicodedata
from decimal import Decimal, InvalidOperation

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import db, Product, Brand, Category, ProductCategory


def normalize_product_name(name: str) -> str:
    value = name.strip().lower()

    # Quitar tildes
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))

    # Reemplazar espacios múltiples por uno solo
    value = re.sub(r"\s+", " ", value)

    return value


def parse_decimal(value, field_name):
    if value is None or value == "":
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"El campo {field_name} debe ser numérico")


def get_products(search=None, brand_id=None, category_id=None, is_active=None, page=1, per_page=10):
    query = Product.query

    if search:
        search_pattern = f"%{normalize_product_name(search)}%"
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search.strip()}%"),
                Product.normalizedName.ilike(search_pattern),
                Product.ean.ilike(f"%{search.strip()}%")
            )
        )

    if brand_id:
        query = query.filter(Product.brandId == brand_id)

    if category_id:
        query = query.join(ProductCategory).filter(
            ProductCategory.categoryId == category_id
        )

    if is_active is not None:
        is_active_value = is_active.lower() == "true"
        query = query.filter(Product.isActive == is_active_value)

    per_page = min(per_page, 50)

    return query.order_by(Product.productId.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


def get_product_by_id(product_id):
    return db.session.get(Product, product_id)


def create_product(data):
    required_fields = ["brandId", "name", "unit"]

    missing_fields = [
        field for field in required_fields
        if data.get(field) is None or str(data.get(field)).strip() == ""
    ]

    if missing_fields:
        return None, {
            "message": "Faltan campos obligatorios",
            "fields": missing_fields
        }, 400

    brand = db.session.get(Brand, data["brandId"])

    if brand is None:
        return None, {
            "message": "La marca indicada no existe"
        }, 404

    category_ids = data.get("categoryIds", [])

    if not isinstance(category_ids, list):
        return None, {
            "message": "categoryIds debe ser una lista"
        }, 400

    unique_category_ids = list(dict.fromkeys(category_ids))

    if unique_category_ids:
        categories = Category.query.filter(
            Category.categoryId.in_(unique_category_ids)
        ).all()

        if len(categories) != len(unique_category_ids):
            return None, {
                "message": "Una o más categorías no existen"
            }, 400

    try:
        clean_name = data["name"].strip()

        product = Product(
            brandId=data["brandId"],
            name=clean_name,
            normalizedName=normalize_product_name(clean_name),
            ean=data.get("ean"),
            description=data.get("description"),
            weightValue=parse_decimal(data.get("weightValue"), "weightValue"),
            unit=data["unit"].strip(),
            format=data.get("format"),
            imageURL=data.get("imageURL"),
            isActive=data.get("isActive", True)
        )

        db.session.add(product)
        db.session.flush()

        for category_id in unique_category_ids:
            db.session.add(ProductCategory(
                productId=product.productId,
                categoryId=category_id
            ))

        db.session.commit()

        return product, None, 201

    except ValueError as error:
        db.session.rollback()
        return None, {"message": str(error)}, 400

    except IntegrityError as error:
        db.session.rollback()
        return None, {
            "message": "No se pudo crear el producto por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al crear producto",
            "error": str(error)
        }, 500


def update_product(product_id, data):
    product = get_product_by_id(product_id)

    if product is None:
        return None, {
            "message": "Producto no encontrado"
        }, 404

    try:
        if "brandId" in data:
            brand = db.session.get(Brand, data["brandId"])

            if brand is None:
                return None, {
                    "message": "La marca indicada no existe"
                }, 404

            product.brandId = data["brandId"]

        if "name" in data:
            if data["name"] is None or str(data["name"]).strip() == "":
                return None, {
                    "message": "El nombre del producto no puede estar vacío"
                }, 400

            clean_name = data["name"].strip()
            product.name = clean_name
            product.normalizedName = normalize_product_name(clean_name)

        if "ean" in data:
            product.ean = data["ean"]

        if "description" in data:
            product.description = data["description"]

        if "weightValue" in data:
            product.weightValue = parse_decimal(data.get("weightValue"), "weightValue")

        if "unit" in data:
            if data["unit"] is None or str(data["unit"]).strip() == "":
                return None, {
                    "message": "La unidad del producto no puede estar vacía"
                }, 400

            product.unit = data["unit"].strip()

        if "format" in data:
            product.format = data["format"]

        if "imageURL" in data:
            product.imageURL = data["imageURL"]

        if "isActive" in data:
            product.isActive = data["isActive"]

        if "categoryIds" in data:
            category_ids = data.get("categoryIds", [])

            if not isinstance(category_ids, list):
                return None, {
                    "message": "categoryIds debe ser una lista"
                }, 400

            unique_category_ids = list(dict.fromkeys(category_ids))

            if unique_category_ids:
                categories = Category.query.filter(
                    Category.categoryId.in_(unique_category_ids)
                ).all()

                if len(categories) != len(unique_category_ids):
                    return None, {
                        "message": "Una o más categorías no existen"
                    }, 400

            ProductCategory.query.filter_by(
                productId=product.productId
            ).delete(synchronize_session=False)

            for category_id in unique_category_ids:
                db.session.add(ProductCategory(
                    productId=product.productId,
                    categoryId=category_id
                ))

        db.session.commit()

        return product, None, 200

    except ValueError as error:
        db.session.rollback()
        return None, {"message": str(error)}, 400

    except IntegrityError as error:
        db.session.rollback()
        return None, {
            "message": "No se pudo actualizar el producto por una restricción de integridad",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al actualizar producto",
            "error": str(error)
        }, 500


def deactivate_product(product_id):
    product = get_product_by_id(product_id)

    if product is None:
        return None, {
            "message": "Producto no encontrado"
        }, 404

    try:
        product.isActive = False
        db.session.commit()

        return product, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al desactivar producto",
            "error": str(error)
        }, 500