from flask                              import Blueprint, abort, request, current_app
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator      import Orchestrator
from marshmallow                        import Schema, fields
from flask_apispec                      import marshal_with,doc, use_kwargs
from flask_apispec.views                import MethodResource
from model.DocInfo                      import DocInfo
from model.process.ValidEvaluators      import ValidEvaluators
from flask_jwt_extended                 import create_access_token
from flask_jwt_extended                 import get_jwt_identity
from flask_jwt_extended                 import jwt_required
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import token_required
import rpa_orchestrator.lib.persistence.models as model
import json, jwt, datetime

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

class AuthSchema(Schema):
    """
    Clase esquema para representar qué se necesita para la autenticación de usuarios.
    """
    username = fields.Str()
    password = fields.Str()

class TokenSchema(Schema):
    """
    Clase esquema para representar la respuesta para la autenticación de usuarios.
    """
    Auth = fields.Str()

class RefreshSchema(Schema):
    """
    Clase esquema para representar el refresco para la autenticación de usuarios.
    """
    status = fields.Str()

class IdentitySchema(Schema):
    """
    Clase esquema para representar la identidad de un token.
    """
    username = fields.Str()

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

class AuthToken(MethodResource, Resource):
    @doc(description='Obtener token para el login', tags=['Utils'])
    @use_kwargs(AuthSchema, location=('json'))
    @marshal_with(TokenSchema)
    def post(self, **kwargs):
        solicitud = json.dumps(request.get_json(force=True))
        try:
            user = json.loads(solicitud, object_hook=lambda d: model.Username(**d))
            access_user = orch.user_login(user.username, user.password)
            if access_user:
                    if access_user.token != "":
                        try:
                            data = jwt.decode(access_user.token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
                            access_token = access_user.token
                            resp = json.dumps({"status": "ok", "Auth": access_token, "description":"Username Authentication"})
                            return Response(resp, status=200, mimetype='application/json')
                        except Exception as e:
                            if type(e) == jwt.exceptions.ExpiredSignatureError:
                                resp = json.dumps({"msg": "Token expirado."})
                                orch.update_username_token(user.username, "")
                                return Response(resp, status=403, mimetype='application/json')
                            if type(e) == jwt.exceptions.DecodeError:
                                resp = json.dumps({"msg": "Token malformado."})
                                orch.update_username_token(user.username, "")
                                return Response(resp, status=403, mimetype='application/json')
                            access_token = create_access_token(identity=user.username,expires_delta=datetime.timedelta(minutes=30))
                            orch.update_username_token(user.username, access_token)
                            resp = json.dumps({"status": "ok", "Auth": access_token, "description":"Username Authentication"})
                            return Response(resp, status=200, mimetype='application/json')                  
                    else:
                        access_token = create_access_token(identity=user.username,expires_delta=datetime.timedelta(minutes=30))
                        orch.update_username_token(user.username, access_token)
                        resp = json.dumps({"status": "ok", "Auth": access_token, "description":"Username Authentication"})
                        return Response(resp, status=200, mimetype='application/json')
            else:
                return Response(json.dumps({"msg": "Bad username or password"}), status=401, mimetype='application/json')
        except Exception as e:
            abort(400, description=""+str(e))

class AuthRefreshToken(MethodResource, Resource):
    @token_required
    @doc(description='Comprobar si el token es válido', tags=['Utils'])
    @marshal_with(TokenSchema)
    def get(self):
        token = request.headers['Authorization'].split(" ")[1]
        data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        orch.token_revoke.append(token)
        access_token = create_access_token(identity=data["sub"],expires_delta=datetime.timedelta(minutes=30))
        orch.update_username_token(data["sub"], access_token)
        resp = json.dumps({"status": "ok", "Auth": access_token, "description":"Username Authentication"})
        return Response(resp, status=200, mimetype='application/json')

class AuthLogoutToken(MethodResource, Resource):
    @token_required
    @doc(description='Revocamos token en el logout', tags=['Utils'])
    @marshal_with(RefreshSchema)
    def get(self):                 
        token = request.headers['Authorization'].split(" ")[1]
        data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        orch.token_revoke.append(token)
        orch.update_username_token(data["sub"], "")
        resp = json.dumps({"status": "ok."})
        return Response(resp, status=200, mimetype='application/json')        

class CommitteesUtilsResource(MethodResource, Resource):
    @token_required
    @doc(description='Obtener todos los comités', tags=['Sexenios'])
    @token_required
    @marshal_with(ComiSchema)  
    def get(self):
        committees = ve.get_valid_committee()
        resp = json.dumps(committees)
        return Response(resp,status=200, mimetype='application/json')
        

class CommissionsUtilsResource(MethodResource, Resource):
    @token_required
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
    ep4 = DocInfo(doc_class = AuthToken, doc_blueprint='util_v1_0_bp', doc_endpoint='get_login')
    ep5 = DocInfo(doc_class = AuthRefreshToken, doc_blueprint='util_v1_0_bp', doc_endpoint='get_refresh')
    ep6 = DocInfo(doc_class = AuthLogoutToken, doc_blueprint='util_v1_0_bp', doc_endpoint='get_logout')
    doc_info_list.append(ep1)
    doc_info_list.append(ep2)
    doc_info_list.append(ep3)
    doc_info_list.append(ep4)
    doc_info_list.append(ep5)
    doc_info_list.append(ep6)
    return doc_info_list

api.add_resource(CommitteesUtilsResource,'/api/orchestrator/sexenios/comites',endpoint='get_valid_committees')
api.add_resource(CommissionsUtilsResource,'/api/orchestrator/acreditaciones/comisiones',endpoint='get_valid_commissions')
api.add_resource(IPAddressResource, '/api/orchestrator/getip',endpoint='robot_get_ip_address')
api.add_resource(AuthToken, '/api/orchestrator/auth/login', endpoint='get_login')
api.add_resource(AuthRefreshToken, '/api/orchestrator/auth/refresh_session', endpoint='get_refresh')
api.add_resource(AuthLogoutToken, '/api/orchestrator/auth/logout', endpoint='get_logout')
