from flask                              import Blueprint, abort, request
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator    import Orchestrator
import json

orch = Orchestrator()



stat_v1_0_bp = Blueprint('stat_v1_0_bp', __name__)
api = Api(stat_v1_0_bp)

def getBlueprint():
    return stat_v1_0_bp

class MainStatisticsResource(Resource):
    def get(self):
        return Response(orch.get_main_stats(), status=201, mimetype='application/json')

api.add_resource(MainStatisticsResource,'/api/orchestrator/statistics/maindashboard',endpoint='stats_maindashboard_resource' )
