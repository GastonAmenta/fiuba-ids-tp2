from src.db import execute, fetch_all, fetch_one, get_connection


# ---------------------------------------------------------------
# GET /canchas  → listar canchas con filtros y paginación
# ---------------------------------------------------------------
def list_courts(filters, limit, offset):
    conditions = []
    params = []
    if filters.get("id_deporte") is not None:
        conditions.append("c.id_deporte = %s")
        params.append(filters["id_deporte"])
    if filters.get("nombre") is not None:
        conditions.append("LOWER(c.nombre) LIKE %s")
        params.append(f"%{filters['nombre'].lower()}%")
    for field in ("techada", "activa"):
        if filters.get(field) is not None:
            conditions.append(f"c.{field} = %s")
            params.append(filters[field])

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""SELECT c.id, c.nombre, c.id_deporte, c.precio_hora,
        c.techada, c.activa FROM canchas c {where}
        ORDER BY c.id LIMIT %s OFFSET %s"""
    rows = fetch_all(query, (*params, limit, offset))
    count = fetch_one(f"SELECT COUNT(*) AS total FROM canchas c {where}", params)
    return rows, count["total"]


# ---------------------------------------------------------------
# GET /canchas/{id}  → obtener una cancha por id
# ---------------------------------------------------------------
def obtener_cancha(id_cancha):
    query = "SELECT * FROM canchas WHERE id = %s"
    return fetch_one(query, (id_cancha,))


# ---------------------------------------------------------------
# True si la cancha tiene al menos una reserva (sin importar estado)
# ---------------------------------------------------------------
def tiene_reservas(id_cancha):
    query = "SELECT 1 FROM reservas WHERE id_cancha = %s LIMIT 1"
    reserva = fetch_one(query, (id_cancha,))
    return reserva is not None


# ---------------------------------------------------------------
# DELETE /canchas/{id}  → eliminar cancha
# La route verifica antes que exista y no tenga reservas.
# ---------------------------------------------------------------
def eliminar_cancha(id_cancha):
    query = "DELETE FROM canchas WHERE id = %s"
    with get_connection() as c, c.cursor() as cur:
        cur.execute(query, (id_cancha,))
        c.commit()


# ---------------------------------------------------------------
# POST /canchas  → crear una cancha
# ---------------------------------------------------------------
def create_court(data):
    court_id = execute(
        """INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
           VALUES (%s, %s, %s, %s, %s)""",
        (
            data["nombre"],
            data["id_deporte"],
            data["precio_hora"],
            data.get("techada", False),
            data.get("activa", True),
        ),
        True,
    )
    return obtener_cancha(court_id)


# ---------------------------------------------------------------
# PATCH /canchas/{id}  → actualizar parcialmente una cancha
# ---------------------------------------------------------------
def update_court(court_id, data):
    assignments = ", ".join(f"{field} = %s" for field in data)
    execute(
        f"UPDATE canchas SET {assignments} WHERE id = %s",
        (*data.values(), court_id),
    )
    return obtener_cancha(court_id)


# ---------------------------------------------------------------
# GET /canchas/disponibles  → canchas activas libres en un intervalo
# Una cancha está libre si no tiene reserva ni bloqueo en el intervalo.
# ---------------------------------------------------------------
def list_available(filters, start, end, limit, offset):
    conditions = [
        "c.activa = TRUE",
        "NOT EXISTS (SELECT 1 FROM reservas r WHERE r.id_cancha = c.id AND r.estado = 'confirmada' AND r.fecha_hora_inicio < %s AND r.fecha_hora_fin > %s)",
        "NOT EXISTS (SELECT 1 FROM bloqueos b WHERE b.id_cancha = c.id AND b.fecha = DATE(%s) AND b.hora_inicio < TIME(%s) AND b.hora_fin > TIME(%s))",
    ]
    params = [end, start, start, end, start]

    if filters.get("id_deporte") is not None:
        conditions.append("c.id_deporte = %s")
        params.append(filters["id_deporte"])
    if filters.get("techada") is not None:
        conditions.append("c.techada = %s")
        params.append(filters["techada"])

    where = " AND ".join(conditions)
    query = f"""SELECT c.id, c.nombre, c.id_deporte, c.precio_hora, c.techada, c.activa
        FROM canchas c WHERE {where}
        ORDER BY c.id LIMIT %s OFFSET %s"""
    rows = fetch_all(query, (*params, limit, offset))
    count = fetch_one(f"SELECT COUNT(*) AS total FROM canchas c WHERE {where}", params)
    return rows, count["total"]