from datetime import datetime

from src.constants import (
    CLUB_CLOSING_HOUR,
    CLUB_OPENING_HOUR,
    MAX_RESERVATION_HOURS,
    MIN_RESERVATION_HOURS,
)
from src.utils import now_gmt_minus_3, parse_iso_datetime


def require_json_object(data):
    if not isinstance(data, dict) or not data:
        raise ValueError("El cuerpo debe ser un objeto JSON no vacío")


def reject_unknown_fields(data, allowed):
    unknown = set(data) - set(allowed)
    if unknown:
        raise ValueError(f"Campos desconocidos: {', '.join(sorted(unknown))}")


def require_fields(data, fields):
    missing = [field for field in fields if field not in data]
    if missing:
        raise ValueError(f"Faltan campos obligatorios: {', '.join(missing)}")


def validate_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"El campo '{field}' no puede estar vacío")
    return value.strip()


def validate_positive_integer(value, field):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"El campo '{field}' debe ser un entero positivo")
    return value


def validate_boolean(value, field):
    if not isinstance(value, bool):
        raise ValueError(f"El campo '{field}' debe ser booleano")
    return value


def validate_interval(start_text, end_text):
    # Todas las reglas de horario de reservas se concentran aqui.
    start = parse_iso_datetime(start_text)
    end = parse_iso_datetime(end_text)
    if start >= end:
        raise ValueError("La fecha_hora_inicio debe ser anterior a fecha_hora_fin")
    if start <= now_gmt_minus_3():
        raise ValueError("El inicio de la reserva debe ser posterior al momento actual")
    if start.date() != end.date():
        raise ValueError("La reserva no puede atravesar la medianoche")
    if start.minute or start.second or start.microsecond or end.minute or end.second or end.microsecond:
        raise ValueError("El intervalo debe comenzar y terminar en horas en punto")
    duration = int((end - start).total_seconds() // 3600)
    if not MIN_RESERVATION_HOURS <= duration <= MAX_RESERVATION_HOURS:
        raise ValueError("La reserva debe durar entre 1 y 3 horas")
    if start.hour < CLUB_OPENING_HOUR or end.hour > CLUB_CLOSING_HOUR:
        raise ValueError("El intervalo debe estar entre las 08:00 y las 23:00")
    return start, end, duration
