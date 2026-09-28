from flask import Blueprint,jsonify,request
from layered_architecture.validators.canchas_validacion import validar_consulta_disponibles, validar_actializar_canchas
from layered_architecture.service.canchas_service import definiciones_canchas_diponibles
import traceback
Canchas_bp = Blueprint('Canchas_bp', __name__)


@Canchas_bp.route ("/Canchas/<int:id>", methods=['PATCH'])
def actualizar_cancha(id):
    try:
        datos = request.get_json()
        
        errores_validacion = validar_actializar_canchas(datos)
        if errores_validacion:
            return jsonify(errores_validacion), 400
        
        return '', 204 

        
    except Exception as e:
        
        print(traceback.format_exc()) 
        
        respuesta_500 = {
            "errors": [
                {
                    "code": "ERROR_INTERNO",
                    "message": "Error interno del servidor",
                    "level": "error",
                    "description": "Ha ocurrido un error inesperado al procesar la solicitud."
                }
            ]
        }
        
        return jsonify(respuesta_500), 500
    




@Canchas_bp.route('/canchas/disponibles', methods=['GET'])
def consultar_canchas_disponibles():
    

    parametros = request.args
    

    errores_formato = validar_consulta_disponibles(parametros)
    
    if errores_formato:

        return jsonify(errores_formato), 400
        

    fecha = parametros.get('fecha')
    hora_inicio = parametros.get('hora_inicio')
    hora_fin = parametros.get('hora_fin')
    
    limit = int(parametros.get('limit', 10))
    offset = int(parametros.get('offset', 0))
    
    id_deporte = parametros.get('id_deporte')
    if id_deporte is not None:
        id_deporte = int(id_deporte)
        
    techada = parametros.get('techada')
    if techada is not None:

        techada = techada.lower() == 'true'

    resultado = definiciones_canchas_diponibles(
        hora_inicio, hora_fin, fecha, limit, offset, id_deporte, techada
    )
    

    if isinstance(resultado, dict) and "Error" in resultado:
        respuesta_error = {
            "errors": [{
                "code": "BUSINESS_RULE_VIOLATION",
                "message": "Regla de negocio no cumplida",
                "level": "error",
                "description": resultado["Error"]
            }]
        }
        return jsonify(respuesta_error), 400
        

    return jsonify({"canchas": resultado}), 200
