from logging import log
from sqlalchemy                 import create_engine  
from sqlalchemy                 import Column, String, desc, asc, and_, or_, func
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm             import sessionmaker
from datetime                   import datetime,timedelta
import rpa_orchestrator.lib.dbprocess.models as model
import json

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ControllerDBProcess(metaclass=Singleton):
    def __init__(self, user, password, host, port, database):
        self.user           = user
        self.password       = password
        self.host           = host
        self.port           = port
        self.database       = database
        self.db = create_engine("postgresql://"+user+":"+password+"@"+host+":"+port+"/"+database)  
        self.base = declarative_base()
        self.Session = sessionmaker(self.db)

    def dump(self,objects):
        session = self.Session()
        session.expire_on_commit = False
        for object in objects:
            if isinstance(object, model.Sgi):
                if not object.id:
                    object.fecha_creacion = datetime.today().isoformat()
                    session.add(object)
                    session.commit()
                    session.refresh(object)
                    
            elif isinstance(object, model.Convocatoria):
                exists = session.query(model.Convocatoria).filter_by(url=object.url).first()
                if not object.id and not exists:
                    object.fecha_creacion = datetime.today().isoformat()
                    if object.fecha_publicacion:
                        object.fecha_publicacion = datetime.fromtimestamp(object.fecha_publicacion).isoformat()
                    session.add(object)
                    session.commit()
                    session.refresh(object)
                else:
                    if not exists:
                        exists = session.query(model.Convocatoria).filter_by(id=object.id).first()
                    if exists:
                        exists.sgiid = object.sgiid
                        exists.basereguladoraid = object.basereguladoraid
                        exists.notificada = object.notificada
                        session.commit()
                        #session.refresh(object)

            elif isinstance(object,model.Solicitud):
                if not object.id:
                    object.fecha_creacion = datetime.today().isoformat()
                    session.add(object)
                    session.commit()
                    session.refresh(object)
                else:
                    exists = session.query(model.Solicitud).filter_by(id=object.id).first()
                    if exists:
                        exists.sgiid = object.sgiid
                        session.commit()
                        #session.refresh(object)

            elif isinstance(object, model.Basereguladora):
                exists = session.query(model.Basereguladora).filter_by(id_base=object.id_base).first()
                if not exists:
                    object.fecha_creacion = datetime.today().isoformat()
                    session.add(object)
                    session.commit()
                    session.refresh(object)
                else:
                    exists.notificada = object.notificada
                    exists.titulo     = object.titulo
                    exists.url        = object.url
                    object.id         = exists.id
                    session.commit()
            
            elif isinstance(object, model.Noticia):
                exists = session.query(model.Noticia).filter_by(id=object.id).first()
                if not exists:
                    object.fecha = datetime.today().isoformat()
                    session.add(object)
                    session.commit()
                    session.refresh(object)
                else:
                    exists.notificada = object.notificada
                    exists.titulo     = object.titulo
                    exists.url        = object.url
                    object.id         = exists.id
                    session.commit()
                    
        session.close()

    def update_convocatoria(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Convocatoria).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (convocatoria)")
                session.close()
                return False
        return False


    def update_basereguladora(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Basereguladora).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (basereguladora)")
                session.close()
                return False
        return False

    def update_noticia(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Noticia).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (noticia)")
                session.close()
                return False
        return False

    def update_solicitud(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Solicitud).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (solicitud)")
                session.close()
                return False
        return False

    def update_sgi(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Sgi).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (sgi)")
                session.close()
                return False
        return False
        

    def read_sgi(self, filters=None):
        session = self.Session()
        sgi_db = session.query(model.Sgi)
        if filters:
            for (key, value) in filters.items():
                try:
                    if isinstance(value, bool) or value is None:
                        sgi_db = sgi_db.filter(getattr(model.Sgi,key).is_(value))
                    else:
                        sgi_db = sgi_db.filter(getattr(model.Sgi,key)==value)
                except:
                    print("No existe la columna "+key)
                    return []
        sgi_db = sgi_db.all()
        session.close()
        return sgi_db

    def read_convocatoria(self, filters=None):
        session = self.Session()
        convocatoria_db = session.query(model.Convocatoria)
        if filters:
            for (key, value) in filters.items():
                try:
                    if isinstance(value, bool) or value is None:
                        convocatoria_db = convocatoria_db.filter(getattr(model.Convocatoria,key).is_(value))
                    else:
                        convocatoria_db = convocatoria_db.filter(getattr(model.Convocatoria,key)==value)
                except:
                    print("No existe la columna "+key)
                    return []
        convocatoria_db = convocatoria_db.all()
        session.close()
        return convocatoria_db

    def read_solicitud(self, filters=None):
        session = self.Session()
        solicitud_db = session.query(model.Solicitud)
        if filters:
            for (key, value) in filters.items():
                try:
                    if isinstance(value, bool) or value is None:
                        solicitud_db = solicitud_db.filter(getattr(model.Solicitud,key).is_(value))
                    else:
                        solicitud_db = solicitud_db.filter(getattr(model.Solicitud,key)==value)
                except:
                    print("No existe la columna "+key)
                    return []
        solicitud_db = solicitud_db.all()
        session.close()
        return solicitud_db

    def read_basereguladora(self, filters=None):
        session = self.Session()
        basereguladora_db = session.query(model.Basereguladora)
        if filters:
            for (key, value) in filters.items():
                try:
                    if isinstance(value, bool) or value is None:
                        basereguladora_db = basereguladora_db.filter(getattr(model.Basereguladora,key).is_(value))
                    else:
                        basereguladora_db = basereguladora_db.filter(getattr(model.Basereguladora,key)==value)
                except:
                    print("No existe la columna "+key)
                    return []
        basereguladora_db = basereguladora_db.all()
        session.close()
        return basereguladora_db

    def read_noticia(self, filters=None):
        session = self.Session()
        noticia_db = session.query(model.Noticia)
        if filters:
            for (key, value) in filters.items():
                try:
                    if isinstance(value, bool) or value is None:
                        noticia_db = noticia_db.filter(getattr(model.Noticia,key).is_(value))
                    else:
                        noticia_db = noticia_db.filter(getattr(model.Noticia,key)==value)
                except:
                    print("No existe la columna "+key)
                    return []
        noticia_db = noticia_db.all()
        session.close()
        return noticia_db
