import re
from source.validators.comunes import (
    rechazar_campos_desconocidos,
    campos_requeridos,
    requiere_objeto_json,
    validar_booleano,
    validar_int_positivo,
    validar_texto,
)

PATRON_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def validar_cancha(data, parcial=False):
    requiere_objeto_json(data)
    permitidos = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
    rechazar_campos_desconocidos(data, permitidos)
    if not parcial:
        campos_requeridos(data, {"nombre", "id_deporte", "precio_hora"})
    resultado = {}
    if "nombre" in data:
        resultado["nombre"] = validar_texto(data["nombre"], "nombre")
    if "id_deporte" in data:
        resultado["id_deporte"] = validar_int_positivo(data["id_deporte"], "id_deporte")
    if "precio_hora" in data:
        resultado["precio_hora"] = validar_int_positivo(data["precio_hora"], "precio_hora")
    if "techada" in data:
        resultado["techada"] = validar_booleano(data["techada"], "techada")
    if "activa" in data:
        resultado["activa"] = validar_booleano(data["activa"], "activa")
    return resultado