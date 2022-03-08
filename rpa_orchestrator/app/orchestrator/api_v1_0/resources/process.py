import json
from flask                              import Blueprint, request, abort
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator    import Orchestrator
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import validate_create_process, validate_edit_process

orch = Orchestrator()

process_v1_0_bp = Blueprint('process_v1_0_bp', __name__)
api = Api(process_v1_0_bp)

def getBlueprint():
    return process_v1_0_bp

class ProcessListResource(Resource):
    def get(self):
        return Response(orch.get_process(),mimetype='application/json')

class ProcessResource(Resource):
    def get(self,process_id):
        resp = orch.get_process(process_id)
        if resp is None:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

class ProcessResourceForm(Resource):
    def get(self,process_id):
        resp = orch.get_process_form(process_id)
        if resp is None:
            abort(404, description="Resource not found")
        return Response(json.dumps(resp),mimetype='application/json')

class ScheduleResource(Resource):
    def get(self,schedule_id):
        resp = orch.get_schedule(schedule_id)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')
    
    @validate_create_process
    def post(self):
        time_schedule = request.get_json(force=True)['time_schedule']
        process = request.get_json(force=True)['process']
        print(time_schedule)
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
    
    def delete(self, schedule_id):
        canceljob = orch.remove_schedule(schedule_id)
        if canceljob:
            resp = json.dumps({"status": "ok", "schedule_id": schedule_id, "description":"Removed Process "})
            return Response(resp,status=200,  mimetype='application/json')
        abort(404, description={"status": "ERROR", "schedule_id": schedule_id, "description":"Error removing process"})
    
    @validate_edit_process
    def patch(self, schedule_id):
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

class ScheduleListFilterResource(Resource):
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
        
class ScheduleListResource(Resource):
    def get(self):
        resp = orch.get_all_schedules()
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

class ScheduleLogResource(Resource):
    def get(self,schedule_id):
        resp = orch.get_all_logs_by_idschedule(schedule_id)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

class ScheduleRobotResource(Resource):
    def delete(self,robot_id, schedule_id):
        resp = orch.remove_process_robot(robot_id, schedule_id)
        if resp:
            resp = json.dumps({"status": "ok", "schedule_id": schedule_id, "description":"Process remove from robot", "robot": robot_id})
            return Response(resp, status=201, mimetype='application/json')
        abort(400, description={"status": "error", "schedule_id": schedule_id, "description":"Error removing process from robot ", "robot": robot_id})


api.add_resource(ProcessListResource,'/api/orchestrator/process/', endpoint='process_resource_list')
api.add_resource(ProcessResource,'/api/orchestrator/process/<int:process_id>',endpoint='process_resource')
api.add_resource(ProcessResourceForm,'/api/orchestrator/process/<int:process_id>/form',endpoint='process_resource_form')
api.add_resource(ScheduleResource,'/api/orchestrator/schedules/<int:schedule_id>',endpoint='schedule_resource')
api.add_resource(ScheduleResource, '/api/orchestrator/schedules/<int:schedule_id>',endpoint='process_edit_resource') #nueva typo patch
api.add_resource(ScheduleResource, '/api/orchestrator/schedules/<int:schedule_id>',endpoint='process_remove_resource') #'/api/orchestrator/canceljob/<string:schedule_id>' -> '/api/orchestrator/schedules/<int:schedule_id>'
api.add_resource(ScheduleResource, '/api/orchestrator/schedules/execute',endpoint='process_run_resource') #'/api/orchestrator/robots/<string:robot_id>/execute' ->  /api/orchestrator/schedules/
api.add_resource(ScheduleListFilterResource,'/api/orchestrator/schedules',endpoint='schedule_list_resource_filter')
api.add_resource(ScheduleListResource,'/api/orchestrator/schedules/',endpoint='schedule_list_resource')
api.add_resource(ScheduleLogResource,'/api/orchestrator/schedules/<int:schedule_id>/logs',endpoint='schedule_logs_resource')
api.add_resource(ScheduleRobotResource, '/api/orchestrator/robots/<string:robot_id>/schedules/<int:schedule_id>', endpoint='robot_remove_process_resource') #cambio /api/orchestrator/robots/removeprocess -> /api/orchestrator/robots/<string:robot_id>/schedules/<int:schedule_id> 
