from flask import Blueprint, jsonify, request

from services.price_comparison_service import (
    parse_store_ids,
    compare_product_prices
)

price_comparison_bp = Blueprint("price_comparison", __name__)


@price_comparison_bp.route("/products/<int:product_id>", methods=["GET"])
def compare_prices(product_id):
    store_ids_raw = request.args.get("storeIds")

    store_ids, parse_error = parse_store_ids(store_ids_raw)

    if parse_error:
        return jsonify({
            "success": False,
            **parse_error
        }), 400

    result, error, status_code = compare_product_prices(
        product_id=product_id,
        store_ids=store_ids
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "data": result
    }), status_code