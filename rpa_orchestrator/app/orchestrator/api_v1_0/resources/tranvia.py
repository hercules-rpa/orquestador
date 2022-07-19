import json
import os
import uuid
import werkzeug
from flask                              import request, Blueprint, abort, send_from_directory
from flask.wrappers                     import Response
from flask_restful                      import Api, Resource, reqparse
from rpa_orchestrator.lib.TranviaController     import TranviaController
from werkzeug.utils                     import secure_filename
from model.File                         import File
from datetime                           import datetime



controller = TranviaController()



tranvia_v1_0_bp = Blueprint('tranvia_v1_0_bp', __name__)
api = Api(tranvia_v1_0_bp)

def getBlueprint():
    return tranvia_v1_0_bp


class TranviaResource(Resource):
    def get(self):
        date = request.args.get("date")
        resp = controller.get_data_date(date)
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')
        
    def post(self):
        data = request.get_json(force=True)
        date = data['date']
        if data['billetes'] == 0:
            resp = json.dumps({"status": "Fail", "description":" fichero no contiene datos"})
            return Response(resp, status=400, mimetype='application/json')

        del data['date']
        controller.write_data(date, data)
        controller.write_date(date)
        resp = json.dumps({"status": "ok", "description":" fichero creado"})
        return Response(resp, status=201, mimetype='application/json')
        
class TranviaDatesResource(Resource):
    def get(self):
        resp = controller.get_dates_extract()
        if not resp:
            abort(404, description="Resource not found")
        return Response(resp,mimetype='application/json')
        


api.add_resource(TranviaResource, '/api/orchestrator/tranvia/data',endpoint='data_post_resource')
api.add_resource(TranviaResource, '/api/orchestrator/tranvia/data',endpoint='data_get_resource')
api.add_resource(TranviaDatesResource, '/api/orchestrator/tranvia/data/date',endpoint='data_get_all_resource')