from flask                              import Blueprint, abort
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator    import Orchestrator


orch = Orchestrator()



log_v1_0_bp = Blueprint('log_v1_0_bp', __name__)
api = Api(log_v1_0_bp)

def getBlueprint():
    return log_v1_0_bp

class LogListResource(Resource):
    def get(self):
        return Response(orch.get_log(),mimetype='application/json')

class LogResource(Resource):
    def get(self,log_id):
        resp = orch.get_log(log_id)
        if resp is None:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')

api.add_resource(LogListResource,'/api/orchestrator/logs', endpoint='log_list_resource')
api.add_resource(LogResource,'/api/orchestrator/logs/<int:log_id>', endpoint='log_resource')