import json
from flask                              import Blueprint, abort
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from flask import request
from rpa_orchestrator.orchestrator      import Orchestrator
from marshmallow                        import Schema, fields
from flask_apispec                      import marshal_with,doc
from flask_apispec.views                import MethodResource
from model.DocInfo                      import DocInfo
from rpa_orchestrator.app.orchestrator.api_v1_0.resources.log import LogSchema
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import token_required

orch = Orchestrator()
robot_v1_0_bp = Blueprint('robot_v1_0_bp', __name__)
api = Api(robot_v1_0_bp)

def getBlueprint():
    return robot_v1_0_bp

class ProcessRunningSchema(Schema):
    """
    Clase esquema para representar un proceso corriendo.
    """
    id = fields.Int()
    name = fields.Str()
    id_log = fields.Int()

class RobotListResourceSchema(Schema):
    """
    Clase esquema para representar un robot.
    """
    robot_name = fields.Str(allow_none=True,missing=True)
    robot_id = fields.Str()
    robot_address = fields.Str()
    robot_online = fields.Bool()
    time_online = fields.Float()
    last_seen = fields.Float()
    process_running = fields.Nested(ProcessRunningSchema,allow_none=True)

class ProblemResourceSchema(Schema):
    """
    Clase esquema para representar la gestión de problemas.
    """
    robot_id = fields.Str()
    execution_id = fields.Int()
    process_id = fields.Int()
    process_name = fields.Str()
    log = fields.Int()
    msg = fields.Str()
    ts = fields.Float()

class StadisticSchema(Schema):
    """
    Clase esquema para representar las estadísticas técnicas de un robot.
    """
    cpu = fields.List(fields.Float())
    ram = fields.List(fields.Float())
    disk = fields.List(fields.Float())

class ExecutionSchema(Schema):
    """
    Clase esquema para representar la ejecución de procesos.
    """
    execution_id = fields.Int()
    process = fields.Str()
    success = fields.Bool()
    log = fields.Int()
    ts = fields.Float()

class RobotResourceSchema(Schema):
    """
    Clase esquema para representar los recursos y características de un robot.
    """
    name = fields.Str()
    id = fields.Str()
    ip_address = fields.Str()
    address = fields.Str()
    os = fields.Str()
    registrations = fields.Str()
    mac = fields.Str()
    python_version = fields.Str()
    online = fields.Bool()
    time_online = fields.Float()
    last_seen = fields.Float()
    process_running = fields.List(fields.Nested(ProcessRunningSchema),allow_none=True)
    process_queue = fields.List(fields.Nested(ProcessRunningSchema),allow_none=True)
    problems = fields.List(fields.Nested(ProblemResourceSchema))
    last_executions = fields.List(fields.Nested(ExecutionSchema))
    stats = fields.Nested(ExecutionSchema)

class RobotLogSchema(Schema):
    """
    Clase esquema para representar el esquema de los logs de un robot.
    """
    id = fields.Int()
    id_schedule = fields.Int()
    id_process = fields.Int()
    id_robot = fields.Str()
    log_file_path = fields.Str()
    process_name = fields.Str()
    data = fields.Str()
    start_time = fields.Float()
    data_listener = fields.Str(allow_none=True,missing=True)
    end_time = fields.Float()
    completed = fields.Int()
    state = fields.Str()
    finished = fields.Bool()


class RobotListResource(MethodResource, Resource):
    @token_required
    @doc(description='Obtener lista de robots', tags=['Robot'])
    @marshal_with(RobotListResourceSchema(many=True))
    def get(self):
        """
        Método para recopilar todos los robots registrados en el sistema.
        """
        result = orch.get_all_robots()
        result = Response(result,mimetype='application/json')
        return result

class RobotListProblemResource(MethodResource, Resource):
    @token_required
    @doc(description='Obtener lista de problemas de todos los robots', tags=['Robot'])
    @marshal_with(ProblemResourceSchema(many=True))
    def get(self):
        """
        Método para recopilar todos los problemas que pueda notificar un robot
        """
        result = orch.get_robot_problems()
        result = Response(result,mimetype='application/json')
        return result

class RobotResource(MethodResource, Resource):
    @token_required
    @doc(description='Obtener datos y características de un robot', tags=['Robot'])
    @marshal_with(RobotResourceSchema)
    def get(self,robot_id):
        """
        Método para recopilar los datos y características de un robot en concreto.
        """
        resp = orch.get_robot(robot_id)
        if resp is None:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

class RobotProblemResource(MethodResource, Resource):
    @token_required
    @doc(description='Obtener problemas notificados de un robot', tags=['Robot'])
    @marshal_with(ProblemResourceSchema(many=True))
    def get(self,robot_id):
        """
        Método para recopilar los problemas que han sido notificados por un robot concreto.
        """
        resp = orch.get_robot_problems(robot_id)
        if resp is None:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

class RobotLogResource(MethodResource, Resource):
    @token_required
    @doc(description='Obtener logs generados de un robot', tags=['Robot'])
    @marshal_with(RobotLogSchema(many=True))
    def get(self,robot_id):
        """
        Método para recopilar los logs generados por un robot concreto.
        """
        resp = orch.get_all_logs_by_idrobot(robot_id)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

def getDocInfo():
    """
    Método abstracto para crear las entradas en Swagger.
    """
    doc_info_list = []
    ep1 = DocInfo(doc_class = RobotListResource, doc_blueprint='robot_v1_0_bp', doc_endpoint = 'robot_list_resource')
    ep2 = DocInfo(doc_class = RobotListProblemResource, doc_blueprint='robot_v1_0_bp', doc_endpoint='robot_list_problems_resource')
    ep3 = DocInfo(doc_class = RobotResource, doc_blueprint='robot_v1_0_bp', doc_endpoint='robot_resource')
    ep4 = DocInfo(doc_class = RobotProblemResource, doc_blueprint='robot_v1_0_bp', doc_endpoint='robot_problems_resource')
    ep5 = DocInfo(doc_class = RobotLogResource, doc_blueprint='robot_v1_0_bp', doc_endpoint='robot_log_resource')

    doc_info_list.append(ep1)
    doc_info_list.append(ep2)
    doc_info_list.append(ep3)
    doc_info_list.append(ep4)
    doc_info_list.append(ep5)
    return doc_info_list

api.add_resource(RobotListResource, '/api/orchestrator/robots/', endpoint='robot_list_resource')
api.add_resource(RobotListProblemResource, '/api/orchestrator/robots/problems', endpoint='robot_list_problems_resource')
api.add_resource(RobotResource, '/api/orchestrator/robots/<string:robot_id>', endpoint='robot_resource')
api.add_resource(RobotProblemResource, '/api/orchestrator/robots/<string:robot_id>/problems', endpoint='robot_problems_resource')
api.add_resource(RobotLogResource, '/api/orchestrator/robots/<string:robot_id>/logs', endpoint='robot_log_resource')
