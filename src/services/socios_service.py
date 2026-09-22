from src.db import execute, fetch_all, fetch_one


def list_members(filters, limit, offset):
    conditions = []
    params = []
    if filters.get("nombre") is not None:
        conditions.append("LOWER(nombre) LIKE %s")
        params.append(f"%{filters['nombre'].lower()}%")
    if filters.get("activo") is not None:
        conditions.append("activo = %s")
        params.append(filters["activo"])
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    rows = fetch_all(f"SELECT id, nombre, email, activo FROM socios {where} ORDER BY id LIMIT %s OFFSET %s", (*params, limit, offset))
    count = fetch_one(f"SELECT COUNT(*) AS total FROM socios {where}", params)
    return rows, count["total"]


def get_member(member_id):
    return fetch_one("SELECT id, nombre, email, activo FROM socios WHERE id = %s", (member_id,))


def create_member(data):
    member_id = execute("INSERT INTO socios (nombre, email) VALUES (%s, %s)", (data["nombre"], data["email"]), True)
    return get_member(member_id)


def update_member(member_id, data):
    assignments = ", ".join(f"{field} = %s" for field in data)
    execute(f"UPDATE socios SET {assignments} WHERE id = %s", (*data.values(), member_id))
    return get_member(member_id)
