from sqlalchemy import text
from database import db

#-----------------------------------------------------------------------------------------------
#Funciones de soporte
#-----------------------------------------------------------------------------------------------


def ejecutar_consulta(sql: str, parametros:dict= None)

    with db.connect() as conexion:
     
        resultado = conexion.execute(text(sql), parametros or {})
        
        return [fila_adict(fila) for fila in resultado]
    

def ejecutar_mutacion (sql:str, parametros:dict= None):
    """
    ejecuta un INSERT, UPDATE o DELATE y hace commit .
    Retorna el id autoincremental generado por el INSERT (0 si no aplica).
    """
    with db.begin.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})
        
        return resultado.lastrowid or 0  

#-----------------------------------------------------------------------------------------------
#Queries de canchas
#-----------------------------------------------------------------------------------------------

def actualizar_cancha_parcialmente(id_buscado, datos_nuevos):
    
    if not datos_nuevos:
        return 0
    
    fragmento=[]
    for clave in datos_nuevos.keys():
        fragmento.append(f"{clave}= :{clave}")
        
    datos_separados= ",".join(fragmento)    
    sql= f"""UPDATE canchas SET {datos_separados} WHERE id = :id 
    """
    
    datos_nuevos["id"]= id_buscado
    
    filas_afectadas= ejecutar_mutacion(sql, datos_nuevos)
    
    return filas_afectadas


def obtener_canchas_diponibles(hora_inicio, hora_fin, fecha, limit, offset, id_deporte=None, techada=None):
    sql= """SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas WHERE activa = True 
    AND id NOT IN (
        SELECT id_cancha FROM reservas
        
        WHERE fecha = :fecha
        AND (hora_inicio < :hora_fin AND hora_fin > :hora_inicio) 
    )  
    """

    if id_deporte is not None:
        sql+= "AND id_deporte = :id_deporte"
    
    if techada is not None:
        sql+= "AND techada = :techada"
        
    sql += "LIMIT :limit OFFSET :offset"
    
    parametros={
        "offset": offset,
        "limit": limit,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "id_deporte": id_deporte,
        "techada": techada
        
    }
    resultado = db.session.execute(text(sql), parametros)
    filas=[dict(row._mapping) for row in resultado]
    return filas



