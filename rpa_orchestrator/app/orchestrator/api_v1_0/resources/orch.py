from flask                              import Blueprint, abort, request
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator      import Orchestrator
import json

orch = Orchestrator()

orch_v1_0_bp = Blueprint('orch_v1_0_bp', __name__)
api = Api(orch_v1_0_bp)

def getBlueprint():
    return orch_v1_0_bp

class OrchestratorReload(Resource):
    def get(self):
        orch.reload_process()
        orch.reload_robot()
        orch.reload_schedule()
        return Response({"Orchestrator reloaded"}, status=201, mimetype='application/json')

class OrchestratorRestart(Resource):
    def get(self):
        orch.restart()
        return Response({"TODO. Under construction"}, status=201, mimetype='application/json')

api.add_resource(OrchestratorReload,'/api/orchestrator/reload/',endpoint='orchestrator_reload' )
api.add_resource(OrchestratorRestart,'/api/orchestrator/restart/',endpoint='orchestrator_update' )
