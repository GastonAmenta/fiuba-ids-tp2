from flask import Blueprint, jsonify, request
from mysql.connector import Error

from source.servicios.servicios_canchas import crear_cancha, listar_canchas, obtener_cancha, eliminar_cancha,tiene_reservas
from source.utiles import (
    limpiar_historiales,
    error,
    respuesta_paginacion,
    analisis_bool,
    analisis_id,
    analisis_paginacion,
    rechazar_query_desconocida,
)
from source.validators.comunes import validar_intervalo
from source.validators.entidades import validar_cancha


canchas_bp = Blueprint("canchas", __name__)


def _consulta_filtros():
    filtros = {}
    if "id_deporte" in request.args:
        filtros["id_deporte"] = analisis_id(request.args["id_deporte"], "id_deporte")
    if "nombre" in request.args:
        filtros["nombre"] = request.args["nombre"]
    for campo in ("techada", "activa"):
        if campo in request.args:
            filtros[campo] = analisis_bool(request.args[campo], campo)
    return filtros


@canchas_bp.route("/canchas", methods=["GET"])
def get_canchas():
    try:
        rechazar_query_desconocida({"id_deporte", "nombre", "techada", "activa", "_limit", "_offset"})
        filtros = _consulta_filtros()
        limit, offset = analisis_paginacion()
        filas, total = listar_canchas(filtros, limit, offset)
        if not filas:
            return "", 204
        return jsonify(respuesta_paginacion("canchas", limpiar_historiales(filas), total, limit, offset)), 200
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Parámetros inválidos", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudieron consultar las canchas", "La base de datos no está disponible", 500)


@canchas_bp.route("/canchas", methods=["POST"])
def post_cancha():
    try:
        datos = request.get_json(silent=True)
        cancha_validada = validar_cancha(datos)
        cancha = crear_cancha(cancha_validada)
        return jsonify(cancha), 201
    except ValueError as exc:
        return error("ERROR_VALIDACION", "El cuerpo es inválido", str(exc), 400)
    except Error as exc:
        if getattr(exc, "errno", None) == 1452:
            return error("DEPORTE_NO_ENCONTRADO", "Deporte inexistente", "El id_deporte no existe", 404)
        return error("ERROR_BASE_DATOS", "No se pudo crear la cancha", str(exc), 500)

@canchas_bp.route("/canchas/<id_cancha>", methods=["GET"])
def obtener_canchas_por_id(id_cancha):

    rechazar_query_desconocida(request.args)
    try:
        id_cancha = analisis_id(id_cancha)
    except ValueError as exc:
        return error("ERROR_VALIDACION", "id invalido", str(exc), 400)

    cancha = obtener_cancha(id_cancha)
    if cancha is None:
            return error("CANCHA_NO_ENCONTRADA", "Cancha inexistente", "no existe una cancha con ese id", 404)

    return jsonify(cancha)


@canchas_bp.route("/canchas/<id_cancha>", methods=["DELETE"])
def eliminar_cancha_por_id(id_cancha):

    rechazar_query_desconocida(request.args)
    try:
        id_cancha = analisis_id(id_cancha)
    except ValueError as exc:
        return error("ERROR_VALIDACION", "id invalido", str(exc), 400)

    if obtener_cancha(id_cancha) is None:
        return error("CANCHA_NO_ENCONTRADA", "Cancha inexistente", "no existe una cancha con ese id", 404)

    if tiene_reservas(id_cancha):
        return error("CANCHA_CON_RESERVAS", "La cancha tiene reservas", "no se puede eliminar una cancha con reservas,desactivarla mediante PATCH", 409)

    
    eliminar_cancha(id_cancha)
    return "", 204
