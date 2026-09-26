from flask import Blueprint, jsonify, request
from mysql.connector import Error

from source.servicios.servicios_socios import crear_socio, listar_socios
from source.utiles import error, respuesta_paginacion, analisis_bool, analisis_paginacion, rechazar_query_desconocida
from source.validators.entidades import validar_socio

socios_bp = Blueprint("socios", __name__)

@socios_bp.route("/socios", methods=["GET"])
def get_socios():
    try:
        rechazar_query_desconocida({"nombre", "activo", "_limit", "_offset"})
        filtros = {"nombre": request.args.get("nombre")}
        if "activo" in request.args:
            filtros["activo"] = analisis_bool(request.args.get("activo"), "activo")
        limit, offset = analisis_paginacion()
        filas, total = listar_socios(filtros, limit, offset)
        if not filas:
            return "", 204
        
        # Corregido: se eliminaron las llaves {} que envolvían el diccionario
        return jsonify(respuesta_paginacion("socios", filas, total, limit, offset)), 200
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Parámetros inválidos", str(exc), 400)
    except Error:
        return error("ERROR_BASE_DE_DATOS", "No se pudo consultar socios", "base de datos no disponible", 500)

@socios_bp.route("/socios", methods=["POST"])
def post_socio():
    try:
        # Corregido: silent con 's' minúscula
        datos = request.get_json(silent=True)
        socio_validado = validar_socio(datos)
        socio = crear_socio(socio_validado)
        return jsonify(socio), 201
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Datos inválidos", str(exc), 400)
    except Error as exc:
        if getattr(exc, "errno", None) == 1062:
            return error("ERROR_DUPLICADO", "El email ya existe", "El email proporcionado ya está registrado", 409)
        return error("ERROR_BASE_DE_DATOS", "No se pudo crear socio", str(exc), 500)