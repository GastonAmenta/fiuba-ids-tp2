from src.utils import now_gmt_minus_3, validar_id as parse_id
from src.validators.common import reject_unknown_fields, require_json_object


def validar_id_reserva(reservation_id):
    """
    Valida y normaliza el id de reserva.
    """
    return parse_id(reservation_id)


def validar_existencia_reserva(reserva):
    """
    Verifica que la reserva exista.
    """
    if reserva is None:
        return error(
            "RESERVA_NO_ENCONTRADA",
            "Reserva inexistente",
            "No existe una reserva con ese id",
            404,
        )
    return None


def validar_cuerpo_estado(data):
    """
    Valida el body del PUT /reservas/{id}/estado.
    """
    require_json_object(data)
    reject_unknown_fields(data, {"estado"})

    estado_solicitado = data.get("estado")
    if estado_solicitado not in RESERVATION_STATES:
        raise ValueError("El estado solicitado no es válido")

    return estado_solicitado


def validar_transicion_estado(reserva, estado_solicitado):
    """
    Valida las reglas de transición de estado.
    """
    estado_actual = reserva["estado"]

    # Repetir el estado actual → éxito sin modificar
    if estado_solicitado == estado_actual:
        return ("", 204)

    # Solo se puede transicionar desde 'confirmada'
    if estado_actual != "confirmada":
        raise ValueError(
            "Una reserva cancelada o finalizada no puede cambiar de estado"
        )

    ahora = now_gmt_minus_3()

    # Cancelar solo si el inicio todavía no llegó
    if estado_solicitado == "cancelada":
        if ahora >= reserva["fecha_hora_inicio"]:
            raise ValueError("El horario de inicio ya llegó, no se puede cancelar")

    # Finalizar solo si el fin ya se alcanzó
    if estado_solicitado == "finalizada":
        if ahora < reserva["fecha_hora_fin"]:
            raise ValueError(
                "El horario de finalización todavía no llegó, no se puede finalizar"
            )

    return None