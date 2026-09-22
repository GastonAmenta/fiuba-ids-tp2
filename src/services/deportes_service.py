from src.db import fetch_all


def list_sports():
    return fetch_all("SELECT id, nombre FROM deportes ORDER BY id")
