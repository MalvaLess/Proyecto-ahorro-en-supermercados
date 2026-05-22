from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.models import db, Offer, OfferSchedule

def validate_day_of_week(day_of_week):
    try:
        day = int(day_of_week)

    except (ValueError, TypeError):
        raise ValueError("dayOfWeek debe ser un número entre 1 y 7")
    
    if day < 1 or day > 7:
        raise ValueError("dayOfWeek debe ser entre 1 y 7")
    
    return day


def get_day_name(day_of_week):
    days = {
        1: "Lunes",
        2: "Martes",
        3: "Miércoles",
        4: "Jueves",
        5: "Viernes",
        6: "Sábado",
        7: "Domingo"
    }

    return days.get(day_of_week)

def offer_schedule_to_dict(schedule):
    return {
        "offerScheduleId": schedule.offerSheduleId,
        "offerId": schedule.offerId,
        "dayOfWeek": schedule.dayOfWeek,
        "dayName": get_day_name(schedule.dayOfWeek)
    }

def get_schedules_by_offer(offer_id):
    offer = db.session.get(Offer, offer_id)

    if offer is None:
        return None, {
            "message": "Oferta no encontrada"
        }, 404

    schedules = OfferSchedule.query.filter_by(
        offerId=offer_id
    ).order_by(
        OfferSchedule.dayOfWeek.asc()
    ).all()

    return schedules, None, 200

def add_schedule_to_offer(offer_id, data):
    offer = db.session.get(Offer, offer_id)

    if offer is None:
        return None, {
            "message": "Oferta no encontrada"
        }, 404

    if offer.offerType != "WEEKLY_DAY":
        return None, {
            "message": "Solo las ofertas WEEKLY_DAY pueden tener días asociados"
        }, 400

    day_of_week = data.get("dayOfWeek")

    if day_of_week is None:
        return None, {
            "message": "dayOfWeek es obligatorio"
        }, 400

    try:
        day = validate_day_of_week(day_of_week)

        existing_schedule = OfferSchedule.query.filter_by(
            offerId=offer_id,
            dayOfWeek=day
        ).first()

        if existing_schedule:
            return None, {
                "message": "La oferta ya tiene asociado ese día"
            }, 409

        schedule = OfferSchedule(
            offerId=offer_id,
            dayOfWeek=day
        )

        db.session.add(schedule)
        db.session.commit()

        return schedule, None, 201

    except ValueError as error:
        db.session.rollback()
        return None, {"message": str(error)}, 400

    except IntegrityError as error:
        db.session.rollback()
        return None, {
            "message": "No se pudo asociar el día a la oferta",
            "details": str(error.orig)
        }, 409

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al asociar día a la oferta",
            "error": str(error)
        }, 500


def replace_offer_schedules(offer_id, data):
    offer = db.session.get(Offer, offer_id)

    if offer is None:
        return None, {
            "message": "Oferta no encontrada"
        }, 404

    if offer.offerType != "WEEKLY_DAY":
        return None, {
            "message": "Solo las ofertas WEEKLY_DAY pueden tener días asociados"
        }, 400

    days_of_week = data.get("daysOfWeek", [])

    if not isinstance(days_of_week, list):
        return None, {
            "message": "daysOfWeek debe ser una lista"
        }, 400

    try:
        clean_days = []

        for day in days_of_week:
            clean_day = validate_day_of_week(day)

            if clean_day not in clean_days:
                clean_days.append(clean_day)

        OfferSchedule.query.filter_by(
            offerId=offer_id
        ).delete(synchronize_session=False)

        for day in clean_days:
            db.session.add(OfferSchedule(
                offerId=offer_id,
                dayOfWeek=day
            ))

        db.session.commit()

        schedules = OfferSchedule.query.filter_by(
            offerId=offer_id
        ).order_by(
            OfferSchedule.dayOfWeek.asc()
        ).all()

        return schedules, None, 200

    except ValueError as error:
        db.session.rollback()
        return None, {"message": str(error)}, 400

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al reemplazar días de la oferta",
            "error": str(error)
        }, 500


def delete_offer_schedule(schedule_id):
    schedule = db.session.get(OfferSchedule, schedule_id)

    if schedule is None:
        return None, {
            "message": "Día de oferta no encontrado"
        }, 404

    try:
        db.session.delete(schedule)
        db.session.commit()

        return schedule, None, 200

    except SQLAlchemyError as error:
        db.session.rollback()
        return None, {
            "message": "Error al eliminar día de oferta",
            "error": str(error)
        }, 500

