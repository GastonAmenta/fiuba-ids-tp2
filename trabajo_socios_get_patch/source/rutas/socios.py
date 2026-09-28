from flask import Blueprint, jsonify, request
from mysql.connector import Error

from src.utils import error

from source.servicios.servicios_socios import obtener_socio_id, actualizar_socio
from source.validators.entidades import validar_socio

socios_bp = Blueprint("socios", __name__)

@socios_bp.route("/socios/<int:socio_id>", methods=["GET"])
def get_socio(socio_id):
    try:
        socio = obtener_socio_id(socio_id)
        
        if not socio:
            return error("NO_ENCONTRADO", "Socio no encontrado", f"No existe un socio con el ID {socio_id}", 404)
            
        return jsonify(socio), 200
        
    except Error:
        return error("ERROR_BASE_DE_DATOS", "No se pudo consultar el socio", "Base de datos no disponible", 500)

@socios_bp.route("/socios/<int:socio_id>", methods=["PATCH"])
def patch_socio(socio_id):
    try:
        datos = request.get_json(silent=True)
        datos_validados = validar_socio(datos, parcial=True)
        
        if not datos_validados:
            return error("ERROR_VALIDACION", "Datos inválidos", "No se proporcionaron campos para actualizar", 400)
            
        socio_existente = obtener_socio_id(socio_id)
        if not socio_existente:
            return error("NO_ENCONTRADO", "Socio no encontrado", f"No existe un socio con el ID {socio_id}", 404)
            
        socio_actualizado = actualizar_socio(socio_id, datos_validados)
        
        return jsonify(socio_actualizado), 200
        
    except ValueError as exc:
        return error("ERROR_VALIDACION", "Datos inválidos", str(exc), 400)
    except Error as exc:
        if getattr(exc, "errno", None) == 1062:
            return error("ERROR_DUPLICADO", "El email ya existe", "El email proporcionado ya está registrado por otro socio", 409)
        return error("ERROR_BASE_DE_DATOS", "No se pudo actualizar el socio", str(exc), 500)