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
        self.db = create_engine("postgresql://"+user+":"+password+"@"+host+":"+port+"/"+database,pool_size=50, max_overflow=0)  
        self.base = declarative_base()
        self.Session = sessionmaker(self.db)

    def dump(self,objects):
        session = self.Session()
        session.expire_on_commit = False
        for object in objects:
            if isinstance(object, model.Convocatoria):
                exists = session.query(model.Convocatoria).filter_by(url=object.url).first()
                if not object.id and not exists:
                    object.fecha_creacion = datetime.today().isoformat()
                    if object.fecha_publicacion:
                        object.fecha_publicacion = datetime.fromtimestamp(object.fecha_publicacion).isoformat()
                    if object.fecha_inicio:
                        object.fecha_inicio = datetime.fromtimestamp(object.fecha_inicio).isoformat()
                    if object.fecha_fin:
                        object.fecha_fin = datetime.fromtimestamp(object.fecha_fin).isoformat()
                    if object.fecha_definitiva:
                        object.fecha_definitiva = datetime.fromtimestamp(object.fecha_definitiva).isoformat()
                    session.add(object)
                    session.commit()
                    session.refresh(object)
                else:
                    if not exists:
                        exists = session.query(model.Convocatoria).filter_by(id=object.id).first()
                    if exists:
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
                    exists.notificada   = object.notificada
                    exists.titulo       = object.titulo
                    exists.url          = object.url
                    exists.seccion      = object.seccion
                    exists.departamento = object.departamento
                    object.id           = exists.id
                    session.commit()

            elif isinstance(object, model.Ejecucion_Boletin):
                exists = session.query(model.Ejecucion_Boletin).filter_by(id=object.id).first()
                if not exists:
                    if object.fecha_inicio:
                        object.fecha_inicio = datetime.fromtimestamp(object.fecha_inicio).isoformat()
                    if object.fecha_fin:
                        object.fecha_fin = datetime.fromtimestamp(object.fecha_fin).isoformat()
                    if object.fecha_ejecucion:
                        object.fecha_ejecucion = datetime.fromtimestamp(object.fecha_ejecucion).isoformat()
                    session.add(object)
                    session.commit()
                    session.refresh(object)
                else:
                    exists.fecha_inicio         = object.fecha_inicio
                    exists.fecha_fin            = object.fecha_fin
                    exists.fecha_ejecucion      = object.fecha_ejecucion
                    exists.exito                = object.exito
                    object.id                   = exists.id
                    session.commit()


            elif isinstance(object, model.Investigador):
                exists = session.query(model.Investigador).filter_by(email=object.email).first()
                if not exists:
                    session.add(object)
                    session.commit()
                    session.refresh(object)

            elif isinstance(object, model.Areatematica):
                print(object.nombre)
                print(object.parents)
                exists = session.query(model.Areatematica).filter(model.Areatematica.nombre==object.nombre, model.Areatematica.fuente==object.fuente).first()
                if not exists:
                    session.add(object)
                    session.commit()
                    session.refresh(object)
                else:
                    if len(object.parents) > 0:
                        child_at = object.parents[0]
                        exists_child = session.query(model.t_areatematica_areatematica).filter(model.t_areatematica_areatematica.c.areatematicaidhijo==child_at.id,model.t_areatematica_areatematica.c.areatematicaid==object.id).first()
                        print(exists_child)
                        if not exists_child:
                            exists.parents.append(child_at)
                            session.commit()

            elif isinstance(object, model.Calificacionarea):
                exists = session.query(model.Calificacionarea).filter(model.Calificacionarea.idinvestigador==object.idinvestigador, model.Calificacionarea.idarea==object.idarea).first()
                if not exists:
                    session.add(object)
                    session.commit()
                    session.refresh(object)
                else:
                    exists.puntuacion = object.puntuacion
                    session.commit()

            elif isinstance(object, model.Calificacionconvocatoria):
                exists = session.query(model.Calificacionconvocatoria).filter(model.Calificacionconvocatoria.idinvestigador==object.idinvestigador, model.Calificacionconvocatoria.idconvocatoriasgi==object.idconvocatoriasgi).first()
                if not exists:
                    session.add(object)
                    session.commit()
                    session.refresh(object)
                else:
                    exists.puntuacion = object.puntuacion
                    session.commit()

            elif isinstance(object, model.Notificacioninvestigador):
                exists = session.query(model.Notificacioninvestigador).filter_by(id=object.id).first()
                if not exists:
                    session.add(object)
                    session.commit()
                    session.refresh(object)

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
        session.close()
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
        session.close()
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
        session.close()
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
        session.close()
        return False   

    def update_investigador(self, id, new_parameters):
            session = self.Session()
            exists = session.query(model.Investigador).filter_by(id=id).first()
            if exists:
                try: 
                    for (key, value) in new_parameters.items():
                        setattr(exists, key, value)
                    session.commit()
                    session.close()
                    return True
                except:
                    print("No existe el campo "+key+" o el valor es erroneo (investigador)")
                    session.close()
                    return False
            session.close()
            return False

    def update_areatematica(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Areatematica).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (area tematica)")
                session.close()
                return False
        session.close()
        return False

    def update_calificacionarea(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Calificacionarea).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (calificacion area)")
                session.close()
                return False
        session.close()
        return False

    def update_calificacionConvocatoria(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Calificacionconvocatoria).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (calificacion area)")
                session.close()
                return False
        session.close()
        return False

    def update_notificacionInvestigador(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Notificacioninvestigador).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (notificacion investigador)")
                session.close()
                return False
        session.close()
        return False

    def update_ejecucion_boletin(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Ejecucion_Boletin).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (Ejecucion_Boletin)")
                session.close()
                return False
        session.close()
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
                    session.close()
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
                    session.close()
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
                    session.close()
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
                    session.close()
                    return []
        basereguladora_db = basereguladora_db.all()
        session.close()
        return basereguladora_db

    def read_ejecucion_notificacion(self, filters=None):
        session = self.Session()
        notificacion_db = session.query(model.Ejecucion_Boletin)
        if filters:
            for (key, value) in filters.items():
                try:
                    if isinstance(value, bool) or value is None:
                        notificacion_db = notificacion_db.filter(getattr(model.Ejecucion_Boletin,key).is_(value))
                    else:
                        notificacion_db = notificacion_db.filter(getattr(model.Ejecucion_Boletin,key)==value)
                except:
                    print("No existe la columna "+key)
                    session.close()
                    return []
        notificacion_db = notificacion_db.all()
        session.close()
        return notificacion_db

    def read_investigador(self, filters=None):
            session = self.Session()
            investigador_db = session.query(model.Investigador)
            if filters:
                for (key, value) in filters.items():
                    try:
                        if isinstance(value, bool) or value is None:
                            investigador_db = investigador_db.filter(getattr(model.Investigador,key).is_(value))
                        else:
                            investigador_db = investigador_db.filter(getattr(model.Investigador,key)==value)
                    except:
                        print("No existe la columna "+key)
                        session.close()
                        return []
            investigador_db = investigador_db.all()
            session.close()
            return investigador_db

    def read_areatematica(self, filters=None):
        session = self.Session()
        areatematica_db = session.query(model.Areatematica)
        if filters:
            for (key, value) in filters.items():
                try:
                    if isinstance(value, bool) or value is None:
                        areatematica_db = areatematica_db.filter(getattr(model.Areatematica,key).is_(value))
                    else:
                        areatematica_db = areatematica_db.filter(getattr(model.Areatematica,key)==value)
                except:
                    print("No existe la columna "+key)
                    session.close()
                    return []
        areatematica_db = areatematica_db.all()
        session.close()
        return areatematica_db

    def read_areatematica_id(self, id):
        session = self.Session()
        areatematica_db = session.query(model.Areatematica, model.t_areatematica_areatematica).join(model.t_areatematica_areatematica, model.t_areatematica_areatematica.c.areatematicaid == model.Areatematica.id ).filter(model.Areatematica.id == id).all()
        if len(areatematica_db) > 0:
            session.close()
            return areatematica_db
        else:
            areatematica_db =session.query(model.Areatematica).filter(model.Areatematica.id == id).all()
        session.close()
        return areatematica_db

    def read_areatematica_id_padre(self,id):
        session = self.Session()
        areatematica_db = session.query(model.t_areatematica_areatematica.c.areatematicaid).join(model.Areatematica, model.t_areatematica_areatematica.c.areatematicaidhijo == model.Areatematica.id ).filter(model.Areatematica.id == id).all()
        session.close()
        return areatematica_db

    def read_calificacionArea(self, filters=None):
        session = self.Session()
        calificacionarea_db = session.query(model.Calificacionarea)
        if filters:
            for (key, value) in filters.items():
                try:
                    if isinstance(value, bool) or value is None:
                        calificacionarea_db = calificacionarea_db.filter(getattr(model.Calificacionarea,key).is_(value))
                    else:
                        calificacionarea_db = calificacionarea_db.filter(getattr(model.Calificacionarea,key)==value)
                except:
                    print("No existe la columna "+key)
                    return []
        calificacionarea_db = calificacionarea_db.all()
        session.close()
        return calificacionarea_db

    def read_calificacionConvocatoria(self, filters=None):
            session = self.Session()
            calificacionconvocatoria_db = session.query(model.Calificacionconvocatoria)
            if filters:
                for (key, value) in filters.items():
                    try:
                        if isinstance(value, bool) or value is None:
                            calificacionconvocatoria_db = calificacionconvocatoria_db.filter(getattr(model.Calificacionconvocatoria,key).is_(value))
                        else:
                            calificacionconvocatoria_db = calificacionconvocatoria_db.filter(getattr(model.Calificacionconvocatoria,key)==value)
                    except:
                        print("No existe la columna "+key)
                        session.close()
                        return []
            calificacionconvocatoria_db = calificacionconvocatoria_db.all()
            session.close()
            return calificacionconvocatoria_db

    def read_notificacionInvestigador(self, filters=None):
        session = self.Session()
        notificacionInvestigador_db = session.query(model.Notificacioninvestigador)
        if filters:
            for (key, value) in filters.items():
                try:
                    if isinstance(value, bool) or value is None:
                        notificacionInvestigador_db = notificacionInvestigador_db.filter(getattr(model.Notificacioninvestigador,key).is_(value))
                    else:
                        notificacionInvestigador_db = notificacionInvestigador_db.filter(getattr(model.Notificacioninvestigador,key)==value)
                except:
                    print("No existe la columna "+key)
                    session.close()
                    return []
        notificacionInvestigador_db = notificacionInvestigador_db.all()
        session.close()
        return notificacionInvestigador_db

    def read_last_notificacionInvestigador(self):
        session = self.Session()
        notificacionInvestigador_db = session.query(model.Notificacioninvestigador).order_by(model.Notificacioninvestigador.id.desc()).first()
        session.close()
        return notificacionInvestigador_db


    def update_investigador(self, id, new_parameters):
            session = self.Session()
            exists = session.query(model.Investigador).filter_by(id=id).first()
            if exists:
                try: 
                    for (key, value) in new_parameters.items():
                        setattr(exists, key, value)
                    session.commit()
                    session.close()
                    return True
                except:
                    print("No existe el campo "+key+" o el valor es erroneo (investigador)")
                    session.close()
                    return False
            return False

    def update_areatematica(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Areatematica).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (area tematica)")
                session.close()
                return False
        session.close()
        return False

    def update_calificacionarea(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Calificacionarea).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (calificacion area)")
                session.close()
                return False
        session.close()
        return False

    def update_calificacionConvocatoria(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Calificacionconvocatoria).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (calificacion area)")
                session.close()
                return False
        session.close()
        return False

    def update_notificacionInvestigador(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.Notificacioninvestigador).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (notificacion investigador)")
                session.close()
                return False
        session.close()
        return False
    
    def delete_profile(self, id):
        try:
            session = self.Session()
            session.query(model.Calificacionarea).filter_by(idinvestigador=id).delete()
            session.commit()
            session.close()
            return True
        except Exception as e:
            print("No se pudo eliminar el perfil del investigador "+str(id)+" "+str(e))
            session.close()
            return False
        
