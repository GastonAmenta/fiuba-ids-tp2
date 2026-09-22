from datetime import date, datetime, time, timedelta
from urllib.parse import urlencode

from flask import request

from src.constants import DEFAULT_LIMIT, GMT_MINUS_3, MAX_LIMIT


def error(code, message, description, status):
	body = {"errors": [{
		"code": code,
		"message": message,
		"level": "error",
		"description": description,
	}]}
	return body, status


def parse_id(value, field="id"):
	try:
		number = int(value)
	except (TypeError, ValueError):
		raise ValueError(f"El campo '{field}' debe ser un entero positivo")
	if number <= 0:
		raise ValueError(f"El campo '{field}' debe ser un entero positivo")
	return number


def parse_bool(value, field):
	if value not in ("true", "false"):
		raise ValueError(f"El parámetro '{field}' debe ser true o false")
	return value == "true"


def parse_pagination():
	try:
		limit = int(request.args.get("_limit", DEFAULT_LIMIT))
		offset = int(request.args.get("_offset", 0))
	except ValueError as exc:
		raise ValueError("_limit y _offset deben ser enteros") from exc
	if not 1 <= limit <= MAX_LIMIT:
		raise ValueError("_limit debe estar entre 1 y 100")
	if offset < 0:
		raise ValueError("_offset debe ser mayor o igual a cero")
	return limit, offset


def reject_unknown_query(allowed):
	unknown = set(request.args) - set(allowed)
	if unknown:
		raise ValueError(f"Parámetros desconocidos: {', '.join(sorted(unknown))}")


def pagination_response(key, items, total, limit, offset):
	# Los enlaces conservan los filtros y cambian solamente el offset.
	base = request.base_url
	query = request.args.to_dict()
	last_offset = (max(total - 1, 0) // limit) * limit

	def link(page_offset):
		params = dict(query)
		params["_limit"] = limit
		params["_offset"] = page_offset
		return {"href": f"{base}?{urlencode(params)}"}

	links = {
		"_first": link(0),
		"_prev": link(max(offset - limit, 0)),
		"_next": link(offset + limit),
		"_last": link(last_offset),
	}
	if offset == 0:
		links["_prev"] = None
	if offset + limit >= total:
		links["_next"] = None
	return {key: items, "_links": links}


def parse_iso_datetime(value):
	# Se exige el formato exacto del contrato: seis decimales y -03:00.
	if not isinstance(value, str):
		raise ValueError("La fecha debe ser un texto ISO 8601")
	try:
		return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f-03:00")
	except ValueError as exc:
		raise ValueError("La fecha debe tener formato ISO 8601 GMT-3 con 6 decimales") from exc


def parse_date(value, field="fecha"):
	try:
		return date.fromisoformat(value)
	except (TypeError, ValueError) as exc:
		raise ValueError(f"El campo '{field}' debe tener formato YYYY-MM-DD") from exc


def serialize_datetime(value):
	return value.strftime("%Y-%m-%dT%H:%M:%S.%f-03:00")


def now_gmt_minus_3():
	return datetime.now(GMT_MINUS_3).replace(tzinfo=None)


def clean_record(record):
	if not record:
		return record
	result = dict(record)
	# MySQL devuelve date/time; Flask necesita valores serializables a JSON.
	for key, value in result.items():
		if isinstance(value, datetime):
			result[key] = serialize_datetime(value)
		elif isinstance(value, date):
			result[key] = value.isoformat()
		elif isinstance(value, time):
			result[key] = value.strftime("%H:%M:%S")
		elif isinstance(value, timedelta):
			total_seconds = int(value.total_seconds())
			result[key] = f"{total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}:{total_seconds % 60:02d}"
	return result


def clean_records(records):
	return [clean_record(record) for record in records]
