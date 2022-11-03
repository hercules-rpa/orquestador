from flask                              import Blueprint, abort, request
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator      import Orchestrator
from marshmallow                        import Schema, fields
from flask_apispec                      import marshal_with,doc
from flask_apispec.views                import MethodResource
from model.DocInfo                      import DocInfo
import json
from model.process.ValidEvaluators import ValidEvaluators

orch = Orchestrator()

util_v1_0_bp = Blueprint('util_v1_0_bp', __name__)
api = Api(util_v1_0_bp)

ve = ValidEvaluators()

def getBlueprint():
    return util_v1_0_bp

class UtilIPSchema(Schema):
    """
    Clase esquema para representar la ip del robot
    """
    ip = fields.Str()
    id_robot = fields.Str(allow_none=True,missing=True)

class NameComissionComitteeSchema(Schema):
    """
    Clase esquema nombre de los comites y comisiones.
    """
    name = fields.Str()

class ComiSchema(Schema):
    """
    Clase esquema para representar una comisión.
    """
    fields.Dict(keys=fields.Int(), values=fields.Nested(NameComissionComitteeSchema))

class IPAddressResource(MethodResource, Resource):
    @doc(description='Obtener IPs para la página dashboard', tags=['Utils'])
    @marshal_with(UtilIPSchema)    
    def get(self):
        id_robot = request.args.get('id_robot')
        resp = json.dumps({"ip": request.remote_addr, "id_robot": id_robot})
        return Response(resp, status=200, mimetype='application/json')

class CommitteesUtilsResource(MethodResource, Resource):
    @doc(description='Obtener todos los comités', tags=['Sexenios'])
    @marshal_with(ComiSchema)  
    def get(self):
        committees = ve.get_valid_committee()
        resp = json.dumps(committees)
        return Response(resp,status=200, mimetype='application/json')
        

class CommissionsUtilsResource(MethodResource, Resource):
    @doc(description='Obtener todas las comisiones', tags=['Acreditaciones'])
    @marshal_with(ComiSchema)  
    def get(self):
        commissions = ve.get_valid_commissions()
        resp = json.dumps(commissions)
        return Response(resp,status=200, mimetype='application/json')

def getDocInfo():
    """
    Método abstracto para crear las entradas en Swagger.
    """
    doc_info_list = []
    ep1 = DocInfo(doc_class = IPAddressResource, doc_blueprint='util_v1_0_bp', doc_endpoint='robot_get_ip_address')
    ep2 = DocInfo(doc_class = CommitteesUtilsResource, doc_blueprint='util_v1_0_bp', doc_endpoint='get_valid_committees')
    ep3 = DocInfo(doc_class = CommissionsUtilsResource, doc_blueprint='util_v1_0_bp', doc_endpoint='get_valid_commissions')
    doc_info_list.append(ep1)
    doc_info_list.append(ep2)
    doc_info_list.append(ep3)
    return doc_info_list

api.add_resource(CommitteesUtilsResource,'/api/orchestrator/sexenios/comites',endpoint='get_valid_committees')
api.add_resource(CommissionsUtilsResource,'/api/orchestrator/acreditaciones/comisiones',endpoint='get_valid_commissions')
api.add_resource(IPAddressResource, '/api/orchestrator/getip',endpoint='robot_get_ip_address')
