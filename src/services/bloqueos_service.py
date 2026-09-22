from src.db import execute, fetch_all, fetch_one


def list_blocks(filters, limit, offset):
    conditions = []
    params = []
    if filters.get("id_cancha") is not None:
        conditions.append("id_cancha = %s")
        params.append(filters["id_cancha"])
    if filters.get("fecha") is not None:
        conditions.append("fecha = %s")
        params.append(filters["fecha"])
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    rows = fetch_all(f"""SELECT id, id_cancha, fecha, hora_inicio, hora_fin, motivo
        FROM bloqueos {where} ORDER BY id LIMIT %s OFFSET %s""", (*params, limit, offset))
    total = fetch_one(f"SELECT COUNT(*) AS total FROM bloqueos {where}", params)["total"]
    return rows, total


def get_block(block_id):
    return fetch_one("""SELECT id, id_cancha, fecha, hora_inicio, hora_fin, motivo
        FROM bloqueos WHERE id = %s""", (block_id,))


def create_block(data):
    block_id = execute("""INSERT INTO bloqueos
        (id_cancha, fecha, hora_inicio, hora_fin, motivo)
        VALUES (%s, %s, %s, %s, %s)""", (data["id_cancha"], data["fecha"], data["hora_inicio"], data["hora_fin"], data["motivo"]), True)
    return get_block(block_id)


def delete_block(block_id):
    return execute("DELETE FROM bloqueos WHERE id = %s", (block_id,))


def block_overlaps(court_id, date_value, start, end):
    return fetch_one("""SELECT id FROM bloqueos
        WHERE id_cancha = %s AND fecha = %s
        AND hora_inicio < %s AND hora_fin > %s LIMIT 1""", (court_id, date_value, end, start)) is not None


def reservation_overlaps(court_id, date_value, start, end):
    return fetch_one("""SELECT id FROM reservas
        WHERE id_cancha = %s AND DATE(fecha_hora_inicio) = %s
        AND estado = 'confirmada'
        AND TIME(fecha_hora_inicio) < %s AND TIME(fecha_hora_fin) > %s
        LIMIT 1""", (court_id, date_value, end, start)) is not None