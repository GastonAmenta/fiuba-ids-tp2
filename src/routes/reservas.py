from datetime import timedelta

from flask import Blueprint, jsonify, request
from mysql.connector import Error

from src.constants import RESERVATION_STATES
from src.services.reservas_service import (
    count_reservations,
    create_reservation,
    create_reservations_transaction,
    find_court,
    find_member,
    obtener_reserva,
    has_overlap,
    reservation_query,
    actualizar_estado,
)
from src.services.bloqueos_service import block_overlaps
from src.utils import clean_record, clean_records, error, now_gmt_minus_3, pagination_response, parse_date, validar_id as parse_id , parse_pagination, reject_unknown_query
from src.validators.common import require_json_object, reject_unknown_fields
from src.validators.entities import validate_reservation
from src.validators.optional import validate_recurring
from src.validators.reservas import (
    validar_cuerpo_estado,
    validar_existencia_reserva,
    validar_id_reserva,
    validar_transicion_estado,
)


reservas_bp = Blueprint("reservas", __name__)


@reservas_bp.route("/reservas", methods=["GET"])
def get_reservas():
    try:
        reject_unknown_query({"id_cancha", "id_socio", "estado", "fecha_desde", "fecha_hasta", "_limit", "_offset"})
        conditions = []
        params = []
        for field, column in (("id_cancha", "id_cancha"), ("id_socio", "id_socio")):
            if field in request.args:
                conditions.append(f"{column} = %s")
                params.append(parse_id(request.args[field], field))
        if "estado" in request.args:
            if request.args["estado"] not in RESERVATION_STATES:
                raise ValueError("estado no válido")
            conditions.append("estado = %s")
            params.append(request.args["estado"])
        for field, operator in (("fecha_desde", ">="), ("fecha_hasta", "<=")):
            if field in request.args:
                conditions.append(f"DATE(fecha_hora_inicio) {operator} %s")
                params.append(parse_date(request.args[field], field))
        if "fecha_desde" in request.args and "fecha_hasta" in request.args and request.args["fecha_desde"] > request.args["fecha_hasta"]:
            raise ValueError("fecha_desde no puede ser posterior a fecha_hasta")
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        limit, offset = parse_pagination()
        rows = reservation_query(where, params, limit, offset)
        total = count_reservations(where, params)
        if not rows:
            return "", 204
        return jsonify(pagination_response("reservas", clean_records(rows), total, limit, offset)), 200
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Parámetros inválidos", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudieron consultar las reservas", "La base de datos no está disponible", 500)


@reservas_bp.route("/reservas", methods=["POST"])
def post_reserva():
    try:
        # Se valida otra vez antes de insertar: consultar disponibilidad no reserva.
        member_id, court_id, start, end, duration = validate_reservation(request.get_json(silent=True))
        member = find_member(member_id)
        court = find_court(court_id)
        if member is None or court is None:
            return error("REFERENCIA_NO_ENCONTRADA", "Referencia inexistente", "El socio o la cancha no existen", 404)
        if not member["activo"] or not court["activa"]:
            return error("ENTIDAD_INACTIVA", "Entidad inactiva", "El socio y la cancha deben estar activos", 409)
        if (has_overlap("id_cancha", court_id, start, end)
            or has_overlap("id_socio", member_id, start, end)
            or block_overlaps(court_id, start.date(), start.time(), end.time())):
            return error("SUPERPOSICION", "Horario no disponible", "Existe una reserva confirmada superpuesta", 409)
        price = court["precio_hora"]
        return jsonify(clean_record(create_reservation(member_id, court_id, start, end, price, duration * price))), 201
    except ValueError as exc:
        return error("ERROR_VALIDACION", "El cuerpo es inválido", str(exc), 400)
    except Error as exc:
        return error("ERROR_BASE_DATOS", "No se pudo crear la reserva", str(exc), 500)


@reservas_bp.route("/reservas/<int:reservation_id>", methods=["GET"])
def get_reserva(reservation_id):
    try:
        id_reserva = validar_id_reserva(reservation_id)
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Identificador inválido", str(exc), 400)

    reserva = obtener_reserva(id_reserva)

    if reserva is None:
        return error("RESERVA_NO_ENCONTRADA", "Reserva inexistente", "No existe una reserva con ese id", 404)

    return jsonify(clean_record(reserva)), 200


@reservas_bp.route("/reservas/<int:reservation_id>/estado", methods=["PUT"])
def put_estado(reservation_id):
    try:
        id_reserva = validar_id_reserva(reservation_id)
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Identificador inválido", str(exc), 400)

    reserva = obtener_reserva(id_reserva)

    if reserva is None:
        return error("RESERVA_NO_ENCONTRADA", "Reserva inexistente", "No existe una reserva con ese id", 404)

    data = request.get_json(silent=True)

    try:
        estado_solicitado = validar_cuerpo_estado(data)
    except ValueError as exc:
        return error("ESTADO_INVALIDO", "Estado desconocido", str(exc), 400)

    try:
        resultado_transicion = validar_transicion_estado(reserva, estado_solicitado)
    except ValueError as exc:
        return error("TRANSICION_INVALIDA", "Transición no permitida", str(exc), 409)

    if resultado_transicion is not None:
        return resultado_transicion

    try:
        actualizar_estado(id_reserva, estado_solicitado)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudo actualizar el estado", "La base de datos no está disponible", 500)

    return "", 204


@reservas_bp.route("/reservas/recurrentes", methods=["POST"])
def post_reservas_recurrentes():
    try:
        raw_data, weeks = validate_recurring(request.get_json(silent=True))
        reservation_data = dict(raw_data)
        reservation_data.pop("cantidad_semanas")
        member_id, court_id, start, end, duration = validate_reservation(reservation_data)
        member = find_member(member_id)
        court = find_court(court_id)
        if member is None or court is None:
            return error("REFERENCIA_NO_ENCONTRADA", "Referencia inexistente", "El socio o la cancha no existen", 404)
        if not member["activo"] or not court["activa"]:
            return error("ENTIDAD_INACTIVA", "Entidad inactiva", "El socio y la cancha deben estar activos", 409)

        price = court["precio_hora"]
        reservations = []
        conflicts = []
        for week in range(weeks):
            week_start = start + timedelta(weeks=week)
            week_end = end + timedelta(weeks=week)
            if (has_overlap("id_cancha", court_id, week_start, week_end)
                    or has_overlap("id_socio", member_id, week_start, week_end)
                    or block_overlaps(court_id, week_start.date(), week_start.time(), week_end.time())):
                conflicts.append(week_start.date().isoformat())
            reservations.append((member_id, court_id, week_start, week_end, price, duration * price))
        if conflicts:
            return jsonify({
                "errors": [{
                    "code": "SUPERPOSICION",
                    "message": "Hay fechas no disponibles",
                    "level": "error",
                    "description": "Una o más reservas de la serie se superponen"
                }],
                "conflictos": conflicts
            }), 409
        created = create_reservations_transaction(reservations)
        return jsonify(clean_records(created)), 201
    except ValueError as exc:
        return error("ERROR_VALIDACION", "El cuerpo es inválido", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudo crear la serie", "La base de datos no está disponible", 500)