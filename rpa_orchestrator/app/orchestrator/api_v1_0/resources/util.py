from flask                              import Blueprint, abort, request
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator    import Orchestrator
import json

orch = Orchestrator()



util_v1_0_bp = Blueprint('util_v1_0_bp', __name__)
api = Api(util_v1_0_bp)

def getBlueprint():
    return util_v1_0_bp

class IPAddressResource(Resource):
    def get(self):
        id_robot = request.args.get('id_robot')
        resp = json.dumps({"ip": request.remote_addr, "id_robot": id_robot})
        return Response(resp, status=200, mimetype='application/json')


api.add_resource(IPAddressResource, '/api/orchestrator/getip',endpoint='robot_get_ip_address')
