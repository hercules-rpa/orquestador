from werkzeug.wrappers import Request, Response, ResponseStream
from functools import wraps
from flask import request, abort
from flask_jwt_extended import get_jwt, verify_jwt_in_request
#https://www.youtube.com/watch?v=qAqxSTG2870
#https://www.youtube.com/watch?v=kJSl7pWeOfU

def token_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'Authorization' in request.headers:
            try:
                verify_jwt_in_request()
                return func(*args, **kwargs)
            except Exception as e:
                print(str(e))
                abort(403, description="Token no valido")
        else:
            abort(403, description="Token no presente") 
    return decorated_function

def validate_create_process(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        time_schedules_verify = ['every','at','forever','tag','category']
        process_verify = ['id_robot','priority','parameters','id_process','exclude_robots']

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

    
