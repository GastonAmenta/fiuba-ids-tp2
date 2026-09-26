from datetime import datetime

from source.constantes import (
    HORA_CIERRE,
    HORA_APERTURA,
    HORA_RESERVACION_MAXIMA,
    HORA_RESERVACION_MINIMA,
)
from source.utiles import gmt_menos_3_actual, analisis_iso_datetime

def requiere_objeto_json(data):
    if not isinstance(data, dict) or not data:
        raise ValueError ("El cuerpo debe ser un objeto JSON no vacio")

def rechazar_campos_desconocidos(data, permitido):
    desconocido = set(data) - set(permitido)
    if desconocido:
        raise ValueError(f"campos desconocidos : {','.join(sorted(desconocido))}")

def campos_requeridos(data,campos):
    faltante = [campo for campo in campos if campo not in data]
    if faltante:
        raise ValueError (f"Faltan campos obligatorios: {','.join(faltante)}")

def validar_texto(valor,campo):
    if not isinstance(valor,str) or not valor.strip():
        raise ValueError (f"el campo '{campo}' no puede estar vacio")
    return valor.strip()

def validar_int_positivo(valor,campo):
    if isinstance(valor,bool) or not isinstance(valor,int) or valor <=0:
        raise ValueError (f"el campo '{campo}' debe ser un entero positivo")
    return valor

def validar_booleano(valor,campo):
    if not isinstance(valor,bool):
        raise ValueError (f"el campo '{campo}' debe ser un booleano")
    return valor

def validar_intervalo(comienzo_texto, final_texto):
    comienzo = analisis_iso_datetime(comienzo_texto)
    final = analisis_iso_datetime(final_texto)
    if comienzo >= final:
        raise ValueError("la fecha y hora de inicio debe ser anterior a la fecha y hora final")
    if comienzo <= gmt_menos_3_actual():
        raise ValueError("El inicio de la reserva debe ser posterior al momento actual")
    if comienzo.date() != final.date():
        raise ValueError("la reserva no puede atravesar la medianoche")
    if comienzo.minute or comienzo.second or comienzo.microsecond or final.minute or final.second or final.microsecond:
        raise ValueError("El intervalo debe comenzar y terminar en horas en punto")
    duracion = int((final - comienzo).total_seconds() // 3600)
    if not HORA_RESERVACION_MINIMA <= duracion <= HORA_RESERVACION_MAXIMA:
        raise ValueError("La reserva debe durar entre 1 y 3 horas")
    if comienzo.hour < HORA_APERTURA or final.hour > HORA_CIERRE:
        raise ValueError("El intervalo debe estar entre las 08:00 y las 23:00")
    return comienzo, final, duracion


