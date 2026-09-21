import pymysql
from pymysql.cursors import DictCursor

from src.constants import DB_CONFIG


def get_connection():
    """
    Abre una conexión nueva a MySQL.
    Devuelve un objeto Connection de PyMySQL.
    El llamador es responsable de cerrarla (usar context manager).
    """
    config = dict(DB_CONFIG)
    config["cursorclass"] = DictCursor  # devuelve filas como dict
    return pymysql.connect(**config)


def execute_query(sql, params=None, fetch_one=False, fetch_all=False):
    """
    Ejecuta una query de LECTURA (SELECT).
    Devuelve:
      - un dict si fetch_one=True
      - una lista de dicts si fetch_all=True
      - None si no se pide nada
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            return None
    finally:
        conn.close()


def execute_write(sql, params=None):
    """
    Ejecuta una query de ESCRITURA (INSERT / UPDATE / DELETE).
    Hace commit y devuelve:
      - lastrowid si fue un INSERT
      - rowcount en cualquier caso
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            conn.commit()
            return {
                "lastrowid": cursor.lastrowid,
                "rowcount":  cursor.rowcount,
            }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_transaction(queries):
    """
    Ejecuta varias queries en una única transacción.
    `queries` es una lista de tuplas (sql, params).
    Si alguna falla, hace rollback de todas.
    Devuelve una lista con los resultados (dict con lastrowid/rowcount).
    """
    conn = get_connection()
    results = []
    try:
        with conn.cursor() as cursor:
            for sql, params in queries:
                cursor.execute(sql, params or ())
                results.append({
                    "lastrowid": cursor.lastrowid,
                    "rowcount":  cursor.rowcount,
                })
        conn.commit()
        return results
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_select_for_update(sql, params=None):
    """
    Ejecuta un SELECT ... FOR UPDATE dentro de una transacción.
    Pensado para las validaciones de superposición en reservas.
    NOTA: el llamador debe manejar la conexión externamente si necesita
          hacer varios SELECT FOR UPDATE + INSERT en la misma transacción.
    """
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            rows = cursor.fetchall()
        return conn, rows  # el llamador decide commit/rollback y cierra
    except Exception:
        conn.rollback()
        conn.close()
        raise