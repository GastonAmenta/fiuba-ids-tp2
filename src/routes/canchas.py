from flask import Blueprint, jsonify, request
from mysql.connector import Error

from src.services.canchas_service import (
    create_court,
    eliminar_cancha,
    list_available,
    list_courts,
    obtener_cancha,
    tiene_reservas,
    update_court,
)
from src.utils import (
    clean_records,
    error,
    pagination_response,
    parse_bool,
    parse_date,
    parse_pagination,
    reject_unknown_query,
    validar_id,
)
from src.validators.common import validar_params, validate_interval
from src.validators.entities import validate_court


canchas_bp = Blueprint("canchas", __name__)


# ---------------------------------------------------------------
# Helper interno: arma el dict de filtros desde los query params
# ---------------------------------------------------------------
def _query_filters():
    filters = {}
    if "id_deporte" in request.args:
        filters["id_deporte"] = validar_id(request.args["id_deporte"], "id_deporte")
    if "nombre" in request.args:
        filters["nombre"] = request.args["nombre"]
    for field in ("techada", "activa"):
        if field in request.args:
            filters[field] = parse_bool(request.args[field], field)
    return filters


# ---------------------------------------------------------------
# GET /canchas  → listar canchas con filtros y paginación
# ---------------------------------------------------------------
@canchas_bp.route("/canchas", methods=["GET"])
def get_canchas():
    try:
        reject_unknown_query({"id_deporte", "nombre", "techada", "activa", "_limit", "_offset"})
        filters = _query_filters()
        limit, offset = parse_pagination()
        rows, total = list_courts(filters, limit, offset)
        if not rows:
            return "", 204
        return jsonify(pagination_response("canchas", clean_records(rows), total, limit, offset)), 200
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Parámetros inválidos", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudieron consultar las canchas", "La base de datos no está disponible", 500)


# ---------------------------------------------------------------
# POST /canchas  → crear una cancha
# ---------------------------------------------------------------
@canchas_bp.route("/canchas", methods=["POST"])
def post_cancha():
    try:
        data = validate_court(request.get_json(silent=True))
        court = create_court(data)
        return jsonify(court), 201
    except ValueError as exc:
        return error("ERROR_VALIDACION", "El cuerpo es inválido", str(exc), 400)
    except Error as exc:
        if getattr(exc, "errno", None) == 1452:
            return error("DEPORTE_NO_ENCONTRADO", "Deporte inexistente", "El id_deporte no existe", 404)
        return error("ERROR_BASE_DATOS", "No se pudo crear la cancha", str(exc), 500)


# ---------------------------------------------------------------
# GET /canchas/disponibles  → canchas activas libres en un intervalo
# ---------------------------------------------------------------
@canchas_bp.route("/canchas/disponibles", methods=["GET"])
def get_disponibles():
    try:
        reject_unknown_query({"fecha", "hora_inicio", "hora_fin", "id_deporte", "techada", "_limit", "_offset"})
        required = ("fecha", "hora_inicio", "hora_fin")
        if any(field not in request.args for field in required):
            raise ValueError("fecha, hora_inicio y hora_fin son obligatorios")

        day = parse_date(request.args["fecha"])
        start, end, _duration = validate_interval(
            f"{day.isoformat()}T{request.args['hora_inicio']}.000000-03:00",
            f"{day.isoformat()}T{request.args['hora_fin']}.000000-03:00",
        )

        filters = _query_filters()
        limit, offset = parse_pagination()
        rows, total = list_available(filters, start, end, limit, offset)

        if not rows:
            return "", 204
        return jsonify(pagination_response("canchas", clean_records(rows), total, limit, offset)), 200
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Parámetros inválidos", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudo consultar la disponibilidad", "La base de datos no está disponible", 500)


# ---------------------------------------------------------------
# GET /canchas/<id>  → obtener una cancha por id
# ---------------------------------------------------------------
@canchas_bp.route("/canchas/<id_cancha>", methods=["GET"])
def obtener_canchas_por_id(id_cancha):
    try:
        validar_params(request.args)
        id_cancha = validar_id(id_cancha)
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Identificador inválido", str(exc), 400)

    cancha = obtener_cancha(id_cancha)
    if cancha is None:
        return error("CANCHA_NO_ENCONTRADA", "Cancha inexistente", "No existe una cancha con ese id", 404)

    return jsonify(cancha)


# ---------------------------------------------------------------
# PATCH /canchas/<id>  → actualizar parcialmente una cancha
# ---------------------------------------------------------------
@canchas_bp.route("/canchas/<int:court_id>", methods=["PATCH"])
def patch_cancha(court_id):
    try:
        court_id = validar_id(court_id)
        if obtener_cancha(court_id) is None:
            return error("CANCHA_NO_ENCONTRADA", "Cancha inexistente", "No existe una cancha con ese id", 404)

        data = validate_court(request.get_json(silent=True), partial=True)
        if not data:
            raise ValueError("La actualización debe incluir al menos un campo")

        updated = update_court(court_id, data)
        return jsonify(updated), 204
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Solicitud inválida", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudo modificar la cancha", "La base de datos no está disponible", 500)


# ---------------------------------------------------------------
# DELETE /canchas/<id>  → eliminar una cancha sin reservas
# ---------------------------------------------------------------
@canchas_bp.route("/canchas/<id_cancha>", methods=["DELETE"])
def eliminar_cancha_por_id(id_cancha):
    try:
        validar_params(request.args)
        id_cancha = validar_id(id_cancha)
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Identificador inválido", str(exc), 400)

    if obtener_cancha(id_cancha) is None:
        return error("CANCHA_NO_ENCONTRADA", "Cancha inexistente", "No existe una cancha con ese id", 404)

    if tiene_reservas(id_cancha):
        return error(
            "CANCHA_CON_RESERVAS",
            "La cancha tiene reservas",
            "No se puede eliminar una cancha con reservas, puede desactivarse mediante PATCH",
            409,
        )

    eliminar_cancha(id_cancha)
    return "", 204