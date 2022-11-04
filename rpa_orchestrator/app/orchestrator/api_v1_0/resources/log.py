from pickle import TRUE
from flask                              import Blueprint, abort
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource, fields
from model.DocInfo import DocInfo
from rpa_orchestrator.orchestrator    import Orchestrator
from marshmallow import Schema, fields
from flask_apispec import marshal_with,doc, use_kwargs
from flask_apispec.views import MethodResource

orch = Orchestrator()

class LogSchema(Schema):
    """
    Clase esquema para representar los logs.
    """
    id = fields.Int()
    id_schedule = fields.Int()
    id_robot = fields.Str(default='robot1')
    log_file_path = fields.Str(default='30-07-2022-073359ProcessSexenios.log')
    process_name = fields.Str(default='ProcessSexenios')
    start_time = fields.Float()
    end_time = fields.Float()
    completed = fields.Int()
    state = fields.Str()
    finished = fields.Boolean()

class LogListResponseSchema(Schema):
    """
    Clase esquema para representar una array de logs.
    """
    log = fields.Nested(LogSchema,many=True)

class LogRequestSchema(Schema):
    """
    Clase esquema para representar el tipo de api.
    """
    api_type = fields.String(required=True, description="API type of awesome API")


log_v1_0_bp = Blueprint('log_v1_0_bp', __name__)
api = Api(log_v1_0_bp)

def getBlueprint():
    return log_v1_0_bp

def isDocumented():
    return TRUE

class LogListResource(MethodResource,Resource):
    @doc(description='Get Log list', tags=['Logs'])
    @marshal_with(LogSchema(many=True))  # marshalling with marshmallow library
    def get(self):
        '''
        Método get para el listado de log
        '''
        return Response(orch.get_log(),mimetype='application/json')

class LogResource(MethodResource,Resource):
    @doc(description='Get Log por id', tags=['Logs'],params={'log_id': 
            {
                'description': 'id del log',
                'example': '5'
            }
        })
    @marshal_with(LogSchema)  # marshalling with marshmallow library
    def get(self,log_id):
        '''
        Método get para el listado de log por id
        '''
        resp = orch.get_log(log_id)
        if resp is None:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

def getDocInfo():
    """
    Método abstracto para crear las entradas en Swagger.
    """
    doc_info_list = []
    ep1 = DocInfo(doc_class = LogListResource,doc_blueprint=log_v1_0_bp.name, doc_endpoint='log_list_resource')
    ep2 = DocInfo(doc_class = LogResource,doc_blueprint=log_v1_0_bp.name, doc_endpoint='log_resource')
    doc_info_list.append(ep1)
    doc_info_list.append(ep2)
    return doc_info_list

api.add_resource(LogListResource,'/api/orchestrator/logs', endpoint='log_list_resource')
api.add_resource(LogResource,'/api/orchestrator/logs/<int:log_id>', endpoint='log_resource')