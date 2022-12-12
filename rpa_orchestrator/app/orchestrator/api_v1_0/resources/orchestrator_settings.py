import json
from flask                                 import request, Blueprint, abort
from flask.wrappers                        import Response
from flask_restful                         import Api, Resource
from rpa_orchestrator.orchestrator         import Orchestrator
from model.DocInfo                         import DocInfo
from marshmallow                           import Schema, fields
from flask_apispec                         import marshal_with,doc, use_kwargs
from flask_apispec.views                   import MethodResource
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import token_required
orch = Orchestrator()

orchestrator_settings_v1_0_bp = Blueprint('orchestrator_settings_v1_0_bp', __name__)
api = Api(orchestrator_settings_v1_0_bp)

def getBlueprint():
    return orchestrator_settings_v1_0_bp

class AMQPSettingsSchema(Schema):
    """
    Clase esquema de la configuración de AMQP.
    """
    user = fields.Str()
    password = fields.Str()
    host = fields.Str()
    port = fields.Int()
    subscriptions = fields.List(fields.Str())
    exchange_name = fields.Str()
    queue_name = fields.Str()

class DBPersistenceSettingsSchema(Schema):
    """
    Clase esquema de la configuración de la persistencia DB.
    """
    user = fields.Str()
    password = fields.Str()
    host = fields.Str()
    port = fields.Int()
    database = fields.Str()

class DBBISettingsSchema(Schema):
    """
    Clase esquema de la configuración de la persistencia BI.
    """
    username = fields.Str()
    password = fields.Str()
    host = fields.Str()
    port = fields.Int()
    keyspace = fields.Str()

class OrchestratorSettingsSchema(Schema):
    """
    Clase esquema de la configuración del orquestador.
    """
    id_orch = fields.Str()
    name = fields.Str()
    company = fields.Str()
    pathlog_store = fields.Str()
    cdn_url = fields.Str()
    
class ProcessGeneralSettingsSchema(Schema):
    """
    Clase esquema de la configuración general de los procesos
    """
    salaprensa_url = fields.Str()
    ucc_url = fields.Str()
    boe_url = fields.Str()
    bdns_url = fields.Str()
    bdns_search = fields.Str()
    europe_url = fields.Str()
    europe_link = fields.Str()

class AMQPSettingsResource(MethodResource, Resource):
    @token_required
    @doc(description='Mostrar configuraciones AMQP', tags=['Orch Settings'])
    @marshal_with(AMQPSettingsSchema)
    def get(self,id = 1):
        """
        Método para extraer la información sobre las conexiones amqp.
        """
        amqp_settings = orch.get_amqp_settings_by_id(id)
        resp = {}
        resp = amqp_settings.__dict__.copy()
        return Response(json.dumps(resp), status=200, mimetype='application/json')

    @token_required
    @doc(description='Cambio de un parámetro de AMQP', tags=['Orch Settings'])
    @use_kwargs(AMQPSettingsSchema, location=('json'))
    @marshal_with(AMQPSettingsSchema)
    def patch(self, id_settings = 1, **kwargs):
        """
        Método para editar algún parámetro de AMQP.
        """
        new_parameters = request.get_json()
        black_list = ['id']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = orch.update_amqp_settings(id_settings, new_parameters)
        if not resp:
            abort(404, description="Error intentado actualizar los ajustes globales con id "+str(id_settings))
        resp = json.dumps({"status": "ok", "amqp_settings": id_settings, "descripcion":"Ajustes AMQP actualizados"})
        return Response(resp,mimetype='application/json')


class DBProcessResource(MethodResource, Resource):
    @token_required
    @doc(description='Mostrar las configuraciones de la persistencia de procesos', tags=['Orch Settings'])
    @marshal_with(DBPersistenceSettingsSchema)
    def get(self,id = 1):
        """
        Método para obtener la configuración de base de datos.
        """
        dbprocess_settings = orch.get_dbprocess_settings_by_id(id)
        resp = {}
        resp = dbprocess_settings.__dict__.copy()
        return Response(json.dumps(resp), status=200, mimetype='application/json')

    @token_required
    @doc(description='Cambio de un parámetro de la persistencia de procesos', tags=['Orch Settings'])
    @use_kwargs(DBPersistenceSettingsSchema, location=('json'))
    @marshal_with(DBPersistenceSettingsSchema)
    def patch(self, id_settings = 1, **kwargs):
        """
        Método para editar parámetros de la persistencia.
        """
        new_parameters = request.get_json()
        black_list = ['id']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = orch.update_dbprocess_settings(id_settings, new_parameters)
        if not resp:
            abort(404, description="Error intentado actualizar los ajustes globales con id "+str(id_settings))
        resp = json.dumps({"status": "ok", "dbprocess_settings": id_settings, "descripcion":"Ajustes DB PROCESS actualizados"})
        return Response(resp,mimetype='application/json')

class DBBIResource(MethodResource, Resource):
    @token_required
    @doc(description='Mostrar la configuración de la persistencia BI', tags=['Orch Settings'])
    @marshal_with(DBBISettingsSchema)
    def get(self,id = 1):
        """
        Método para obtener la configuración de base de datos BI.
        """
        dbbi_settings = orch.get_dbbi_settings_by_id(id)
        resp = {}
        resp = dbbi_settings.__dict__.copy()
        return Response(json.dumps(resp), status=200, mimetype='application/json')

    @token_required
    @doc(description='Cambio de un parámetro de la persistencia BI', tags=['Orch Settings'])
    @use_kwargs(DBBISettingsSchema, location=('json'))
    @marshal_with(DBBISettingsSchema)
    def patch(self, id_settings = 1, **kwargs):
        """
        Método para editar parámetros de la persistencia BI.
        """
        new_parameters = request.get_json()
        black_list = ['id']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = orch.update_dbbi_settings(id_settings, new_parameters)
        if not resp:
            abort(404, description="Error intentado actualizar los ajustes globales con id "+str(id_settings))
        resp = json.dumps({"status": "ok", "dbbi_settings": id_settings, "descripcion":"Ajustes  DBBI actualizados"})
        return Response(resp,mimetype='application/json')


class OrchestratorSettingsResource(MethodResource, Resource):
    @token_required
    @doc(description='Mostrar la configuración del orquestador', tags=['Orch Settings'])
    @marshal_with(OrchestratorSettingsSchema)
    def get(self,id = 1):
        """
        Método para obtener la configuración del orquestador.
        """
        orchestrator_settings = orch.get_orchestrator_settings_by_id(id)
        resp = {}
        resp = orchestrator_settings.__dict__.copy()
        return Response(json.dumps(resp), status=200, mimetype='application/json')

    @token_required
    @doc(description='Cambio de un parámetro de la configuración del orquestador', tags=['Orch Settings'])
    @use_kwargs(OrchestratorSettingsSchema, location=('json'))
    @marshal_with(OrchestratorSettingsSchema)
    def patch(self, id_settings = 1, **kwargs):
        """
        Método para editar parámetros de la configuración del orquestador.
        """
        new_parameters = request.get_json()
        black_list = ['id']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = orch.update_orchestrator_settings(id_settings, new_parameters)
        if not resp:
            abort(404, description="Error intentado actualizar los ajustes globales con id "+str(id_settings))
        resp = json.dumps({"status": "ok", "orchestrator_settings": id_settings, "descripcion":"Ajustes del orquestador actualizados"})
        return Response(resp,mimetype='application/json')

class ProcessSettingsResource(MethodResource, Resource):
    @token_required
    @doc(description='Mostrar la configuración general de los procesos', tags=['Orch Settings'])
    @marshal_with(ProcessGeneralSettingsSchema)
    def get(self,id = 1):
        """
        Método para obtener la configuración de los procesos.
        """
        process_settings = orch.get_process_settings_by_id(id)
        resp = {}
        resp = process_settings.__dict__.copy()
        return Response(json.dumps(resp), status=200, mimetype='application/json')

    @token_required
    @doc(description='Editar la configuración general de los procesos', tags=['Orch Settings'])
    @marshal_with(ProcessGeneralSettingsSchema)
    def patch(self, id_settings = 1, **kwargs):
        """
        Método para editar la configuración de los procesos.
        """
        new_parameters = request.get_json()
        black_list = ['id']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = orch.update_process_settings(id_settings, new_parameters)
        if not resp:
            abort(404, description="Error intentado actualizar los ajustes de proceso con id "+str(id_settings))
        resp = json.dumps({"status": "ok", "process_settings": id_settings, "descripcion":"Ajustes de proceso actualizados"})
        return Response(resp,mimetype='application/json')


def getDocInfo():
    """
    Método abstracto para crear las entradas en Swagger.
    """
    doc_info_list = []
    ep1 = DocInfo(doc_class = AMQPSettingsResource, doc_blueprint='orchestrator_settings_v1_0_bp', doc_endpoint='amqp_settings_resource')
    ep3 = DocInfo(doc_class = DBProcessResource, doc_blueprint='orchestrator_settings_v1_0_bp', doc_endpoint='dbprocess_settings_resource')
    ep4 = DocInfo(doc_class = DBBIResource, doc_blueprint='orchestrator_settings_v1_0_bp', doc_endpoint='dbbi_settings_resource')
    ep5 = DocInfo(doc_class = OrchestratorSettingsResource, doc_blueprint='orchestrator_settings_v1_0_bp', doc_endpoint='orchestrator_settings_resource')
    ep6 = DocInfo(doc_class = ProcessSettingsResource, doc_blueprint='orchestrator_settings_v1_0_bp', doc_endpoint='process_settings_resource')

    doc_info_list.append(ep1)
    doc_info_list.append(ep3)
    doc_info_list.append(ep4)
    doc_info_list.append(ep5)
    doc_info_list.append(ep6)
    return doc_info_list

api.add_resource(AMQPSettingsResource, '/api/orchestrator/amqp_settings/',endpoint='amqp_settings_resource')
api.add_resource(DBProcessResource, '/api/orchestrator/dbprocess_settings/',endpoint='dbprocess_settings_resource')
api.add_resource(DBBIResource, '/api/orchestrator/dbbi_settings/',endpoint='dbbi_settings_resource')
api.add_resource(OrchestratorSettingsResource, '/api/orchestrator/orchestrator_settings/',endpoint='orchestrator_settings_resource')
api.add_resource(ProcessSettingsResource, '/api/orchestrator/process_settings/',endpoint='process_settings_resource')