from dataclasses import fields
import json
import os
import uuid

from flask_apispec import MethodResource, doc, marshal_with, use_kwargs
from marshmallow import Schema
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import token_required
import werkzeug
from flask                              import request, Blueprint, abort, send_from_directory
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource, reqparse
from rpa_orchestrator.orchestrator     import Orchestrator
from model.GlobalSettings              import GlobalSettings
from datetime                           import datetime
from rpa_orchestrator.ControllerProcess    import ControllerProcess
from flask import redirect
from urllib.parse import urljoin
from marshmallow                        import Schema, fields
from flask_apispec                      import marshal_with,doc
from flask_apispec.views                import MethodResource
from model.DocInfo                      import DocInfo

orch = Orchestrator()


global_settings_v1_0_bp = Blueprint('global_settings_v1_0_bp', __name__)
api = Api(global_settings_v1_0_bp)

def getBlueprint():
    return global_settings_v1_0_bp


class GlobalSettingsResourceSchema(Schema):
    """
    Clase esquema para representar settings de sparql
    """
    edma_host_sparql = fields.Str()
    edma_host_servicios = fields.Str()
    edma_port_sparql = fields.Int()
    sgi_user = fields.Str()
    sgi_password = fields.Str()
    sgi_ip = fields.Str()
    sgi_port = fields.Int()
    database_ip = fields.Str()
    database_port = fields.Int()
    url_upload_cdn = fields.Str()
    url_release = fields.Str()

class GlobalSettingsResource(MethodResource,Resource):
    @token_required
    @doc(description='Obtener ajustes globales', tags=['Settings'])
    @marshal_with(GlobalSettingsResourceSchema)
    def get(self,id = 1):
        global_settings = orch.get_global_settings_by_id(id)
        if global_settings:
            resp = {}
            resp = global_settings.__dict__.copy()
            return Response(json.dumps(resp), status=200, mimetype='application/json')
        else:
            return Response(json.dumps({"msg":"No se ha podido recuperar los parámetros globales"}), status=404, mimetype='application/json') 

    @token_required
    @doc(description='Modificar ajustes globales', tags=['Settings'])
    @use_kwargs(GlobalSettingsResourceSchema,
    location=('json'))
    def patch(self, id_settings = 1,**kwargs):
        new_parameters = request.get_json()
        black_list = ['id']
        for key in black_list:
            if key in new_parameters:
                del new_parameters[key]
        resp = orch.update_global_settings(id_settings, new_parameters)
        if not resp:
            return Response(json.dumps({"msg":"Error intentado actualizar los ajustes globales con id "+str(id_settings)}), status=404, mimetype='application/json')
        resp = json.dumps({"status": "ok", "global_settings": id_settings, "descripcion":"Ajustes actualizados"})
        return Response(resp,mimetype='application/json')


def getDocInfo():
    doc_info_list = []
    ep1 = DocInfo(doc_class = GlobalSettingsResource, doc_blueprint='global_settings_v1_0_bp', doc_endpoint = 'global_settings_resource')

    doc_info_list.append(ep1)
    return doc_info_list



api.add_resource(GlobalSettingsResource, '/api/orchestrator/global_settings/',endpoint='global_settings_resource')