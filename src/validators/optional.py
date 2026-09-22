from datetime import datetime, time
import re

from src.utils import now_gmt_minus_3, parse_date
from src.validators.common import reject_unknown_fields, require_fields, require_json_object, validate_positive_integer, validate_text


def validate_block(data):
    # Un bloqueo puede durar toda la jornada y no usa el limite de 3 horas.
    require_json_object(data)
    reject_unknown_fields(data, {"id_cancha", "fecha", "hora_inicio", "hora_fin", "motivo"})
    require_fields(data, {"id_cancha", "fecha", "hora_inicio", "hora_fin", "motivo"})
    court_id = validate_positive_integer(data["id_cancha"], "id_cancha")
    day = parse_date(data["fecha"])
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):00:00", str(data["hora_inicio"])) or not re.fullmatch(r"(?:[01]\d|2[0-3]):00:00", str(data["hora_fin"])):
        raise ValueError("Las horas deben tener formato HH:00:00")
    try:
        start = time.fromisoformat(data["hora_inicio"])
        end = time.fromisoformat(data["hora_fin"])
    except (TypeError, ValueError) as exc:
        raise ValueError("Las horas deben tener formato HH:MM:SS") from exc
    if start.minute or start.second or end.minute or end.second or start >= end:
        raise ValueError("El bloqueo debe usar horas en punto y tener inicio anterior al fin")
    if start < time(8) or end > time(23):
        raise ValueError("El bloqueo debe estar entre las 08:00 y las 23:00")
    if datetime.combine(day, start) <= now_gmt_minus_3():
        raise ValueError("El bloqueo debe comenzar en el futuro")
    return {"id_cancha": court_id, "fecha": day, "hora_inicio": start, "hora_fin": end, "motivo": validate_text(data["motivo"], "motivo")}


def validate_recurring(data):
    require_json_object(data)
    reject_unknown_fields(data, {"id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin", "cantidad_semanas"})
    require_fields(data, {"id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin", "cantidad_semanas"})
    weeks = data["cantidad_semanas"]
    if isinstance(weeks, bool) or not isinstance(weeks, int) or not 2 <= weeks <= 12:
        raise ValueError("cantidad_semanas debe ser un entero entre 2 y 12")
    return data, weeks