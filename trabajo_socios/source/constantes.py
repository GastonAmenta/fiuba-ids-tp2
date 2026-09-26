from datetime import timedelta, timezone

HORA_APERTURA = 8
HORA_CIERRE = 23
HORA_RESERVACION_MINIMA = 1
HORA_RESERVACION_MAXIMA = 3
LIMIT_DEFAULT = 10
LIMIT_MAXIMO = 100
ESTADOS_RESERVACION = ("confirmada", "cancelada", "finalizada")
GMT_MENOS_3 = timezone(timedelta(hours=-3))