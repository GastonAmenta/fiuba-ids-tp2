from source.db import execute, fetch_all, fetch_one

def obtener_socio_id(id_socio):
    return fetch_one("SELECT id, nombre, email, activo FROM socios WHERE id = %s", (id_socio,))

def actualizar_socio(id_socio, datos):
    campos_permitidos = ["nombre", "email", "activo"]
    
    campos_set = []
    valores = []
    
    for clave, valor in datos.items():
        if clave in campos_permitidos:
            campos_set.append(f"{clave} = %s")
            valores.append(valor)
            
    if not campos_set:
        return obtener_socio_id(id_socio)
        
    valores.append(id_socio)
    
    clausula_set = ", ".join(campos_set)
    query = f"UPDATE socios SET {clausula_set} WHERE id = %s"
    
    execute(query, tuple(valores))
    
    return obtener_socio_id(id_socio)