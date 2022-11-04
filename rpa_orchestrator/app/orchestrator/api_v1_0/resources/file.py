import json
from model.DocInfo import DocInfo
from flask                              import request, Blueprint, abort
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource
from rpa_orchestrator.orchestrator      import Orchestrator
from model.File                         import File
from flask import redirect
from urllib.parse import urljoin
from marshmallow import Schema, fields
from flask_apispec import marshal_with,doc, use_kwargs
from flask_apispec.views import MethodResource


UPLOAD_FOLDER = 'epic_orchestrator/files/'
orch = Orchestrator()
CDN_URL = 'http://'+orch.cdn_url

file_v1_0_bp = Blueprint('file_v1_0_bp', __name__)
api = Api(file_v1_0_bp)

def getBlueprint():
    return file_v1_0_bp

class FileSchema(Schema):
    """
    Clase esquema que representa un File.
    """
    id = fields.Int()
    name = fields.Str()
    url_cdn = fields.Str()
    format = fields.Str()
    filename = fields.Str()

class URLCDNSchema(Schema):
    """
    Clase esquema que representa la URL del CDN.
    """
    url_cdn = fields.Str()

class FileListResponseSchema(Schema):
    """
    Clase esquema que representa la lista de ficheros.
    """
    log = fields.List(fields.Nested(FileSchema))

class FileRequestSchema(Schema):
    """
    Clase esquema que representa la forma de pedir un fichero
    """
    url_cdn = fields.String(required=True, description="URL del cdn del fichero")
    name = fields.String(required=True, description="Nombre del fichero")


class FilesResource(MethodResource,Resource):
    @doc(description='Obtiene el listado de los ficheros del sistema', tags=['Files'])
    @marshal_with(FileSchema(many=True))  # marshalling with marshmallow library
    def get(self):
        '''
        Método get para el listado de ficheros
        '''
        files = orch.get_file()
        resp = {}
        result = []
        for file in files:
            resp = file.__dict__.copy()
            resp['id'] = file.id
            resp['filename'] = file.name
            resp['name'] = file.get_name()
            resp['format'] = file.get_format()
            result.append(resp)
        return Response(json.dumps(result), status=200, mimetype='application/json')


    @doc(description='Notificación de fichero nuevo desde el CDN', tags=['Files'])
    @use_kwargs(FileRequestSchema, location=('json'))
    @marshal_with(FileSchema)
    def post(self,**kwargs):
        '''
        Método para la subida de ficheros al servidor
        '''
        data = request.get_json(force=True)

        f_name = data['name']
        f_url_cdn = data['url_cdn']
        file = File(id = None, name = f_name, url_cdn = f_url_cdn)
        #creamos file pero sin archivo
        orch.add_file(file)
        data['id'] = file.id
        
        if data:
            resp = json.dumps(data)
            return Response(resp, status=201, mimetype='application/json')
        else:
            abort(404, description="Error no information file was found")

class FileResource(MethodResource,Resource):
    @doc(description='Información de fichero', tags=['Files'],params={'file_id': 
            {
                'description': 'id del fichero',
                'example': '5'
            }
        })
    @marshal_with(FileSchema)  # marshalling with marshmallow library
    def get(self,file_id):
        '''
        Método para obtener la información de un fichero y su url para descargarlo
        '''
        file = orch.get_file(file_id)
        download = request.args.get("download") in ['True', 'true']
        
        if download:
            return redirect(urljoin(file.get_url_cdn))
        if not file:
            abort(404, description="Resource not found")
        resp = file.__dict__.copy()
        resp['id'] = file.id
        resp['filename'] = file.name
        resp['name'] = file.get_name()
        resp['format'] = file.get_format()
        resp['url_cdn'] = file.get_url_cdn()
        return Response(json.dumps(resp), status=200, mimetype='application/json')
        
class CDNURLResource(MethodResource,Resource):
    #HACER EL DELETE
    @doc(description='Obtención de la URL del CDN', tags=['Files'])
    @marshal_with(URLCDNSchema)  # marshalling with marshmallow library 
    def get(self):
        '''
        Método para obtener la URL del CDN actual del sistema
        '''
        resp = {}
        resp['cdn_url'] = CDN_URL
        return Response(json.dumps(resp), status=200, mimetype='application/json')

def getDocInfo():
    """
    Método abstracto para crear las entradas en Swagger.
    """
    doc_info_list = []
    ep1 = DocInfo(doc_class = FilesResource,doc_blueprint='file_v1_0_bp', doc_endpoint='files_get_all_resource')
    ep2 = DocInfo(doc_class = FileResource,doc_blueprint='file_v1_0_bp', doc_endpoint='files_get_resource')
    ep4 = DocInfo(doc_class = CDNURLResource,doc_blueprint='file_v1_0_bp', doc_endpoint='files_url_resource')

    doc_info_list.append(ep1)
    doc_info_list.append(ep2)
    doc_info_list.append(ep4)
    return doc_info_list

api.add_resource(FilesResource, '/api/orchestrator/cdn/files/',endpoint='files_get_all_resource')
api.add_resource(FileResource, '/api/orchestrator/cdn/files/<int:file_id>',endpoint='files_get_resource')
api.add_resource(CDNURLResource, '/api/orchestrator/cdn/url',endpoint='files_url_resource')