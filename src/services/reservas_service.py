from src.db import execute, fetch_all, fetch_one, get_connection


def reservation_query(where="", params=(), limit=None, offset=None):
    pagination = " LIMIT %s OFFSET %s" if limit is not None else ""
    values = (*params, limit, offset) if limit is not None else params
    return fetch_all(f"""SELECT id, id_socio, id_cancha, fecha_hora_inicio,
        fecha_hora_fin, estado, precio_hora, precio_total
        FROM reservas {where} ORDER BY id{pagination}""", values)


def get_reservation(reservation_id):
    return fetch_one("""SELECT id, id_socio, id_cancha, fecha_hora_inicio,
        fecha_hora_fin, estado, precio_hora, precio_total
        FROM reservas WHERE id = %s""", (reservation_id,))


def count_reservations(where="", params=()):
    return fetch_one(f"SELECT COUNT(*) AS total FROM reservas {where}", params)["total"]


def find_member(member_id):
    return fetch_one("SELECT id, activo FROM socios WHERE id = %s", (member_id,))


def find_court(court_id):
    return fetch_one("SELECT id, precio_hora, activa FROM canchas WHERE id = %s", (court_id,))


def has_overlap(column, value, start, end):
    # Dos intervalos se superponen si uno empieza antes de que termine el otro.
    return fetch_one(f"""SELECT id FROM reservas
        WHERE {column} = %s AND estado = 'confirmada'
        AND fecha_hora_inicio < %s AND fecha_hora_fin > %s LIMIT 1""", (value, end, start)) is not None


def create_reservation(member_id, court_id, start, end, price, total):
    reservation_id = execute("""INSERT INTO reservas
        (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
        VALUES (%s, %s, %s, %s, 'confirmada', %s, %s)""", (member_id, court_id, start, end, price, total), True)
    return get_reservation(reservation_id)


def update_status(reservation_id, status):
    execute("UPDATE reservas SET estado = %s WHERE id = %s", (status, reservation_id))
    return get_reservation(reservation_id)


def create_reservations_transaction(reservations):
    # Las reservas recurrentes se guardan todas o no se guarda ninguna.
    connection = get_connection()
    cursor = connection.cursor()
    try:
        created_ids = []
        for reservation in reservations:
            cursor.execute("""INSERT INTO reservas
                (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin,
                 estado, precio_hora, precio_total)
                VALUES (%s, %s, %s, %s, 'confirmada', %s, %s)""", reservation)
            created_ids.append(cursor.lastrowid)
        connection.commit()
        return [get_reservation(reservation_id) for reservation_id in created_ids]
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
