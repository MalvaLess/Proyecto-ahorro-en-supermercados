from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from services.offer_service import (
    get_offers,
    get_offer_by_id,
    create_offer,
    update_offer,
    deactivate_offer
)

offer_bp = Blueprint("offers", __name__)

@offer_bp.route("/", methods=["GET"])
def list_offers():
    store_product_id = request.args.get("storeProductId", type=int)
    offer_type = request.args.get("offerType", type=str)
    is_active = request.args.get("isActive")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("perPage", 10, type=int)

    pagination = get_offers(
        store_product_id=store_product_id,
        offer_type=offer_type,
        is_active=is_active,
        page=page,
        per_page=per_page
    )

    return jsonify({
        "success": True,
        "data": [
            offer.to_dict()
            for offer in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages
        }
    }), 200


@offer_bp.route("/<int:offer_id>", methods=["GET"])
def find_offer(offer_id):
    offer = get_offer_by_id(offer_id)

    if offer is None:
        return jsonify({
            "success": False,
            "message": "Oferta no encontrada"
        }), 404

    return jsonify({
        "success": True,
        "data": offer.to_dict()
    }), 200


@offer_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    data = request.get_json(silent=True) or {}

    offer, error, status_code = create_offer(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Oferta creada correctamente",
        "data": offer.to_dict()
    }), status_code


@offer_bp.route("/<int:offer_id>", methods=["PUT"])
@jwt_required()
def update(offer_id):
    data = request.get_json(silent=True) or {}

    offer, error, status_code = update_offer(
        offer_id=offer_id,
        data=data
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Oferta actualizada correctamente",
        "data": offer.to_dict()
    }), status_code


@offer_bp.route("/<int:offer_id>", methods=["DELETE"])
@jwt_required()
def delete(offer_id):
    offer, error, status_code = deactivate_offer(offer_id)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Oferta desactivada correctamente"
    }), status_code
