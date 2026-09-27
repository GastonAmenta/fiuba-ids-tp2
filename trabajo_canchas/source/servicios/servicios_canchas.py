from source.db import execute, fetch_all, fetch_one


def listar_canchas(filtros, limit, offset):
    condiciones = []
    parametros = []
    if filtros.get("id_deporte") is not None:
        condiciones.append("c.id_deporte = %s")
        parametros.append(filtros["id_deporte"])
    if filtros.get("nombre") is not None:
        condiciones.append("LOWER(c.nombre) LIKE %s")
        parametros.append(f"%{filtros['nombre'].lower()}%")
    for field in ("techada", "activa"):
        if filtros.get(field) is not None:
            condiciones.append(f"c.{field} = %s")
            parametros.append(filtros[field])
    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    query = f"""SELECT c.id, c.nombre, c.id_deporte, c.precio_hora,
        c.techada, c.activa FROM canchas c {where}
        ORDER BY c.id LIMIT %s OFFSET %s"""
    filas = fetch_all(query, (*parametros, limit, offset))
    conteo = fetch_one(f"SELECT COUNT(*) AS total FROM canchas c {where}", parametros)
    return filas, conteo["total"]

def crear_cancha(data):
    activa = data.get("activa", True)
    cancha_id = execute (
        "INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES (%s, %s, %s, %s, %s)", 
        (data["nombre"], data["id_deporte"], data["precio_hora"], data.get("techada", False), activa),
        return_id=True
    )
    return get_cancha_id(cancha_id)