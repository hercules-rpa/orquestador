from flask                              import Blueprint, abort, request
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator      import Orchestrator
import json
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import token_required

orch = Orchestrator()

orch_v1_0_bp = Blueprint('orch_v1_0_bp', __name__)
api = Api(orch_v1_0_bp)

def getBlueprint():
    return orch_v1_0_bp

class OrchestratorReload(Resource):
    @token_required
    def get(self):
        orch.reload_process()
        orch.reload_robot()
        orch.reload_schedule()
        return Response({"Orchestrator reloaded"}, status=201, mimetype='application/json')

api.add_resource(OrchestratorReload,'/api/orchestrator/reload/',endpoint='orchestrator_reload' )
