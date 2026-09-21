import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Configuración de la base de datos
# ============================================================
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "database": os.getenv("DB_NAME", "club_deportivo"),
    "charset":  "utf8mb4",
    "cursorclass": None,  # se completa en db.py para evitar import circular
    "autocommit": False,
}

# ============================================================
# Configuración de Flask
# ============================================================
API_PREFIX = "/api"
FLASK_PORT  = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

# ============================================================
# Reglas de dominio (según enunciado)
# ============================================================
HORA_APERTURA   = 8     # 08:00
HORA_CIERRE     = 23    # 23:00
DURACION_MIN_H  = 1
DURACION_MAX_H  = 3

ESTADOS_RESERVA = ("confirmada", "cancelada", "finalizada")

PAGINACION_LIMIT_DEFAULT = 10
PAGINACION_LIMIT_MAX     = 100
PAGINACION_OFFSET_DEFAULT = 0

# ============================================================
# Códigos de error (para el schema `Error` del swagger)
# ============================================================
ERROR_VALIDACION     = "ERROR_VALIDACION"
ERROR_NO_ENCONTRADO  = "ERROR_NO_ENCONTRADO"
ERROR_CONFLICTO      = "ERROR_CONFLICTO"
ERROR_INTERNO        = "ERROR_INTERNO"