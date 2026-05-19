from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.models import (
    db,
    ShoppingList,
    ShoppingListItem,
    Product,
    StoreProduct,
    PriceSnapshot
)


def parse_decimal(value, field_name):
    if value is None or str(value).strip() == "":
        return Decimal("0")

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"El campo {field_name} debe ser numérico")


def parse_quantity(value):
    if value is None:
        return 1

    try:
        quantity = int(value)
    except ValueError:
        raise ValueError("quantity debe ser un número entero")

    if quantity <= 0:
        raise ValueError("quantity debe ser mayor a 0")

    return quantity


def get_user_shopping_list(shopping_list_id, user_id):
    return ShoppingList.query.filter_by(
        shoppingListId=shopping_list_id,
        userId=user_id
    ).first()


def get_latest_price_by_store_product(store_product_id):
    return PriceSnapshot.query.filter_by(
        storeProductId=store_product_id
    ).order_by(
        PriceSnapshot.capturedAt.desc(),
        PriceSnapshot.priceSnapshotId.desc()
    ).first()


def recalculate_shopping_list_totals(shopping_list):
    items = ShoppingListItem.query.filter_by(
        shoppingListId=shopping_list.shoppingListId
    ).all()

    subtotal = sum(
        item.totalPrice or Decimal("0")
        for item in items
    )

    shopping_list.subTotal = subtotal
    shopping_list.total = subtotal


def get_items_by_shopping_list(shopping_list_id, user_id):
    shopping_list = get_user_shopping_list(shopping_list_id, user_id)

    if shopping_list is None:
        return None, {
            "message": "Lista de compras no encontrada"
        }, 404

    items = ShoppingListItem.query.filter_by(
        shoppingListId=shopping_list_id
    ).order_by(
        ShoppingListItem.shoppingListItemId.desc()
    ).all()

    return items, None, 200


def add_item_to_shopping_list(shopping_list_id, user_id, data):
    shopping_list = get_user_shopping_list(shopping_list_id, user_id)

    if shopping_list is None:
        return None, {
            "message": "Lista de compras no encontrada"
        }, 404

    required_fields = ["productId"]

    missing_fields = []

    for field in required_fields:
        if data.get(field) is None or str(data.get(field)).strip() == "":
            missing_fields.append(field)

    if missing_fields:
        return None, {
            "message": "Faltan campos obligatorios",
            "fields": missing_fields
        }, 400

    product = db.session.get(Product, data["productId"])

    if product is None:
        return None, {
            "message": "Producto no encontrado"
        }, 404

    selected_store_product_id = data.get("selectedStoreProductId")

    unit_price = Decimal("0")

    if selected_store_product_id is not None:
        store_product = db.session.get(StoreProduct, selected_store_product_id)

        if store_product is None:
            return None, {
                "message": "Producto de tienda no encontrado"
            }, 404

        if store_product.productId != product.productId:
            return None, {
                "message": "El producto de tienda seleccionado no corresponde al producto indicado"
            }, 400

        latest_price = get_latest_price_by_store_product(selected_store_product_id)

        if latest_price:
            unit_price = latest_price.price

    if "unitPrice" in data:
        unit_price = parse_decimal(data.get("unitPrice"), "unitPrice")

    try:
        quantity = parse_quantity(data.get("quantity", 1))
        total_price = unit_price * quantity

        existing_item = ShoppingListItem.query.filter_by(
            shoppingListId=shopping_list_id,
            productId=product.productId,
            selectedStoreProductId=selected_store_product_id
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.unitPrice = unit_price
            existing_item.totalPrice = existing_item.unitPrice * existing_item.quantity

            recalculate_shopping_list_totals(shopping_list)
            db.session.commit()

            return existing_item, None, 200

        item = ShoppingListItem(
            shoppingListId=shopping_list_id,
            productId=product.productId,
            selectedStoreProductId=selected_store_product_id,
            quantity=quantity,
            unitPrice=unit_price,
            totalPrice=total_price
        )

        db.session.add(item)
        db.session.flush()

        recalculate_shopping_list_totals(shopping_list)

        db.session.commit()

        return item, None, 201

    except ValueError as error:
        db.session.rollback()
        return None, {"message": str(error)}, 400

    except IntegrityError as error:
        db.session.rollback()
        return None, {
            "message": "No se pudo agregar el producto a la lista",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al agregar producto a la lista",
            "error": str(error)
        }, 500


def update_shopping_list_item(shopping_list_id, item_id, user_id, data):
    shopping_list = get_user_shopping_list(shopping_list_id, user_id)

    if shopping_list is None:
        return None, {
            "message": "Lista de compras no encontrada"
        }, 404

    item = ShoppingListItem.query.filter_by(
        shoppingListItemId=item_id,
        shoppingListId=shopping_list_id
    ).first()

    if item is None:
        return None, {
            "message": "Producto de la lista no encontrado"
        }, 404

    try:
        if "quantity" in data:
            item.quantity = parse_quantity(data.get("quantity"))

        if "unitPrice" in data:
            item.unitPrice = parse_decimal(data.get("unitPrice"), "unitPrice")

        item.totalPrice = item.unitPrice * item.quantity

        recalculate_shopping_list_totals(shopping_list)

        db.session.commit()

        return item, None, 200

    except ValueError as error:
        db.session.rollback()
        return None, {"message": str(error)}, 400

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al actualizar producto de la lista",
            "error": str(error)
        }, 500


def remove_item_from_shopping_list(shopping_list_id, item_id, user_id):
    shopping_list = get_user_shopping_list(shopping_list_id, user_id)

    if shopping_list is None:
        return None, {
            "message": "Lista de compras no encontrada"
        }, 404

    item = ShoppingListItem.query.filter_by(
        shoppingListItemId=item_id,
        shoppingListId=shopping_list_id
    ).first()

    if item is None:
        return None, {
            "message": "Producto de la lista no encontrado"
        }, 404

    try:
        db.session.delete(item)
        db.session.flush()

        recalculate_shopping_list_totals(shopping_list)

        db.session.commit()

        return item, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al eliminar producto de la lista",
            "error": str(error)
        }, 500