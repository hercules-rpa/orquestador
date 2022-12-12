from distutils.log import FATAL
import json
from flask                              import Blueprint, request, abort
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator      import Orchestrator
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import validate_create_process, validate_edit_process
from marshmallow                        import Schema, fields
from flask_apispec                      import marshal_with,doc, use_kwargs
from flask_apispec.views                import MethodResource
from model.DocInfo                      import DocInfo
from rpa_orchestrator.app.orchestrator.api_v1_0.resources.log import LogSchema
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import token_required
orch = Orchestrator()

process_v1_0_bp = Blueprint('process_v1_0_bp', __name__)
api = Api(process_v1_0_bp)

def getBlueprint():
    return process_v1_0_bp

class ProcessSchema(Schema):
    """
    Clase esquema con la información de un proceso.
    """
    process_id = fields.Int()
    process_class_name = fields.Str()
    process_name = fields.Str()
    process_description = fields.Str()
    required = fields.List(fields.Str())
    capable_robots = fields.List(fields.Str())
    visible = fields.Bool()
    settings = fields.Bool()

class ProcessScheduleSchema(Schema):
    """
    Clase esquema con la información de programación de un proceso.
    """
    id = fields.Int()
    id_robot = fields.Str(allow_none=True,missing=True)
    created = fields.Float()
    process_name = fields.Str()
    id_process = fields.Int()
    priority = fields.Int()
    active = fields.Bool()
    time_schedule = fields.Float()
    logs = fields.List(fields.Nested(LogSchema))
    next_run = fields.Float()
    

class ProcessPostSchema(Schema):
    """
    Clase esquema para añadir un proceso a ejecución.
    """
    id_robot = fields.Str(allow_none=True,missing=True)
    id_process = fields.Int()
    priority = fields.Int()
    exclude_robots = fields.List(fields.Str())
    parameters = fields.Raw(allow_none=True,missing=True)

class TimeScheduleSchema(Schema):
    """
    Clase esquema con el tiempo que se necesita para agendar un proceso.
    """
    every = fields.Raw()
    at = fields.Raw(allow_none=True,missing=True)
    forever = fields.Bool()
    tag = fields.Str()
    category = fields.Str()

class ProcessReceiveSchema(Schema):
    """
    Clase esquema para recibir la respuesta.
    """
    status = fields.Str()
    schedule_id = fields.Int()
    description = fields.Str()

class ProcessSchedulePostSchema(Schema):
    """
    Clase esquema para agendar un proceso en un tiempo determinado.
    """
    time_schedule = fields.Nested(TimeScheduleSchema,allow_none=True,missing=True)
    process = fields.Nested(ProcessPostSchema)

class ProcessListResource(MethodResource, Resource):
    @token_required
    @doc(description='Muestra la lista de procesos disponibles', tags=['Process'])
    @marshal_with(ProcessSchema(many=True))
    def get(self):
        """
        Método que devuelve la lista de procesos que hay disponibles.
        """
        filter = None
        if request.args.get("visible") is not None:
            filter = request.args.get("visible") in ['true','True']
        
        data = orch.get_process(visible=filter)
        return Response(data,mimetype='application/json')


class ProcessResource(MethodResource, Resource):
    @token_required
    @doc(description='Muestra las características del proceso dado', tags=['Process'])
    @marshal_with(ProcessSchema)
    def get(self,process_id):
        """
        Método que devuelve la información de un proceso en concreto.
        """
        filter = None
        if request.args.get("visible") is not None:
            filter = request.args.get("visible") in ['true','True']
        data = orch.get_process(process_id, visible=filter)
        if data:
            return Response(data,mimetype='application/json')
        else:
            return Response("Resource not found",status=404,  mimetype='application/json')

class ProcessResourceForm(MethodResource, Resource):
    @token_required
    @doc(description='Muestra los formularios necesarios del proceso pasado por parámetro.', tags=['Process'])
    def get(self,process_id):
        """
        Método que devuelve el formulario que se utiliza para los procesos
        """
        resp = orch.get_process_form(process_id)
        if resp is None:
            abort(404, description="Resource not found")
        return Response(json.dumps(resp),mimetype='application/json')

class ScheduleResource(MethodResource, Resource):
    @token_required
    @doc(description='Muestra las características del proceso dado', tags=['Process'])
    @marshal_with(ProcessScheduleSchema)
    def get(self,schedule_id):
        """
        Método para consultar la información del proceso agendado.
        """
        resp = orch.get_schedule(schedule_id)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')
    
    @token_required
    @doc(description='Borra un proceso agendado para una marca de tiempo.', tags=['Process'])
    @marshal_with(ProcessScheduleSchema)
    def delete(self, schedule_id, **kwargs):
        """
        Método para borrar un proceso agendado para una marca de tiempo.
        """
        canceljob = orch.remove_schedule(schedule_id)
        if canceljob:
            resp = json.dumps({"status": "ok", "schedule_id": schedule_id, "description":"Removed Process "})
            return Response(resp,status=200,  mimetype='application/json')
        abort(404, description={"status": "ERROR", "schedule_id": schedule_id, "description":"Error removing process"})
    
    @token_required
    @doc(description='Muestra las características del proceso dado', tags=['Process'])
    @marshal_with(ProcessScheduleSchema)
    @validate_edit_process
    def patch(self, schedule_id, **kwargs):
        """
        Método para editar un proceso agendado para una marca de tiempo.
        """
        time_schedule = request.get_json(force=True)['time_schedule']
        process = request.get_json(force=True)['process']        
        if not "exclude_robots" in process:
            process['exclude_robots'] = []
        process_json = {
            "time_schedule":time_schedule,
            "process":process
        }
        if not orch.set_schedule(schedule_id, json.dumps(process_json)):
            abort(400, description={"status": "ERROR", "schedule_id": schedule_id, "description":"Error editing schedule"})

        resp = json.dumps({"status": "ok", "schedule_id": schedule_id, "description":"Job Edited "})
        return Response(resp, status=201, mimetype='application/json')

class ScheduleExecuteResource(MethodResource,Resource):   
    @token_required
    @doc(description='Establecer un proceso para que se ejecute en una marca de tiempo', tags=['Process'])
    @use_kwargs(ProcessSchedulePostSchema, location=('json'))
    @marshal_with(ProcessReceiveSchema)
    @validate_create_process
    def post(self, **kwargs):
        """
        Método para establecer un proceso en una marca de tiempo determinada.
        """
        time_schedule = request.get_json(force=True)['time_schedule']
        process = request.get_json(force=True)['process']

        if not "exclude_robots" in process:
            process['exclude_robots'] = []

        process_json = {
            "time_schedule":time_schedule,
            "process":process
        }
        
        id_schedule = orch.add_process(json.dumps(process_json))
        if id_schedule is None:
            abort(400, description="Error creando proceso. Mal formado el schedule, robot offline o no existe")

        resp = json.dumps({"status": "ok", "schedule_id": id_schedule, "description":"Job Created "})
        return Response(resp, status=201, mimetype='application/json')

class ScheduleListFilterResource(MethodResource, Resource):
    @token_required
    @doc(description='Muestra todos los procesos que han sido agendados.', tags=['Process'])
    @marshal_with(ProcessScheduleSchema)
    def get(self):
        arguments = {"id": int, "created": float, "process_name":str, "id_process":int, "priority":int, "active":bool, "limit": int}
        filter = {}
        for (key, value) in arguments.items():
            if request.args.get(key, type = value):
                if value is bool:
                    filter[key] = request.args.get(key) in ['true','True'] #Lo tratamos como string para sacar que booleano es.
                else:
                    filter[key] = request.args.get(key, type = value)
        resp = orch.get_all_schedules(filter)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')
        
class ScheduleListResource(MethodResource, Resource):
    @token_required
    def get(self):
        resp = orch.get_all_schedules()
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

class ScheduleLogResource(MethodResource, Resource):
    @token_required
    @doc(description='Muestra todos los logs de un proceso que han sido agendado.', tags=['Process'])
    @marshal_with(LogSchema(many=True))
    def get(self,schedule_id):
        resp = orch.get_all_logs_by_idschedule(schedule_id)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

class ScheduleRobotResource(MethodResource, Resource):
    @token_required
    @doc(description='Borra un proceso agendado para una marca de tiempo en un robot concreto.', tags=['Process'])
    @marshal_with(ProcessReceiveSchema)
    def delete(self,robot_id, schedule_id):
        resp = orch.remove_process_robot(robot_id, schedule_id)
        if resp:
            resp = json.dumps({"status": "ok", "schedule_id": schedule_id, "description":"Process remove from robot", "robot": robot_id})
            return Response(resp, status=201, mimetype='application/json')
        abort(400, description={"status": "error", "schedule_id": schedule_id, "description":"Error removing process from robot ", "robot": robot_id})


def getDocInfo():
    """
    Método abstracto para crear las entradas en Swagger.
    """
    doc_info_list = []
    ep1 = DocInfo(doc_class = ProcessListResource, doc_blueprint='process_v1_0_bp', doc_endpoint='process_resource_list')
    ep2 = DocInfo(doc_class = ProcessResource, doc_blueprint='process_v1_0_bp', doc_endpoint='process_resource')
    ep3 = DocInfo(doc_class = ProcessResourceForm, doc_blueprint='process_v1_0_bp', doc_endpoint='process_resource_form')
    ep4 = DocInfo(doc_class = ScheduleResource, doc_blueprint='process_v1_0_bp', doc_endpoint='schedule_resource')
    ep5 = DocInfo(doc_class = ScheduleListFilterResource, doc_blueprint='process_v1_0_bp', doc_endpoint='schedule_list_resource_filter')
    ep6 = DocInfo(doc_class = ScheduleListResource, doc_blueprint='process_v1_0_bp', doc_endpoint='schedule_list_resource')
    ep7 = DocInfo(doc_class = ScheduleLogResource, doc_blueprint='process_v1_0_bp', doc_endpoint='schedule_logs_resource')
    ep8 = DocInfo(doc_class = ScheduleRobotResource, doc_blueprint='process_v1_0_bp', doc_endpoint='robot_remove_process_resource')
    ep9 = DocInfo(doc_class = ScheduleExecuteResource, doc_blueprint='process_v1_0_bp', doc_endpoint='process_run_resource')

    doc_info_list.append(ep1)
    doc_info_list.append(ep2)
    doc_info_list.append(ep3)
    doc_info_list.append(ep4)
    doc_info_list.append(ep5)
    #doc_info_list.append(ep6)
    doc_info_list.append(ep7)
    doc_info_list.append(ep8)
    doc_info_list.append(ep9)
    return doc_info_list

api.add_resource(ProcessListResource,'/api/orchestrator/process/', endpoint='process_resource_list')
api.add_resource(ProcessResource,'/api/orchestrator/process/<int:process_id>',endpoint='process_resource')
api.add_resource(ProcessResourceForm,'/api/orchestrator/process/<int:process_id>/form',endpoint='process_resource_form')
api.add_resource(ScheduleResource, '/api/orchestrator/schedules/<int:schedule_id>',endpoint='schedule_resource')
#api.add_resource(ScheduleResource, '/api/orchestrator/schedules/<int:schedule_id>',endpoint='process_edit_resource') #nueva typo patch
#api.add_resource(ScheduleResource, '/api/orchestrator/schedules/<int:schedule_id>',endpoint='process_remove_resource') #'/api/orchestrator/canceljob/<string:schedule_id>' -> '/api/orchestrator/schedules/<int:schedule_id>'
api.add_resource(ScheduleExecuteResource, '/api/orchestrator/schedules/execute',endpoint='process_run_resource') #'/api/orchestrator/robots/<string:robot_id>/execute' ->  /api/orchestrator/schedules/
api.add_resource(ScheduleListFilterResource,'/api/orchestrator/schedules',endpoint='schedule_list_resource_filter')
#api.add_resource(ScheduleListResource,'/api/orchestrator/schedules/',endpoint='schedule_list_resource')
api.add_resource(ScheduleLogResource,'/api/orchestrator/schedules/<int:schedule_id>/logs',endpoint='schedule_logs_resource')
api.add_resource(ScheduleRobotResource, '/api/orchestrator/robots/<string:robot_id>/schedules/<int:schedule_id>', endpoint='robot_remove_process_resource') #cambio /api/orchestrator/robots/removeprocess -> /api/orchestrator/robots/<string:robot_id>/schedules/<int:schedule_id> 
