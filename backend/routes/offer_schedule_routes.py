from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from services.offer_schedule_service import (
    get_schedules_by_offer,
    add_schedule_to_offer,
    replace_offer_schedules,
    delete_offer_schedule,
    offer_schedule_to_dict
)


offer_schedule_bp = Blueprint("offer_schedules", __name__)


@offer_schedule_bp.route("/offers/<int:offer_id>/schedules", methods=["GET"])
def list_offer_schedules(offer_id):
    schedules, error, status_code = get_schedules_by_offer(offer_id)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "data": [
            offer_schedule_to_dict(schedule)
            for schedule in schedules
        ]
    }), status_code


@offer_schedule_bp.route("/offers/<int:offer_id>/schedules", methods=["POST"])
def create_offer_schedule(offer_id):
    data = request.get_json(silent=True) or {}

    schedule, error, status_code = add_schedule_to_offer(
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
        "message": "Día asociado correctamente a la oferta",
        "data": offer_schedule_to_dict(schedule)
    }), status_code


@offer_schedule_bp.route("/offers/<int:offer_id>/schedules", methods=["PUT"])
def replace_schedules(offer_id):
    data = request.get_json(silent=True) or {}

    schedules, error, status_code = replace_offer_schedules(
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
        "message": "Días de la oferta actualizados correctamente",
        "data": [
            offer_schedule_to_dict(schedule)
            for schedule in schedules
        ]
    }), status_code


@offer_schedule_bp.route("/offer-schedules/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    schedule, error, status_code = delete_offer_schedule(schedule_id)

    if error:
        return jsonify({
            "success": False,
            **error
        }), status_code

    return jsonify({
        "success": True,
        "message": "Día de oferta eliminado correctamente"
    }), status_code