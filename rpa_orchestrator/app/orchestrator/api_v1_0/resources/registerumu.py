import json
from datetime                               import datetime
from rpa_orchestrator.ControllerProcess    import ControllerProcess
from flask                                  import Blueprint, request, abort
from flask.wrappers                         import Response
from flask_restful                          import Api, Resource
from rpa_orchestrator.ControllerProcess    import ControllerProcess
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import validate_create_process, validate_edit_process
import rpa_orchestrator.lib.dbprocess.models as model

cp = ControllerProcess()
registerumu_v1_0_bp = Blueprint('registerumu_v1_0_bp', __name__)
api = Api(registerumu_v1_0_bp)

def getBlueprint():
    return registerumu_v1_0_bp

class SGI(Resource):
    def get(self, id_sgi):
        filter = {}
        if not id_sgi:
            arguments = {"id": int, "id_sgi": str, "url":str, "fecha_creacion":datetime}
            for (key, value) in arguments.items():
                if request.args.get(key)=="null":
                    filter[key] = None
                if not request.args.get(key) or request.args.get(key)=="null":
                    if not request.args.get(key):
                        filter[key] = None
                    elif value is bool:
                        filter[key] = request.args.get(key) in ['true','True'] #Lo tratamos como string para sacar que booleano es.
                    elif value is datetime:
                        filter[key] = datetime.fromtimestamp(request.args.get(key)).isoformat()
                    else:
                        filter[key] = request.args.get(key, type = value)
        else:
            filter['id'] = id_sgi
        resp = cp.get_sgi(filter)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

    def post(self):
        sgi_list = json.dumps(request.get_json(force=True))
        try:
            sgi_list = json.loads(sgi_list, object_hook=lambda d: model.Sgi(**d))
            cp.dump(sgi_list)
            resp = json.dumps({"status": "ok", "sgi": [x.id for x in sgi_list], "description":"SGI Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            abort(400, description=str(e))
    
    def patch(self, id_sgi):
        new_parameters = request.get_json()
        black_list = ['id','fecha_creacion']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_sgi(id_sgi, new_parameters)
        if not resp:
            abort(404, description="Error intentado actualizar la sgi_convocatoria con id "+str(id_sgi))
        resp = json.dumps({"status": "ok", "SGI": id_sgi, "description":"SGI Updated"})
        return Response(resp,mimetype='application/json')

class Convocatoria(Resource):
    def get(self, id_convocatoria = None):
        filter = {}
        if not id_convocatoria:
            arguments = {"id": int, "fecha_creacion": datetime, "fecha_publicacion": datetime, "titulo": str, "_from": str, "url":str, "entidad_gestora":str, 
                        "entidad_convocante":str, "area_tematica":str, "observaciones":str, "sgiid": int, "basereguladora":int, "notificada":bool, "unidad_gestion":str, "modelo_ejecucion":str}
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
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

    def post(self):
        convocatoria_list = json.dumps(request.get_json(force=True))
        try:
            convocatoria_list = json.loads(convocatoria_list, object_hook=lambda d: model.Convocatoria(**d))
            cp.dump(convocatoria_list)
            resp = json.dumps({"status": "ok", "convocatoria": [x.id for x in convocatoria_list], "description":"Convocatoria Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            abort(400, description=str(e))

    def patch(self, id_convocatoria):
        new_parameters = request.get_json()
        black_list = ['id','fecha_creacion']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_convocatoria(id_convocatoria, new_parameters)
        if not resp:
            abort(404, description="Error intentado actualizar la convocatoria con id "+str(id_convocatoria))
        resp = json.dumps({"status": "ok", "convocatoria": id_convocatoria, "description":"Convocatoria Updated"})
        return Response(resp,mimetype='application/json')


class Solicitud(Resource):
    def get(self, id_solicitud = None):
        filter = {}
        if not id_solicitud:
            arguments = {"id": int, "id_solicitud": int, "email": str, "concesion":bool, "referencia_proyecto": str, "IP": str, "fecha_creacion": datetime, "sgiid": int}
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
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')
    
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

    def patch(self, id_solicitud):
        new_parameters = request.get_json()
        black_list = ['id','fecha_creacion']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_solicitud(id_solicitud, new_parameters)
        if not resp:
            abort(404, description="Error intentado actualizar la solicitud con id "+str(id_solicitud))
        resp = json.dumps({"status": "ok", "Solicitud": id_solicitud, "description":"Solicitud Updated"})
        return Response(resp,mimetype='application/json')


class Base_Reguladora(Resource):
    def get(self, id_basereguladora = None):
        filter = {}
        if not id_basereguladora:
            arguments = {"id": int, "id_base": str, "fecha_creacion": datetime, "titulo": str, "url": str, "notificada":bool}
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
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')
    
    def post(self):
        basereguladora_list = json.dumps(request.get_json(force=True))
        try:
            basereguladora_list = json.loads(basereguladora_list, object_hook=lambda d: model.Basereguladora(**d))
            cp.dump(basereguladora_list)
            resp = json.dumps({"status": "ok", "BaseReguladora": [x.id for x in basereguladora_list], "description":"Base Reguladora Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            abort(400, description=str(e))

    def patch(self, id_basereguladora):
        new_parameters = request.get_json()
        black_list = ['id','fecha_creacion']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_basereguladora(id_basereguladora, new_parameters)
        if not resp:
            abort(404, description="Error intentado actualizar la base reguladora con id "+str(id_basereguladora))
        resp = json.dumps({"status": "ok", "Base Reguladora": id_basereguladora, "description":"Base Reguladora Updated"})
        return Response(resp,mimetype='application/json')

class Noticia(Resource):
    def get(self, id_noticia = None):
        filter = {}
        if not id_noticia:
            arguments = {"id": int, "titulo": str, "url": str, "autor": str,"fecha": datetime, "notificada":bool}
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
            filter['id'] = id_noticia
        resp = cp.get_noticia(filter)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')
    
    def post(self):
        noticia_list = json.dumps(request.get_json(force=True))
        try:
            noticia_list = json.loads(noticia_list, object_hook=lambda d: model.Noticia(**d))
            cp.dump(noticia_list)
            resp = json.dumps({"status": "ok", "Noticias": [x.id for x in noticia_list], "description":"Noticia Created"})
            return Response(resp, status=201, mimetype='application/json')
        except Exception as e:
            abort(400, description=str(e))

    def patch(self, id_noticia):
        new_parameters = request.get_json()
        black_list = ['id','fecha_creacion']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = cp.update_noticia(id_noticia, new_parameters)
        if not resp:
            abort(404, description="Error intentado actualizar la noticia con id "+str(id_noticia))
        resp = json.dumps({"status": "ok", "Noticia": id_noticia, "description":"Noticia Updated"})
        return Response(resp,mimetype='application/json')


api.add_resource(SGI,'/api/orchestrator/register/sgi_convocatorias/<int:id_solicitud>',endpoint='sgi_convocatorias')
api.add_resource(SGI,'/api/orchestrator/register/sgi_convocatoria/<int:id_solicitud>',endpoint='get_sgi_convocatoria')
api.add_resource(SGI,'/api/orchestrator/register/sgi_convocatoria/<int:id_solicitud>',endpoint='patch_sgi_convocatoria')
api.add_resource(Convocatoria,'/api/orchestrator/register/convocatorias',endpoint='convocatorias')
api.add_resource(Convocatoria,'/api/orchestrator/register/convocatoria/<int:id_convocatoria>',endpoint='patch_convocatoria')
api.add_resource(Convocatoria,'/api/orchestrator/register/convocatoria/<int:id_convocatoria>',endpoint='get_convocatoria')
api.add_resource(Solicitud,'/api/orchestrator/register/solicitudes',endpoint='solicitudes')
api.add_resource(Solicitud,'/api/orchestrator/register/solicitud/<int:id_solicitud>',endpoint='get_solicitud')
api.add_resource(Solicitud,'/api/orchestrator/register/solicitud/<int:id_solicitud>',endpoint='patch_solicitud')
api.add_resource(Base_Reguladora,'/api/orchestrator/register/basesreguladoras',endpoint='basesreguladoras')
api.add_resource(Base_Reguladora,'/api/orchestrator/register/basereguladora/<int:id_basereguladora>',endpoint='get_basereguladora')
api.add_resource(Base_Reguladora,'/api/orchestrator/register/basereguladora/<int:id_basereguladora>',endpoint='patch_basereguladora')
api.add_resource(Noticia,'/api/orchestrator/register/noticias',endpoint='noticias')
api.add_resource(Noticia,'/api/orchestrator/register/noticia/<int:id_noticia>',endpoint='get_noticia')
api.add_resource(Noticia,'/api/orchestrator/register/noticia/<int:id_noticia>',endpoint='patch_noticia')
