from datetime import timedelta, timezone


CLUB_OPENING_HOUR = 8
CLUB_CLOSING_HOUR = 23
MIN_RESERVATION_HOURS = 1
MAX_RESERVATION_HOURS = 3
DEFAULT_LIMIT = 10
MAX_LIMIT = 100
RESERVATION_STATES = ("confirmada", "cancelada", "finalizada")
GMT_MINUS_3 = timezone(timedelta(hours=-3))
