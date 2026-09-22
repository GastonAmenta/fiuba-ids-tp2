from flask import Blueprint, jsonify
from mysql.connector import Error

from src.services.deportes_service import list_sports


deportes_bp = Blueprint("deportes", __name__)


@deportes_bp.route("/deportes", methods=["GET"])
def get_deportes():
    try:
        sports = list_sports()
        if not sports:
            return "", 204
        return jsonify({"deportes": sports}), 200
    except Error:
        return jsonify({"errors": [{
            "code": "ERROR_BASE_DATOS",
            "message": "No se pudieron consultar los deportes",
            "level": "error",
            "description": "La base de datos no está disponible"
        }]}), 500
