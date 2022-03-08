import rpa_orchestrator.lib.dbprocess.dbcon as dbprocess
import json
from datetime import datetime
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ControllerProcess(metaclass=Singleton):
    def __init__(self):
        self.dbprocess = dbprocess.ControllerDBProcess()
    
    def get_sgi(self, filters=None):
        models_sgi = self.dbprocess.read_sgi(filters)
        sgi_dict = [x.__dict__ for x in models_sgi]
        if len(sgi_dict) == 0:
            return None
        for x in sgi_dict: 
            del x['_sa_instance_state']
            x['fecha_creacion'] = datetime.timestamp(x['fecha_creacion'])
        return json.dumps(sgi_dict)

    def get_convocatoria(self, filters=None):
        models_convocatoria = self.dbprocess.read_convocatoria(filters)
        convocatoria_dict = [x.__dict__ for x in models_convocatoria]
        if len(convocatoria_dict) == 0:
            return None
        for x in convocatoria_dict: 
            del x['_sa_instance_state']
            x['fecha_creacion'] = datetime.timestamp(x['fecha_creacion'])
            if x['fecha_publicacion']:
                x['fecha_publicacion'] = datetime.timestamp(x['fecha_publicacion'])
        return json.dumps(convocatoria_dict)

    def get_solicitud(self, filters=None):
        models_solicitud = self.dbprocess.read_solicitud(filters)
        solicitud_dict = [x.__dict__ for x in models_solicitud]
        if len(solicitud_dict) == 0:
            return None
        for x in solicitud_dict: 
            del x['_sa_instance_state']
            x['fecha_creacion'] = datetime.timestamp(x['fecha_creacion'])
        return json.dumps(solicitud_dict)

    def get_basereguladora(self, filters=None):
        models_basereguladora = self.dbprocess.read_basereguladora(filters)
        basereguladora_dict = [x.__dict__ for x in models_basereguladora]
        if len(basereguladora_dict) == 0:
            return None
        for x in basereguladora_dict: 
            del x['_sa_instance_state']
            x['fecha_creacion'] = datetime.timestamp(x['fecha_creacion'])
        return json.dumps(basereguladora_dict)

    def get_noticia(self, filters=None):
        models_noticia = self.dbprocess.read_noticia(filters)
        noticia_dict = [x.__dict__ for x in models_noticia]
        if len(noticia_dict) == 0:
            return None
        for x in noticia_dict: 
            del x['_sa_instance_state']
            x['fecha'] = datetime.timestamp(x['fecha'])
        return json.dumps(noticia_dict)
    
    def dump(self, object):
        self.dbprocess.dump(object)

    def update_convocatoria(self, id, new_parameters):
        return self.dbprocess.update_convocatoria(id, new_parameters)

    def update_basereguladora(self, id, new_parameters):
        return self.dbprocess.update_basereguladora(id, new_parameters)

    def update_noticia(self, id, new_parameters):
        return self.dbprocess.update_noticia(id, new_parameters)

    def update_solicitud(self, id, new_parameters):
        return self.dbprocess.update_solicitud(id, new_parameters)    

    def update_sgi(self, id, new_parameters):
        return self.dbprocess.update_sgi(id, new_parameters)