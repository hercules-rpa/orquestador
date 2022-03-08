from flask                              import Blueprint, abort
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator    import Orchestrator


orch = Orchestrator()
robot_v1_0_bp = Blueprint('robot_v1_0_bp', __name__)
api = Api(robot_v1_0_bp)

def getBlueprint():
    return robot_v1_0_bp

class RobotListResource(Resource):
    def get(self):
        result = orch.get_all_robots()
        result = Response(result,mimetype='application/json')
        return result

class RobotListProblemResource(Resource):
    def get(self):
        result = orch.get_robot_problems()
        result = Response(result,mimetype='application/json')
        return result

class RobotResource(Resource):
    def get(self,robot_id):
        resp = orch.get_robot(robot_id)
        if resp is None:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

class RobotProblemResource(Resource):
    def get(self,robot_id):
        resp = orch.get_robot_problems(robot_id)
        if resp is None:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

class RobotLogResource(Resource):
    def get(self,robot_id):
        resp = orch.get_all_logs_by_idrobot(robot_id)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')


api.add_resource(RobotListResource, '/api/orchestrator/robots/', endpoint='robot_list_resource')
api.add_resource(RobotListProblemResource, '/api/orchestrator/robots/problems', endpoint='robot_list_problems_resource')
api.add_resource(RobotResource, '/api/orchestrator/robots/<string:robot_id>', endpoint='robot_resource')
api.add_resource(RobotProblemResource, '/api/orchestrator/robots/<string:robot_id>/problems', endpoint='robot_problems_resource')
api.add_resource(RobotLogResource, '/api/orchestrator/robots/<string:robot_id>/logs', endpoint='robot_log_resource')