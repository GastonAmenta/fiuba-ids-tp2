import re

from src.validators.common import (
    reject_unknown_fields,
    require_fields,
    require_json_object,
    validate_boolean,
    validate_positive_integer,
    validate_text,
)

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_court(data, partial=False):
    require_json_object(data)
    allowed = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
    reject_unknown_fields(data, allowed)
    if not partial:
        require_fields(data, {"nombre", "id_deporte", "precio_hora"})
    result = {}
    if "nombre" in data:
        result["nombre"] = validate_text(data["nombre"], "nombre")
    if "id_deporte" in data:
        result["id_deporte"] = validate_positive_integer(data["id_deporte"], "id_deporte")
    if "precio_hora" in data:
        result["precio_hora"] = validate_positive_integer(data["precio_hora"], "precio_hora")
    if "techada" in data:
        result["techada"] = validate_boolean(data["techada"], "techada")
    if "activa" in data:
        result["activa"] = validate_boolean(data["activa"], "activa")
    return result


def validate_member(data, partial=False):
    require_json_object(data)
    allowed = {"nombre", "email", "activo"}
    reject_unknown_fields(data, allowed)
    if not partial:
        require_fields(data, {"nombre", "email"})
    result = {}
    if "nombre" in data:
        result["nombre"] = validate_text(data["nombre"], "nombre")
    if "email" in data:
        email = validate_text(data["email"], "email").lower()
        if not EMAIL_PATTERN.fullmatch(email):
            raise ValueError("El campo 'email' no tiene un formato válido")
        result["email"] = email
    if "activo" in data:
        result["activo"] = validate_boolean(data["activo"], "activo")
    return result


def validate_reservation(data):
    require_json_object(data)
    reject_unknown_fields(data, {"id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin"})
    require_fields(data, {"id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin"})
    member_id = validate_positive_integer(data["id_socio"], "id_socio")
    court_id = validate_positive_integer(data["id_cancha"], "id_cancha")
    from src.validators.common import validate_interval
    start, end, duration = validate_interval(data["fecha_hora_inicio"], data["fecha_hora_fin"])
    return member_id, court_id, start, end, duration
