from werkzeug.wrappers                  import Request, Response, ResponseStream
from functools                          import wraps
from flask                              import request, abort, current_app
from flask_jwt_extended                 import get_jwt, verify_jwt_in_request, get_jwt_identity
from rpa_orchestrator.orchestrator      import Orchestrator

import datetime
import json
import jwt

def token_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token = None
        orch = Orchestrator()
        if 'Token_Robot' in request.headers:
            try:
                token = request.headers['Token_Robot']
                if token == "":
                    return Response(json.dumps({"msg": "Token_Robot no presente"}), status=401, mimetype='application/json')
            except Exception as e:
                print(str(e))
                return Response(json.dumps({"msg": "Token_Robot no válido"}), status=403, mimetype='application/json')       
            for robot in orch.robot_list.values():
                if robot[0].token == token:
                    return func(*args, **kwargs)
        elif 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
                if token == "":
                    return Response(json.dumps({"msg": "Authorization token no presente"}), status=401, mimetype='application/json')

                for jwt_token in orch.token_revoke:
                    try:
                        jwt.decode(jwt_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
                    except Exception as e:
                        if type(e) == jwt.exceptions.ExpiredSignatureError:
                            orch.token_revoke.remove(jwt_token)
                    if jwt_token == token:
                        resp = json.dumps({"status": "Token ya revocado."})
                        return Response(resp, status=401, mimetype='application/json') 
                
                data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
                current_user = orch.get_username(data['sub'])
                if not current_user:
                    return Response(json.dumps({"msg": "Authorization token no válido. El usuario no existe"}), status=403, mimetype='application/json')
            
            except Exception as e:
                if type(e) == jwt.exceptions.ExpiredSignatureError:
                    resp = json.dumps({"msg": "Token expirado."})
                    return Response(resp, status=403, mimetype='application/json')
                if type(e) == jwt.exceptions.DecodeError:
                    resp = json.dumps({"msg": "Token malformado."})
                    return Response(resp, status=403, mimetype='application/json')
                abort(403, description="Token no valido")
            return func(*args, **kwargs)
        else:
            return Response(json.dumps({"msg": "Token no presente"}), status=403, mimetype='application/json') 
    return decorated_function

def token_required_investigador(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            if 'Authorization' in request.headers:
                verify_jwt_in_request()
                return func(*args, **kwargs)
        except Exception as e:
            print(str(e))
            abort(403, description="Token no valido")
    return decorated_function

def validate_create_process(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        time_schedules_verify = ['every','at','forever','tag','category']
        process_verify = ['id_robot','priority','parameters','id_process','exclude_robots']

        try:
            time_schedule = request.get_json(force=True)['time_schedule']
            print(time_schedule)
            process       = request.get_json(force=True)['process']
        except:
            abort(406, description="Mala sintaxis JSON")

        if process['id_process'] == 98 and not process['id_robot']:
            abort(406, description = "id_robot requerido para este proceso")
            
        for p in process_verify:
            if not p in process:
                if p == 'exclude_robots':
                    print("No se ha detectado el campo exclude_robots. No pasa nada sigo funcionando, pero añadelo tu por mi.")
                    continue
                abort(406, description="Mala sintaxis JSON. Es necesario añadir "+p)
        if time_schedule:
            for t in time_schedules_verify:
                if not t in time_schedule:
                    abort(406, description="Mala sintaxis JSON. Es necesario añadir "+t)
        return func(*args, **kwargs)
    return decorated_function

def validate_edit_process(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        time_schedules_verify = ['every','at','forever','tag','category']
        process_verify = ['id_robot','priority','exclude_robots']

        try:
            time_schedule = request.get_json(force=True)['time_schedule']
            process       = request.get_json(force=True)['process']
        except:
            abort(406, description="Mala sintaxis JSON")
        for p in process_verify:
            if not p in process:
                if p == 'exclude_robots':
                    print("No se ha detectado el campo exclude_robots. No pasa nada sigo funcionando, pero añadelo tu por mi.")
                    continue
                abort(406, description="Mala sintaxis JSON. Es necesario añadir "+p)
        if time_schedule:
            for t in time_schedules_verify:
                if not t in time_schedule:
                    abort(406, description="Mala sintaxis JSON. Es necesario añadir "+t)
        return func(*args, **kwargs)
    return decorated_function


class Middleware():
    '''
    Simple WSGI middleware
    '''

    def __init__(self, app):
        self.app = app


    def __call__(self, environ, start_response):
        '''request = Request(environ)
        userName = request.authorization['username']
        password = request.authorization['password']
        
        # these are hardcoded for demonstration
        # verify the username and password from some database or env config variable
        if userName == self.userName and password == self.password:
            environ['user'] = { 'name': 'Tony' }
            return self.app(environ, start_response)

        res = Response(u'Authorization failed', mimetype= 'text/plain', status=401)
        return res(environ, start_response)
        '''
        pass

    
