from source.db import execute, fetch_all, fetch_one

def listar_socios(filtros, limit, offset):
    condiciones = []
    parametros = []
    if filtros.get("nombre") is not None:
        condiciones.append("LOWER(nombre) LIKE %s")
        parametros.append(f"%{filtros['nombre'].lower()}%")
    if filtros.get("activo") is not None:
        condiciones.append("activo = %s")
        parametros.append(filtros["activo"])
    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    filas = fetch_all(f"SELECT id, nombre, email, activo FROM socios {where} ORDER BY id LIMIT %s OFFSET %s", (*parametros, limit, offset))
    conteo = fetch_one(f"SELECT COUNT(*) AS total FROM socios {where}", parametros)
    return filas, conteo["total"]

def crear_socio(data):
    activo = data.get("activo", True)
    id_socio = execute(
        "INSERT INTO socios (nombre, email, activo) VALUES (%s, %s, %s)",
        (data["nombre"], data["email"], activo),
        return_id=True
    )
    # necesita la funcion obtener_socio_id para devolver el socio creado
    return obtener_socio_id(id_socio)