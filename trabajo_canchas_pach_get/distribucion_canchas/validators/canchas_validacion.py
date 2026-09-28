import re

def validar_actializar_canchas(parametros_actualizar):
    errores=[]
    if "precio_hora" in parametros_actualizar:
        if not isinstance( parametros_actualizar["precio_hora"], int):
            errores.append({
                "code":"ERROR_VALIDACION",
                "message": "El cuerpo de la solicitud es invalido",
                "level": "error",
                "description":"El campo 'precio_hora' debe ser un entero"
            })
                
        elif parametros_actualizar["precio_hora"]<= 0:
            errores.append ({
                "code":"ERROR_VALIDACION",
                "message": "El cuerpo de la solicitud es invalido",
                "level": "error",
                "description":"El campo 'precio_hora' debe ser un entero mayor a cero"
            })
            
    campos_editables=["nombre", "precio_hora", "techada", "activa"]
     
    for campo_editable in parametros_actualizar:
        if campo_editable not in campos_editables:
            errores.append({                
                    "code":"ERROR_VALIDACION",
                    "message": "El cuerpo de la solicitud es invalido",
                    "level": "error",
                    "description":"El recurso no a sido encontado o no esta disponible su modificacion"}) 
                  
            
    if len(errores)>0:
        return {"errors":errores}
            
    return None

def validar_consulta_disponibles(parametros_url):
    errores=[]
    campos_validar=["fecha","hora_inicio", "hora_fin"]
    for campo in campos_validar:
        if campo not in parametros_url or not parametros_url[campo]:
            errores.append({
                "code":"MISSING_PARAMETER",
                "message": "parametro obligatorio faltante",
                "level":"error",
                "description":f"El parametro '{campo}' es requerido en la URL"
            })
    patron_hora= r'^([01]\d|2[0-3]):00:00$'
    if "hora_inicio" in parametros_url and not re.match(patron_hora, parametros_url["hora_inicio"]):
        errores.append({"code":"INVALID_FORMAT",
                        "message": "Formato de hora invalido",
                        "level":"error",
                        "description": "hora_inicio debe tener el formato HH:00:00"})

    if "limit" in parametros_url:
        limit= int (parametros_url["limit"])
        if limit< 1 or limit>100:
            errores.append({
                "code": "OUT_OF_BOUNDS",
                "message": "Límite fuera de rango",
                "level": "error",
                "description": "El parámetro _limit debe estar entre 1 y 100."
                
            })
    
    if len(errores) > 0:
        return {"errors": errores}
        
    return None