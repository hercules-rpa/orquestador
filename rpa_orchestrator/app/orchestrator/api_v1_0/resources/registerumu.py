import json
from datetime                               import datetime
from rpa_orchestrator.ControllerProcess    import ControllerProcess
from flask                                  import Blueprint, request, abort
from flask.wrappers                         import Response
from flask_restful                          import Api, Resource
from rpa_orchestrator.ControllerProcess    import ControllerProcess
from rpa_orchestrator.orchestrator      import Orchestrator
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import token_required, token_required_investigador
import rpa_orchestrator.lib.dbprocess.models as model
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime

orch = Orchestrator()
cp = ControllerProcess()
registerumu_v1_0_bp = Blueprint('registerumu_v1_0_bp', __name__)
api = Api(registerumu_v1_0_bp)

def getBlueprint():
    return registerumu_v1_0_bp

class Convocatoria(Resource):
    @token_required
    def get(self, id_convocatoria = None):
        filter = {}
        if not id_convocatoria:
            arguments = {"id": int, "fecha_creacion": datetime, "fecha_publicacion": datetime, "titulo": str, "_from": str, "url":str, "entidad_gestora":str, 
                        "entidad_convocante":str, "area_tematica":str, "observaciones":str, "id_sgi": str, "idproceso":int, "notificada":bool, "unidad_gestion":str, "modelo_ejecucion":str}
            for (key, value) in arguments.items():
                if request.args.get(key)=="null":
                    filter[key] = None
                if request.args.get(key, type = value):
                    if not request.args.get(key):
                        filter[key] = None
                    elif value is bool:
                        filter[key] = request.args.get(key) in ['true','True'] #Lo tratamos como string para sacar que booleano es.
                    elif value is datetime:
                        filter[key] = datetime.fromtimestamp(request.args.get(key)).isoformat()
                    else:
                        filter[key] = request.args.get(key, type = value)
        else:
            filter['id'] = id_convocatoria
        resp = cp.get_convocatoria(filter)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')
    @token_required
    def post(self):
        convocatoria_list = json.dumps(request.get_json(force=True))
        try:
            convocatoria_list = json.loads(convocatoria_list, object_hook=lambda d: model.Convocatoria(**d))
            cp.dump(convocatoria_list)
            resp = json.dumps({"status": "ok", "convocatoria": [x.id for x in convocatoria_list], "description":"Convocatoria Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            abort(400, description=str(e))
    @token_required
    def patch(self, id_convocatoria):
        new_parameters = request.get_json()
        black_list = ['id','fecha_creacion']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_convocatoria(id_convocatoria, new_parameters)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        resp = json.dumps({"status": "ok", "convocatoria": id_convocatoria, "description":"Convocatoria Updated"})
        return Response(resp,mimetype='application/json')


class Solicitud(Resource):
    @token_required
    def get(self, id_solicitud = None):
        filter = {}
        if not id_solicitud:
            arguments = {"id": int, "id_solicitud": int, "email": str, "concesion":bool, "referencia_proyecto": str, "IP": str, "fecha_creacion": datetime}
            for (key, value) in arguments.items():
                if request.args.get(key)=="null":
                    filter[key] = None
                if request.args.get(key, type = value):
                    if not request.args.get(key) or request.args.get(key)=="null":
                        filter[key] = None
                    elif value is bool:
                        filter[key] = request.args.get(key) in ['true','True'] #Lo tratamos como string para sacar que booleano es.
                    elif value is datetime:
                        filter[key] = datetime.fromtimestamp(request.args.get(key)).isoformat()
                    else:
                        filter[key] = request.args.get(key, type = value)
        else:
            filter['id'] = id_solicitud
        resp = cp.get_solicitud(filter)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')
    @token_required
    def post(self):
        solicitud_list = json.dumps(request.get_json(force=True))
        try:
            solicitud_list = json.loads(solicitud_list, object_hook=lambda d: model.Solicitud(**d))
            print(solicitud_list)
            cp.dump(solicitud_list)
            resp = json.dumps({"status": "ok", "convocatoria": [x.id for x in solicitud_list], "description":"Solicitud Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            abort(400, description=str(e))
    @token_required
    def patch(self, id_solicitud):
        new_parameters = request.get_json()
        black_list = ['id','fecha_creacion']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_solicitud(id_solicitud, new_parameters)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        resp = json.dumps({"status": "ok", "Solicitud": id_solicitud, "description":"Solicitud Updated"})
        return Response(resp,mimetype='application/json')


class Base_Reguladora(Resource):
    @token_required
    def get(self, id_basereguladora = None):
        filter = {}
        if not id_basereguladora:
            arguments = {"id": int, "id_base": str, "fecha_creacion": datetime, "titulo": str, "url": str, "notificada":bool, "seccion": str, "departamento": str}
            for (key, value) in arguments.items():
                if request.args.get(key)=="null":
                    filter[key] = None
                if request.args.get(key, type = value):
                    if not request.args.get(key) or request.args.get(key)=="null":
                        filter[key] = None
                    elif value is bool:
                        filter[key] = request.args.get(key) in ['true','True'] #Lo tratamos como string para sacar que booleano es.
                    elif value is datetime:
                        filter[key] = datetime.fromtimestamp(request.args.get(key)).isoformat()
                    else:
                        filter[key] = request.args.get(key, type = value)
        else:
            filter['id'] = id_basereguladora
        resp = cp.get_basereguladora(filter)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')

    @token_required
    def post(self):
        basereguladora_list = json.dumps(request.get_json(force=True))
        try:
            basereguladora_list = json.loads(basereguladora_list, object_hook=lambda d: model.Basereguladora(**d))
            cp.dump(basereguladora_list)
            resp = json.dumps({"status": "ok", "BaseReguladora": [x.id for x in basereguladora_list], "description":"Base Reguladora Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            abort(400, description=str(e))

    @token_required
    def patch(self, id_basereguladora):
        new_parameters = request.get_json()
        black_list = ['id','fecha_creacion']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_basereguladora(id_basereguladora, new_parameters)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        resp = json.dumps({"status": "ok", "Base Reguladora": id_basereguladora, "description":"Base Reguladora Updated"})
        return Response(resp,mimetype='application/json')

class Ejecucion_Boletin(Resource):
    @token_required
    def get(self, id_notificacion = None):
        filter = {}
        if not id_notificacion:
            arguments = {"id": int, "fecha_inicio":datetime, "fecha_fin":datetime, "fecha_ejecucion": datetime, "exito" : bool}
            for (key, value) in arguments.items():
                if request.args.get(key)=="null":
                    filter[key] = None
                if request.args.get(key, type = value):
                    if not request.args.get(key) or request.args.get(key)=="null":
                        filter[key] = None
                    elif value is bool:
                        filter[key] = request.args.get(key) in ['true','True']
                    else:
                        filter[key] = request.args.get(key, type = value)         
        else:
            filter['id'] = id_notificacion
        resp = cp.get_ejecucion_boletin(filter)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')
    
    @token_required
    def post(self):
        notificacion_list = json.dumps(request.get_json(force=True))
        try:
            notificacion_list = json.loads(notificacion_list, object_hook=lambda d: model.Ejecucion_Boletin(**d))
            cp.dump(notificacion_list)
            resp = json.dumps({"status": "ok", "Ejecucion_Boletin": [x.id for x in notificacion_list], "description":"Ejecucion_Boletin Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            abort(400, description=str(e))

    @token_required
    def patch(self, id_notificacion):
        new_parameters = request.get_json()
        black_list = ['id','fecha_creacion']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_ejecucion_notificacion(id_notificacion, new_parameters)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        resp = json.dumps({"status": "ok", "Ejecucion_Boletin": id_notificacion, "description":"Ejecucion_Boletin Updated"})
        return Response(resp,mimetype='application/json')

class Ultima_Ejecucion_Boletin(Resource):
    @token_required
    def get(self):
        resp = cp.get_ejecucion_boletin_ultima()
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')  

class AreaTematica(Resource):
    @token_required
    def get(self, id_areatematica = None):
        filter = {}
        if not id_areatematica:
            arguments = {"id": int, "nombre": str, "fuente":str, "descripcion": str}
            for (key, value) in arguments.items():
                if request.args.get(key)=="null":
                    filter[key] = None
                if request.args.get(key, type = value):
                    if not request.args.get(key) or request.args.get(key)=="null":
                        filter[key] = None
                    elif value is bool:
                        filter[key] = request.args.get(key) in ['true','True']
                    else:
                        filter[key] = request.args.get(key, type = value)
            resp = cp.get_areatematica(filter)
        else:
            resp = cp.get_areatematica_id(id_areatematica)
       
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')

    @token_required
    def post(self):
        areatematica = request.get_json(force=True)
        
        if(len(areatematica) > 1):
            abort(400, description="Solo se permite una única insercción de area tematica a la vez")
        areatematica = areatematica[0]
  
        if 'parents' in areatematica and areatematica['parents']['id']:
            if 'parents' in areatematica['parents']:
                abort(400, description="No se permite que exista un padre dentro de otro padre")           
            areatematica_p = json.loads(cp.get_areatematica_id(int(areatematica['parents']['id'])))
            print(areatematica_p)
            del areatematica_p['padre']
            del areatematica_p['hijos']
            del areatematica['parents']
            areatematica_p = json.loads(json.dumps(areatematica_p), object_hook=lambda d: model.Areatematica(**d))
            areatematica = json.loads(json.dumps(areatematica), object_hook=lambda d: model.Areatematica(**d))
            areatematica_p.parents.append(areatematica) #le metemos el hijo al padre
            cp.dump([areatematica_p])
        else:
            del areatematica['parents']
            areatematica = json.loads(json.dumps(areatematica), object_hook=lambda d: model.Areatematica(**d))
            cp.dump([areatematica])
        resp = json.dumps({"status": "ok", "id": areatematica.id, "description":"Area tematica Created"})
        return Response(resp, status=201, mimetype='application/json')

    @token_required
    def patch(self, id_areatematica):
        new_parameters = request.get_json()
        black_list = ['id']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_areatematica(id_areatematica, new_parameters)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        resp = json.dumps({"status": "ok", "Area tematica": id_areatematica, "description":"Area tematica Updated"})
        return Response(resp,mimetype='application/json')

class Investigador(Resource):
    @token_required
    def get(self, id_investigador = None):
        filter = {}
        if not id_investigador:
            arguments = {"id": int, "nombre": str, "email": str, "perfil":bool}
            for (key, value) in arguments.items():
                if request.args.get(key)=="null":
                    filter[key] = None
                if request.args.get(key, type = value):
                    if not request.args.get(key) or request.args.get(key)=="null":
                        filter[key] = None
                    elif value is bool:
                        filter[key] = request.args.get(key) in ['true','True']
                    else:
                        filter[key] = request.args.get(key, type = value)
        else:
            filter['id'] = id_investigador
        resp = cp.get_investigador(filter)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')
    
    @token_required
    def post(self):
        investigadores = json.dumps(request.get_json(force=True))
        try:
            print(investigadores)
            investigadores = json.loads(investigadores, object_hook=lambda d: model.Investigador(**d))
            cp.dump(investigadores)
            resp = json.dumps({"status": "ok", "Investigadores": [x.id for x in investigadores], "description":"Investigador Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            print(str(e))
            abort(400, description=str(e))

    @token_required
    def patch(self, id_investigador):
        new_parameters = request.get_json()
        black_list = ['id']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_investigador(id_investigador, new_parameters)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        resp = json.dumps({"status": "ok", "Investigador": id_investigador, "description":"Investigador Updated"})
        return Response(resp,mimetype='application/json')

class CalificacionArea(Resource):
    @token_required
    def get(self, id_investigador = None):
        filter = {}
        if not id_investigador:
            arguments = {"id": int, "idinvestigador": int, "idarea": int, "puntuacion": float}
            for (key, value) in arguments.items():
                if request.args.get(key)=="null":
                    filter[key] = None
                if request.args.get(key, type = value):
                    if not request.args.get(key) or request.args.get(key)=="null":
                        filter[key] = None
                    elif value is bool:
                        filter[key] = request.args.get(key) in ['true','True']
                    else:
                        filter[key] = request.args.get(key, type = value)
        else:
            filter['id'] = id_investigador
        resp = cp.get_calificacionArea(filter)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')

    @token_required_investigador
    def post(self):
        calificaciones = json.dumps(request.get_json(force=True))
        print(calificaciones)
        try:
            idinv = get_jwt_identity()
            calificaciones = json.loads(json.dumps(cp.procesar_puntuaciones(idinv, json.loads(calificaciones))), object_hook=lambda d: model.Calificacionarea(**d))
            cp.dump(calificaciones)
            cp.calcular_puntuaciones_areas(calificaciones)
            resp = json.dumps({"status": "ok", "calificaciones": [x.id for x in calificaciones], "description":"Calificaciones Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            print(e)
            return Response(json.dumps({"status": "ERROR", "message":"Error al calificar "+str(e)}), status = 400, mimetype='application/json')

    @token_required_investigador
    def patch(self, id_calificacion):
        new_parameters = request.get_json()
        black_list = ['id']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_calificacionArea(id_calificacion, new_parameters)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        resp = json.dumps({"status": "ok", "Calificacion": id_calificacion, "description":"Calificacion Updated"})
        return Response(resp,mimetype='application/json')
    
    @token_required_investigador
    def delete(self):
        load = request.args.get('load')
        load = load in ['True','true']
        idinv = get_jwt_identity()
        if cp.delete_perfil(idinv):
            if load:
                cp.cargar_perfil(idinv)
            resp = json.dumps({"status": "ok", "description":"Perfil Reseteado"})
            return Response(resp, status=200, mimetype='application/json')
        else:
            resp = json.dumps({"status": "Error", "description":"Perfil NO Reseteado"})
            return Response(resp, status=400, mimetype='application/json')
        

class CalificacionConvocatoria(Resource):
    @token_required
    def get(self, id_investigador = None):
        filter = {}
        if not id_investigador:
            arguments = {"id": int, "idinvestigador": int, "idconvocatoriasgi": int, "titulo":str , "puntuacion": int}
            for (key, value) in arguments.items():
                if request.args.get(key)=="null":
                    filter[key] = None
                if request.args.get(key, type = value):
                    if not request.args.get(key) or request.args.get(key)=="null":
                        filter[key] = None
                    elif value is bool:
                        filter[key] = request.args.get(key) in ['true','True']
                    else:
                        filter[key] = request.args.get(key, type = value)
        else:
            filter['id'] = id_investigador
        resp = cp.get_calificacionConvocatoria(filter)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')
    
    @token_required_investigador
    def post(self):
        calificaciones = json.dumps(request.get_json(force=True))
        try:
            calificaciones = json.loads(calificaciones, object_hook=lambda d: model.Calificacionconvocatoria(**d))
            cp.dump(calificaciones)
            resp = json.dumps({"status": "ok", "calificaciones": [x.id for x in calificaciones], "description":"Calificaciones Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            abort(400, description=str(e))

    @token_required
    def patch(self, id_calificacion):
        new_parameters = request.get_json()
        black_list = ['id']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_calificacionConvocatoria(id_calificacion, new_parameters)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        resp = json.dumps({"status": "ok", "Calificacion": id_calificacion, "description":"Calificacion Updated"})
        return Response(resp,mimetype='application/json')

class NotificacionInvestigador(Resource):
    @token_required
    def get(self, id_notInv = None):
        filter = {}
        if not id_notInv:
            arguments = {"id": int, "idinvestigador": int, "idconvocatoriasgi": int, "idcalificacionarea": int, "idcalificacionConvocatoria": int, "notificacion": bool, "fechacreacion":datetime}
            for (key, value) in arguments.items():
                if request.args.get(key)=="null":
                    filter[key] = None
                if request.args.get(key, type = value):
                    if not request.args.get(key) or request.args.get(key)=="null":
                        filter[key] = None
                    elif value is bool:
                        filter[key] = request.args.get(key) in ['true','True']
                    elif value is datetime:
                        filter[key] = datetime.fromtimestamp(request.args.get(key)).isoformat()
                    else:
                        filter[key] = request.args.get(key, type = value)      
        else:
            filter['id'] = id_notInv
        resp = cp.get_notificacionInvestigador(filter)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')

    @token_required
    def post(self):
        notificacionesInv = json.dumps(request.get_json(force=True))
        try:
            notificacionesInv = json.loads(notificacionesInv, object_hook=lambda d: model.Notificacioninvestigador(**d))
            cp.dump(notificacionesInv)
            resp = json.dumps({"status": "ok", "Notificaciones ": [x.id for x in notificacionesInv], "description":"Notificaciones Investigadores Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({"status":"error","message":str(e)}), status=400, mimetype='application/json')

    @token_required
    def patch(self, id_notinv):
        new_parameters = request.get_json()
        black_list = ['id','fechaCreacion']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_notificacionInvestigador(id_notinv, new_parameters)
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        resp = json.dumps({"status": "ok", "notificacion": id_notinv, "description":"Notificacion Updated"})
        return Response(resp,mimetype='application/json')

class NotificacionInvestigadorLast(Resource):
    @token_required
    def get(self):
        resp = cp.get_notificacion_investigador_last()
        if not resp:
            return Response(json.dumps({"msg": "Resource not found"}), status=404, mimetype='application/json')
        return Response(resp,mimetype='application/json')

class FeedbackConvocatoria(Resource):
    @token_required_investigador
    def post(self, idconvocatoria, util):
        utilidad_c = {}
        utilidad_c['no'] = -0.25
        utilidad_c['si'] = 0.25
        idinv = get_jwt_identity()
        try:
            if not util in utilidad_c:
                return Response(json.dumps({"status": "ERROR", "message":"bad syntaxis"}), status = 400, mimetype='application/json')
            if cp.feedback_convocatoria(idconvocatoria, idinv, utilidad_c[util]):
                return Response(json.dumps({"status":"ok"}),status=201,mimetype='application/json')
            else:
                return Response(json.dumps({"status": "ERROR", "message":"Ocurrió un error inesperado, consulte el log para más información"}), status = 400, mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({"status": "ERROR", "message":str(e)}), status = 400, mimetype='application/json')


class Token(Resource):
    @token_required
    def post(self):
        """Generamos un token para el investigador teniendo como información el iduser, idrobot y el token amqp del robot"""
        user = request.json.get("iduser", None)
        token = request.json.get("token", None)
        robot = request.json.get("idrobot", None)
        
        if not orch.is_token_valid(robot, token):
            return Response(json.dumps({"message":"bad password"}),status=401,mimetype='application/json')

        access_token = create_access_token(identity=user, expires_delta=datetime.timedelta(days=6))
        result = {}
        result['access_token'] = access_token
        return Response(json.dumps(result),mimetype='application/json')

class PerfilRecomendacion(Resource):
    @token_required_investigador
    def get(self):
        idinv = get_jwt_identity()
        filter = {}
        filter['id'] = idinv
        result = cp.get_areatematica_pretty(idinv)
        return Response(result,mimetype='application/json')

class InvestigadorPerfil(Resource):
    def get(self):
        investigadores = cp.get_investigador()
        result = []
        if len(investigadores) > 0:
            investigadores = json.loads(investigadores)
        for inv in investigadores:
            if inv['perfil']:
                perfil = {}
                perfil['nombre']   = inv['nombre']
                perfil['email']    = inv['email']
                perfil['tree']     = json.loads(cp.get_areatematica_pretty(inv['id']))
                result.append(perfil)
        return Response(json.dumps(result),mimetype='application/json')

class ProcessConfigResource(Resource):
    @token_required
    def get(self):
        try:
            path = request.args.get("path")
            if not path:
                data = cp.get_config_list()
                if data:
                    return Response(cp.get_config_list(),mimetype='application/json')
            else:
                data = cp.get_config(path)
                if data:
                    return Response(data,mimetype='application/json')
            return Response(json.dumps({"status": "ERROR", "message":"No existe el configurador"}), status = 400, mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({"status": "ERROR", "message":str(e)}), status = 400, mimetype='application/json')
    
    @token_required
    def patch(self):
        try:
            path = request.args.get("path")
            data = json.dumps(request.get_json(force=True))
            if not path:
                return Response(json.dumps({"status": "ERROR", "message": "Es necesario una ruta para modificar"}), status = 400, mimetype='application/json')
            else:
                if cp.patch_config(path, data):
                    return Response(json.dumps({"status": "Ok", "message": "Configurador modificado"}),mimetype='application/json')
                else:
                    return Response(json.dumps({"status": "ERROR", "message": "No se pudo modificar el configurador"}), status = 400, mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({"status": "ERROR", "message": str(e)}), status = 400, mimetype='application/json')
        
    @token_required
    def post(self):
        try:
            path = request.args.get("path")
            
            if not path:
                return Response(json.dumps({"status": "ERROR", "message": "Es necesario una ruta para modificar"}), status = 400, mimetype='application/json')
            else:
                if cp.restore_config(path):
                    return Response(json.dumps({"status": "Ok", "message": "Configurador restaurado"}),mimetype='application/json')
                else:
                    return Response(json.dumps({"status": "ERROR", "message": "No se pudo restaurar el configurador"}), status = 400, mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({"status": "ERROR", "message": str(e)}), status = 400, mimetype='application/json')
        

api.add_resource(Convocatoria,'/api/orchestrator/register/convocatorias',endpoint='convocatorias')
api.add_resource(Convocatoria,'/api/orchestrator/register/convocatoria/<int:id_convocatoria>',endpoint='patch_convocatoria')
api.add_resource(Convocatoria,'/api/orchestrator/register/convocatoria/<int:id_convocatoria>',endpoint='get_convocatoria')
api.add_resource(Solicitud,'/api/orchestrator/register/solicitudes',endpoint='solicitudes')
api.add_resource(Solicitud,'/api/orchestrator/register/solicitud/<int:id_solicitud>',endpoint='get_solicitud')
api.add_resource(Solicitud,'/api/orchestrator/register/solicitud/<int:id_solicitud>',endpoint='patch_solicitud')
api.add_resource(Base_Reguladora,'/api/orchestrator/register/basesreguladoras',endpoint='basesreguladoras')
api.add_resource(Base_Reguladora,'/api/orchestrator/register/basereguladora/<int:id_basereguladora>',endpoint='get_basereguladora')
api.add_resource(Base_Reguladora,'/api/orchestrator/register/basereguladora/<int:id_basereguladora>',endpoint='patch_basereguladora')
api.add_resource(AreaTematica,'/api/orchestrator/register/areatematica',endpoint='areas')
api.add_resource(AreaTematica,'/api/orchestrator/register/areatematica/<int:id_areatematica>',endpoint='get_area')
api.add_resource(AreaTematica,'/api/orchestrator/register/areatematica/<int:id_areatematica>',endpoint='patch_area')
api.add_resource(Investigador,'/api/orchestrator/register/investigador',endpoint='investigadores')
api.add_resource(Investigador,'/api/orchestrator/register/investigador/<int:id_investigador>',endpoint='get_investigador')
api.add_resource(Investigador,'/api/orchestrator/register/investigador/<int:id_investigador>',endpoint='patch_investigador')
api.add_resource(NotificacionInvestigador,'/api/orchestrator/register/notificacioninvestigador',endpoint='notificacioninvestigadores')
api.add_resource(NotificacionInvestigadorLast,'/api/orchestrator/register/notificacioninvestigador/last',endpoint='get_lastnotificacioninvestigadores')
api.add_resource(NotificacionInvestigador,'/api/orchestrator/register/notificacioninvestigador/<int:id_notificacioninvestigador>',endpoint='get_notificacioninvestigador')
api.add_resource(NotificacionInvestigador,'/api/orchestrator/register/notificacioninvestigador/<int:id_notificacioninvestigador>',endpoint='patch_notificacioninvestigador')
api.add_resource(FeedbackConvocatoria,'/api/orchestrator/register/feedback/<string:idconvocatoria>/<string:util>',endpoint='feedback_investigador')
api.add_resource(CalificacionArea,'/api/orchestrator/register/calificacion/area',endpoint='calificacion_area')
api.add_resource(CalificacionArea,'/api/orchestrator/register/calificacion/area/reset',endpoint='calificacion_area_reset')
api.add_resource(CalificacionArea,'/api/orchestrator/register/calificacion/area/<int:id_calificacion>',endpoint='get_calificacion_area')
api.add_resource(CalificacionArea,'/api/orchestrator/register/calificacion/area/<int:id_calificacion>',endpoint='patch_calificacion_area')
api.add_resource(CalificacionConvocatoria,'/api/orchestrator/register/calificacion/convocatoria',endpoint='calificacion_convocatoria')
api.add_resource(CalificacionConvocatoria,'/api/orchestrator/register/calificacion/convocatoria/<int:id_calificacion>',endpoint='get_calificacion_convocatoria')
api.add_resource(CalificacionConvocatoria,'/api/orchestrator/register/calificacion/convocatoria/<int:id_calificacion>',endpoint='patch_calificacion_convocatoria')
api.add_resource(Ejecucion_Boletin,'/api/orchestrator/register/ejecuciones_boletines',endpoint='ejecuciones_boletines')
api.add_resource(Ejecucion_Boletin,'/api/orchestrator/register/ejecucion_boletin/<int:id_notificacion>',endpoint='get_ejecucion_boletin')
api.add_resource(Ejecucion_Boletin,'/api/orchestrator/register/ejecucion_boletin/<int:id_notificacion>',endpoint='patch_ejecucion_boletin')
api.add_resource(Ultima_Ejecucion_Boletin,'/api/orchestrator/register/ultima_ejecucion_boletin',endpoint='ultima_ejecucion_boletin')
api.add_resource(Token,'/api/orchestrator/register/token',endpoint='get_token')
api.add_resource(PerfilRecomendacion,'/api/orchestrator/register/profile',endpoint='get_profile_recomendation')
api.add_resource(InvestigadorPerfil,'/api/orchestrator/register/profile/investigadores',endpoint='get_profile_recomendation_all')
api.add_resource(ProcessConfigResource,'/api/orchestrator/register/config',endpoint='process_config_list')
