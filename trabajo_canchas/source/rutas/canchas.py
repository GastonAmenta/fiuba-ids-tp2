from flask import Blueprint, jsonify, request
from mysql.connector import Error

from source.servicios.servicio_canchas import crear_cancha, listar_canchas
from source.utiles import (
    limpiar_registros,
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
        return jsonify(respuesta_paginacion("canchas", limpiar_registros(filas), total, limit, offset)), 200
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Parámetros inválidos", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DATOS", "No se pudieron consultar las canchas", "La base de datos no está disponible", 500)


@canchas_bp.route("/canchas", methods=["POST"])
def post_cancha():
    try:
        datos = request.get_json(silent=True)
        cancha_validada = validar_cancha(datos)
        cancha = crear_cancha(datos)
        return jsonify(cancha), 201
    except ValueError as exc:
        return error("ERROR_VALIDACION", "El cuerpo es inválido", str(exc), 400)
    except Error as exc:
        if getattr(exc, "errno", None) == 1452:
            return error("DEPORTE_NO_ENCONTRADO", "Deporte inexistente", "El id_deporte no existe", 404)
        return error("ERROR_BASE_DATOS", "No se pudo crear la cancha", str(exc), 500)
