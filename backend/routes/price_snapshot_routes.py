from flask import Blueprint, jsonify, request

from flask_jwt_extended import jwt_required

from services.price_snapshot_service import (
    get_price_snapshots,
    get_price_snapshot_by_id,
    get_latest_price_by_store_product,
    create_price_snapshot,
    delete_price_snapshot
)

price_snapshot_bp = Blueprint("price_snapshots", __name__)

@price_snapshot_bp.route("/", methods=["GET"])
def list_price_snapshot():
    store_product_id = request.args.get("storeProductId", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("perPage", 10, type=int)

    pagination = get_price_snapshots(
        store_product_id=store_product_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        "success": True,
        "data": [
            price_snapshot.to_dict()
            for price_snapshot in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages
        }
    }), 200

@price_snapshot_bp.route("/<int:price_snapshot_id>", methods=["GET"])
def find_price_snapshot(price_snapshot_id):
    price_snapshot = get_price_snapshot_by_id(price_snapshot_id)

    if price_snapshot is None:
        return jsonify({
            "success": False,
            "message": "Registro de precio no encontrado"
        }), 404

    return jsonify({
        "success": True,
        "data": price_snapshot.to_dict()
    }), 200


@price_snapshot_bp.route("/store-product/<int:store_product_id>/latest", methods=["GET"])
def find_latest_price_by_store_product(store_product_id):
    price_snapshot, error, status_code = get_latest_price_by_store_product(
        store_product_id
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "data": price_snapshot.to_dict()
    }), status_code


@price_snapshot_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    data = request.get_json(silent=True) or {}

    price_snapshot, error, status_code = create_price_snapshot(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Registro de precio creado correctamente",
        "data": price_snapshot.to_dict()
    }), status_code


@price_snapshot_bp.route("/<int:price_snapshot_id>", methods=["DELETE"])
@jwt_required()
def delete(price_snapshot_id):
    price_snapshot, error, status_code = delete_price_snapshot(price_snapshot_id)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Registro de precio eliminado correctamente"
    }), status_code