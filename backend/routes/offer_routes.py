from flask import Blueprint, jsonify, request

from services.offer_service import get_offers, create_offer, update_offer, delete_offer

offer_bp = Blueprint("offers", __name__)


@offer_bp.route("/", methods=["GET"])
def list_offers():
    store_product_id = request.args.get("storeProductId", type=int)
    offer_type = request.args.get("offerType", type=str)

    offers = get_offers(store_product_id=store_product_id, offer_type=offer_type)

    return jsonify({
        "success": True,
        "data": [o.to_dict() for o in offers]
    }), 200


@offer_bp.route("/", methods=["POST"])
def create():
    data = request.get_json(silent=True) or {}

    offer, error, status_code = create_offer(data)

    if error:
        return jsonify({"success": False, **error}), status_code

    return jsonify({
        "success": True,
        "message": "Oferta creada correctamente",
        "data": offer.to_dict()
    }), status_code


@offer_bp.route("/<int:store_product_id>", methods=["PUT"])
def update(store_product_id):
    data = request.get_json(silent=True) or {}

    offer, error, status_code = update_offer(store_product_id, data)

    if error:
        return jsonify({"success": False, **error}), status_code

    return jsonify({
        "success": True,
        "message": "Oferta actualizada correctamente",
        "data": offer.to_dict()
    }), status_code


@offer_bp.route("/<int:store_product_id>", methods=["DELETE"])
def delete(store_product_id):
    offer, error, status_code = delete_offer(store_product_id)

    if error:
        return jsonify({"success": False, **error}), status_code

    return jsonify({
        "success": True,
        "message": "Oferta desactivada correctamente"
    }), status_code
