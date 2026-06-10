from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from services.store_chain_service import (
    get_store_chains,
    get_store_chain_by_id,
    create_store_chain,
    update_store_chain,
    deactivate_store_chain
)


store_chain_bp = Blueprint("store_chains", __name__)


@store_chain_bp.route("/", methods=["GET"])
def list_store_chains():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("perPage", 10, type=int)

    pagination = get_store_chains(
        page=page,
        per_page=per_page
    )

    return jsonify({
        "success": True,
        "data": [
            store_chain.to_dict()
            for store_chain in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "perPage": pagination.per_page,
            "totalItems": pagination.total,
            "totalPages": pagination.pages
        }
    }), 200


@store_chain_bp.route("/<int:store_chain_id>", methods=["GET"])
def find_store_chain(store_chain_id):
    store_chain = get_store_chain_by_id(store_chain_id)

    if store_chain is None:
        return jsonify({
            "success": False,
            "message": "Cadena no encontrada"
        }), 404

    return jsonify({
        "success": True,
        "data": store_chain.to_dict()
    }), 200


@store_chain_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    data = request.get_json(silent=True) or {}

    store_chain, error, status_code = create_store_chain(data)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Cadena creada correctamente",
        "data": store_chain.to_dict()
    }), status_code


@store_chain_bp.route("/<int:store_chain_id>", methods=["PUT"])
@jwt_required()
def update(store_chain_id):
    data = request.get_json(silent=True) or {}

    store_chain, error, status_code = update_store_chain(
        store_chain_id,
        data
    )

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Cadena actualizada correctamente",
        "data": store_chain.to_dict()
    }), status_code


@store_chain_bp.route("/<int:store_chain_id>", methods=["DELETE"])
@jwt_required()
def delete(store_chain_id):
    store_chain, error, status_code = deactivate_store_chain(store_chain_id)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Cadena desactivada correctamente"
    }), status_code