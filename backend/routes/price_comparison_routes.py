from flask import Blueprint, jsonify, request

from services.price_comparison_service import (
    parse_chain_ids,
    compare_product_prices,
    get_top_discounts,
    get_offers_paginated
)

price_comparison_bp = Blueprint("price_comparison", __name__)


@price_comparison_bp.route("/top-discounts", methods=["GET"])
def top_discounts():
    limit = request.args.get("limit", 10, type=int)
    limit = min(limit, 50)

    results = get_top_discounts(limit=limit)

    return jsonify({
        "success": True,
        "data": results
    }), 200


@price_comparison_bp.route("/offers", methods=["GET"])
def offers_paginated():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("perPage", 40, type=int)
    per_page = min(per_page, 40)

    result = get_offers_paginated(page=page, per_page=per_page)

    return jsonify({
        "success": True,
        **result
    }), 200


@price_comparison_bp.route("/products/<int:product_id>", methods=["GET"])
def compare_prices(product_id):
    chain_ids_raw = request.args.get("storeChainIds")

    chain_ids, parse_error = parse_chain_ids(chain_ids_raw)

    if parse_error:
        return jsonify({
            "success": False,
            **parse_error
        }), 400

    result, error, status_code = compare_product_prices(
        product_id=product_id,
        chain_ids=chain_ids
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