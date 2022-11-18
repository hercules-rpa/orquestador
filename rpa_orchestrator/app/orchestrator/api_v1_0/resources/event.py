from flask                              import Blueprint, abort, request
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from model.DocInfo import DocInfo
from rpa_orchestrator.orchestrator    import Orchestrator
import json
from marshmallow import Schema, fields
from flask_apispec import marshal_with,doc, use_kwargs
from flask_apispec.views import MethodResource
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import token_required

orch = Orchestrator()

class EventSchema(Schema):
    """
    Clase esquema que define un evento.
    """
    id = fields.Int()
    body = fields.Str()
    msgtype = fields.Str()
    time = fields.Float()
    sender = fields.Str()
    read = fields.Boolean()

class EventListResponseSchema(Schema):
    """
    Clase esquema que define una lista de eventos.
    """
    log = fields.List(fields.Nested(EventSchema))

class EventRequestSchema(Schema):
    """
    Clase esquema que define una petición de un evento.
    """
    api_type = fields.String(required=True, description="API type of awesome API")

event_v1_0_bp = Blueprint('event_v1_0_bp', __name__)
api = Api(event_v1_0_bp)

def getBlueprint():
    return event_v1_0_bp

class EventResource(MethodResource,Resource):
    @token_required
    @doc(description='Get Eventos no leídos', tags=['Events'])
    @marshal_with(EventSchema(many=True))  # marshalling with marshmallow library
    def get(self):
        '''
        Método get para el listado de eventos
        '''
        resp = orch.get_events(request.args)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')


class EventSetReadResource(MethodResource,Resource):    
    @token_required
    @doc(description='Método para leer un evento', tags=['Events'])
    @marshal_with(EventSchema)  # marshalling with marshmallow library
    def post(self, event_id):
        '''
        Método para leer un evento
        '''
        resp = orch.set_event_read(event_id)
        if not resp:
            abort(404, description="Resource not found")
        resp = json.dumps({"status": "ok", "description":"Event Edited. Read "})
        return Response(resp, mimetype='application/json')

def getDocInfo():
    """
    Método abstracto para crear las entradas en Swagger.
    """    
    doc_info_list = []
    ep1 = DocInfo(doc_class = EventResource,doc_blueprint='event_v1_0_bp', doc_endpoint='get_events')
    ep2 = DocInfo(doc_class = EventSetReadResource,doc_blueprint='event_v1_0_bp', doc_endpoint='set_events_read')
    doc_info_list.append(ep1)
    doc_info_list.append(ep2)
    return doc_info_list


api.add_resource(EventResource, '/api/orchestrator/events',endpoint='get_events')
api.add_resource(EventSetReadResource, '/api/orchestrator/events/<int:event_id>/read',endpoint='set_events_read')