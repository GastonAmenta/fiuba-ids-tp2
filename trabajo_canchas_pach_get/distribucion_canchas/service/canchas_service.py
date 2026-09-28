from layered_architecture.repositories.canchas_repositorio import obtener_canchas_diponibles, actualizar_cancha_parcialmente


def definiciones_actualizar_canchas(id_buscado, datos_nuevos):
    
    if len(datos_nuevos)== 0:
        return{"Error":"No hay datos para actualizar"}
    
    if "precio_hora" in datos_nuevos:
        if datos_nuevos["precio_hora"] < 0:
            return{"Error": "campo precio de la hora no puede ser negativo"}
    
    if "nombre" in datos_nuevos:   
        if len(datos_nuevos["nombre"].strip()) == 0:
            return{"Error": "el nombre de la cancha no puede estar vacio"}
        
    if "id" in datos_nuevos or "id_deporte" in datos_nuevos:  
        return{"Error": "el deporte asociado no se puede modificar una vez creada la cancha"}
        
    fila= actualizar_cancha_parcialmente(id_buscado, datos_nuevos)
    return fila


def definiciones_canchas_diponibles(hora_inicio, hora_fin, fecha, limit, offset, id_deporte=None, techada=None):
    
    if offset < 0:
        return{"Error":"Entero mayor o igual a cero"}
    
    if limit< 1 or limit>100:
        return{"Error":"Entero entre 1 y 100"}
    
    if hora_inicio >= hora_fin:
        return{"Error":"No existe cancha disponible que la hora se pisen"}
    
    if not fecha or not hora_inicio or not hora_fin:
        return{"Error":"es necesario colocar la fecha, hora de inicio y hora fin sin excepcion"}

    
    filas=obtener_canchas_diponibles(hora_inicio, hora_fin, fecha, limit, offset, id_deporte, techada)
    
    return filas
