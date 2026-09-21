from flask import Blueprint, jsonify

from src.services import deportes as service

bp = Blueprint("deportes", __name__, url_prefix="/deportes")


@bp.get("")
def listar_deportes():
    resultado = service.listar_deportes()
    if not resultado:
        return "", 204
    return jsonify(resultado), 200