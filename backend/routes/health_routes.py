from flask import Blueprint 
from sqlalchemy import text
from models.models import db

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    return {
        "success": True,
        "message": "API Funcionando Correctamente"
    }, 200

@health_bp.route("/db", methods=["GET"])
def database_check():
    try: 
        db.session.execute(text("SELECT 1"))
        return {
            "success": True,
            "message": "Conexión a Postgres Exitosa"
        }, 200
    except:
        return {
            "success": False,
            "message": "Error al Conectar con PostgreSQL"
        }, 500