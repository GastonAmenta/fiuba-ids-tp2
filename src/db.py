import os

import mysql.connector
from mysql.connector import Error


def get_connection():
	# Los datos de conexion vienen de .env o de Docker.
	return mysql.connector.connect(
		host=os.getenv("DB_HOST", "db"),
		port=int(os.getenv("DB_PORT", "3306")),
		user=os.getenv("DB_USER", "club_user"),
		password=os.getenv("DB_PASSWORD", "club_password"),
		database=os.getenv("DB_NAME", "club_deportivo"),
	)


def fetch_all(query, params=()):
	connection = get_connection()
	cursor = connection.cursor(dictionary=True)
	try:
		cursor.execute(query, params)
		return cursor.fetchall()
	finally:
		cursor.close()
		connection.close()


def fetch_one(query, params=()):
	rows = fetch_all(query, params)
	return rows[0] if rows else None


def execute(query, params=(), return_id=False):
	connection = get_connection()
	cursor = connection.cursor()
	try:
		cursor.execute(query, params)
		connection.commit()
		return cursor.lastrowid if return_id else cursor.rowcount
	except Error:
		# Una escritura fallida se deshace completa.
		connection.rollback()
		raise
	finally:
		cursor.close()
		connection.close()
