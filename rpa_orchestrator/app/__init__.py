from flask import Flask, jsonify
from flask_restful import Api
from rpa_orchestrator.app.common.error_handling import ObjectNotFound, AppErrorBaseClass
#from app.db import db
#from .ext import ma, migrate
from flask_cors import CORS
from rpa_orchestrator.app.orchestrator.api_v1_0.middleware import Middleware

DIRECTORY_RESOURCES = 'rpa_orchestrator/app/orchestrator/api_v1_0/resources/*.py'


def create_app(settings_module):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(settings_module)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    # Inicializa las extensiones
    #db.init_app(app)
    #ma.init_app(app)
    #migrate.init_app(app, db)
    # Captura todos los errores 404
    Api(app, catch_all_404s=True)
    # Deshabilita el modo estricto de acabado de una URL con /
    app.url_map.strict_slashes = False
    
    # Registra los blueprints
    import glob 
    import importlib
    modules_name = glob.glob(DIRECTORY_RESOURCES)
    for i in modules_name:
        module = i.split(".")[0]
        module = module.replace("/",".")
        print(module)
        load_module = importlib.import_module(module)
        app.register_blueprint(load_module.getBlueprint())
        
    # Registra manejadores de errores personalizados
    register_error_handlers(app)
    #app.wsgi_app = Middleware(app.wsgi_app)
    return app

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception_error(e):
        return jsonify({'msg': 'Internal server error'}), 500
    @app.errorhandler(405)
    def handle_405_error(e):
        return jsonify({'msg': 'Method not allowed'}), 405
    @app.errorhandler(406)
    def handle_406_error(e):
        return jsonify({'msg': 'Bad syntaxis in JSON'}), 406
    @app.errorhandler(403)
    def handle_403_error(e):
        return jsonify({'msg': 'Forbidden error'}), 403
    @app.errorhandler(404)
    def handle_404_error(e):
        return jsonify({'msg': 'Not Found error'}), 404
    @app.errorhandler(AppErrorBaseClass)
    def handle_app_base_error(e):
        return jsonify({'msg': str(e)}), 500
    @app.errorhandler(ObjectNotFound)
    def handle_object_not_found_error(e):
        return jsonify({'msg': str(e)}), 404