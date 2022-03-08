import json
import os
import uuid
import werkzeug
from flask                              import request, Blueprint, abort, send_from_directory
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource, reqparse
from rpa_orchestrator.orchestrator     import Orchestrator
from werkzeug.utils                     import secure_filename
from model.File                         import File
from datetime                           import datetime


UPLOAD_FOLDER = 'rpa_orchestrator/files/'
orch = Orchestrator()



file_v1_0_bp = Blueprint('file_v1_0_bp', __name__)
api = Api(file_v1_0_bp)

def getBlueprint():
    return file_v1_0_bp

class FilesResource(Resource):
    def get(self):
        files = orch.get_file()
        resp = {}
        result = []
        for file in files:
            resp = file.__dict__.copy()
            resp['id'] = file.id
            resp['filename'] = file.name
            resp['name'] = file.get_name()
            resp['format'] = file.get_format()
            resp['directory'] = file.directory
            resp['absolute_path'] = file.absolute_path
            resp['URL']  = "http://"+orch.get_host()+":5000/api/orchestrator/files/"+str(file.id)+"?download=True"
            resp['time'] = file.time.timestamp()
            result.append(resp)
        return Response(json.dumps(result), status=200, mimetype='application/json')

class FileResource(Resource):
    #HACER EL DELETE 
    def get(self,file_id):
        download = request.args.get("download") in ['True', 'true']
        file = orch.get_file(file_id)
        if not file:
            abort(404, description="Resource not found")
        filename = file.name
        directory = file.directory
        if download:
            try:
                return send_from_directory(directory, filename, as_attachment=True)
            except FileNotFoundError:
                abort(404, description="Resource not found")
        else:
            resp = file.__dict__.copy()
            resp['id'] = file.id
            resp['filename'] = file.name
            resp['name'] = file.get_name()
            resp['format'] = file.get_format()
            resp['directory'] = file.directory
            resp['absolute_path'] = file.absolute_path
            resp['URL']  = "http://"+orch.get_host()+":5000/api/orchestrator/files/"+str(file_id)+"?download=True"
            resp['time'] = file.time.timestamp()
            return Response(json.dumps(resp), status=200, mimetype='application/json')

    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parse.parse_args()
        file = args['file']
        if file:
            # cogemos el fichero le asignamos un uuid y una ruta
            filename = secure_filename(file.filename)
            extension = os.path.splitext(filename)[1]
            f_name = str(uuid.uuid4().hex) + extension
            f_path = os.path.join(UPLOAD_FOLDER, f_name)
            f_directory = os.path.abspath(os.path.join(UPLOAD_FOLDER))
            file.save(f_path)
            absolute_path = os.path.abspath(f_path)
            file = File(id = None, name = f_name, absolute_path = absolute_path, directory=f_directory, time=datetime.now())
            orch.add_file(file)
            f_object = {}
            f_object['absolute_path'] = absolute_path
            f_object['filename'] = f_name
            f_object['id'] = file.id
            f_object['directory'] = f_directory
            f_object['name'] = file.get_name()
            f_object['format'] = file.get_format()
            f_object['URL']  = "http://"+orch.get_host()+":5000/api/orchestrator/files/"+str(file.id)+"?download=True"
            resp = json.dumps(f_object)
            return Response(resp, status=201, mimetype='application/json')
            #relacionamos la ruta con un id en la base de datos y guardamos
            #devolvemos el id asociado al fichero para guardar la referencia
        else:
            abort(404, description="Error File not found")

api.add_resource(FilesResource, '/api/orchestrator/files/',endpoint='files_get_all_resource')
api.add_resource(FileResource, '/api/orchestrator/files/<int:file_id>',endpoint='files_get_resource')
api.add_resource(FileResource, '/api/orchestrator/files',endpoint='files_upload_resource')