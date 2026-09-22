from flask import Blueprint, jsonify, request
from mysql.connector import Error

from src.services.bloqueos_service import (
    block_overlaps,
    create_block,
    delete_block,
    get_block,
    list_blocks,
    reservation_overlaps,
)
from src.services.canchas_service import get_court
from src.utils import clean_record, clean_records, error, pagination_response, parse_date, parse_id, parse_pagination, reject_unknown_query
from src.validators.optional import validate_block


bloqueos_bp = Blueprint("bloqueos", __name__)


@bloqueos_bp.route("/bloqueos", methods=["GET"])
def get_bloqueos():
    try:
        reject_unknown_query({"id_cancha", "fecha", "_limit", "_offset"})
        filters = {}
        if "id_cancha" in request.args:
            filters["id_cancha"] = parse_id(request.args["id_cancha"], "id_cancha")
        if "fecha" in request.args:
            filters["fecha"] = parse_date(request.args["fecha"])
        limit, offset = parse_pagination()
        rows, total = list_blocks(filters, limit, offset)
        if not rows:
            return "", 204
        return jsonify(pagination_response("bloqueos", clean_records(rows), total, limit, offset)), 200
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Parámetros inválidos", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudieron consultar los bloqueos", "La base de datos no está disponible", 500)


@bloqueos_bp.route("/bloqueos", methods=["POST"])
def post_bloqueo():
    try:
        # Un bloqueo no puede ocupar un horario ya usado.
        data = validate_block(request.get_json(silent=True))
        if get_court(data["id_cancha"]) is None:
            return error("CANCHA_NO_ENCONTRADA", "Cancha inexistente", "No existe la cancha indicada", 404)
        if block_overlaps(data["id_cancha"], data["fecha"], data["hora_inicio"], data["hora_fin"]):
            return error("SUPERPOSICION", "Bloqueo superpuesto", "Ya existe otro bloqueo en ese intervalo", 409)
        if reservation_overlaps(data["id_cancha"], data["fecha"], data["hora_inicio"], data["hora_fin"]):
            return error("SUPERPOSICION", "Bloqueo superpuesto", "Existe una reserva confirmada en ese intervalo", 409)
        return jsonify(clean_record(create_block(data))), 201
    except ValueError as exc:
        return error("ERROR_VALIDACION", "El cuerpo es inválido", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudo crear el bloqueo", "La base de datos no está disponible", 500)


@bloqueos_bp.route("/bloqueos/<int:block_id>", methods=["DELETE"])
def delete_bloqueo(block_id):
    try:
        block_id = parse_id(block_id)
        if get_block(block_id) is None:
            return error("BLOQUEO_NO_ENCONTRADO", "Bloqueo inexistente", "No existe un bloqueo con ese id", 404)
        delete_block(block_id)
        return "", 204
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Identificador inválido", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudo eliminar el bloqueo", "La base de datos no está disponible", 500)