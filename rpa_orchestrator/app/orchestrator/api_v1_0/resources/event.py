from flask                              import Blueprint, abort, request
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator    import Orchestrator
import json

orch = Orchestrator()



event_v1_0_bp = Blueprint('event_v1_0_bp', __name__)
api = Api(event_v1_0_bp)

def getBlueprint():
    return event_v1_0_bp

class EventResource(Resource):
    def get(self):
        resp = orch.get_events(request.args)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')


class EventSetReadResource(Resource):
    def post(self, event_id):
        resp = orch.set_event_read(event_id)
        if not resp:
            abort(404, description="Resource not found")
        resp = json.dumps({"status": "ok", "description":"Event Edited. Read "})
        return Response(resp, mimetype='application/json')


api.add_resource(EventResource, '/api/orchestrator/events',endpoint='get_events')
api.add_resource(EventSetReadResource, '/api/orchestrator/events/<int:event_id>/read',endpoint='set_events_read')