from flask import Blueprint, jsonify, request
from mysql.connector import Error

from src.services.socios_service import create_member, get_member, list_members, update_member
from src.utils import error, pagination_response, parse_bool, parse_id, parse_pagination, reject_unknown_query
from src.validators.entities import validate_member


socios_bp = Blueprint("socios", __name__)


@socios_bp.route("/socios", methods=["GET"])
def get_socios():
    try:
        reject_unknown_query({"nombre", "activo", "_limit", "_offset"})
        filters = {"nombre": request.args.get("nombre")}
        if "activo" in request.args:
            filters["activo"] = parse_bool(request.args["activo"], "activo")
        limit, offset = parse_pagination()
        rows, total = list_members(filters, limit, offset)
        if not rows:
            return "", 204
        return jsonify(pagination_response("socios", rows, total, limit, offset)), 200
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Parámetros inválidos", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudieron consultar los socios", "La base de datos no está disponible", 500)


@socios_bp.route("/socios", methods=["POST"])
def post_socio():
    try:
        member = create_member(validate_member(request.get_json(silent=True)))
        return jsonify(member), 201
    except ValueError as exc:
        return error("ERROR_VALIDACION", "El cuerpo es inválido", str(exc), 400)
    except Error as exc:
        if getattr(exc, "errno", None) == 1062:
            return error("EMAIL_DUPLICADO", "El email ya está registrado", "No se puede repetir un email", 409)
        return error("ERROR_BASE_DATOS", "No se pudo crear el socio", str(exc), 500)


@socios_bp.route("/socios/<int:member_id>", methods=["GET"])
def get_socio(member_id):
    try:
        member_id = parse_id(member_id)
        member = get_member(member_id)
        if member is None:
            return error("SOCIO_NO_ENCONTRADO", "Socio inexistente", "No existe un socio con ese id", 404)
        return jsonify(member), 200
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Identificador inválido", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudo consultar el socio", "La base de datos no está disponible", 500)


@socios_bp.route("/socios/<int:member_id>", methods=["PATCH"])
def patch_socio(member_id):
    try:
        member_id = parse_id(member_id)
        if get_member(member_id) is None:
            return error("SOCIO_NO_ENCONTRADO", "Socio inexistente", "No existe un socio con ese id", 404)
        data = validate_member(request.get_json(silent=True), partial=True)
        if not data:
            raise ValueError("La actualización debe incluir al menos un campo")
        update_member(member_id, data)
        return "", 204
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Solicitud inválida", str(exc), 400)
    except Error as exc:
        if getattr(exc, "errno", None) == 1062:
            return error("EMAIL_DUPLICADO", "El email ya está registrado", "No se puede repetir un email", 409)
        return error("ERROR_BASE_DATOS", "No se pudo modificar el socio", str(exc), 500)
