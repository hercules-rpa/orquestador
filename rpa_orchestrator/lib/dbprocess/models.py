# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, null, text, Table, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Basereguladora(Base):
    __tablename__ = 'basereguladora'

    id = Column(Integer, primary_key=True, server_default=text("nextval('basereguladora_id_seq'::regclass)"))
    id_base = Column(String(255), nullable=False, unique=True)
    fecha_creacion = Column(DateTime, nullable=False)
    titulo = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    notificada = Column(Boolean)
    seccion = Column(String(500))
    departamento = Column(String(500))

class Convocatoria(Base):
    __tablename__ = 'convocatoria'

    id = Column(Integer, primary_key=True, server_default=text("nextval('convocatoria_id_seq'::regclass)"))
    fecha_creacion = Column(DateTime)
    fecha_publicacion = Column(DateTime)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    fecha_definitiva = Column(DateTime)
    titulo = Column(String(500))
    _from = Column(String(255))
    url = Column(String(1000))
    entidad_gestora = Column(String(1000))
    entidad_convocante = Column(String(1000))
    area_tematica = Column(String(1000))
    observaciones = Column(String(5000))
    id_sgi = Column(String(100))
    notificada = Column(Boolean)
    unidad_gestion = Column(String(1000))
    modelo_ejecucion = Column(String(1000))

class Solicitud(Base):
    __tablename__ = 'solicitud'

    id = Column(Integer, primary_key=True, server_default=text("nextval('solicitud_id_seq'::regclass)"))
    id_solicitud = Column(String(255))
    email = Column(String(255))
    concesion = Column(Boolean)
    referencia_proyecto = Column(String(255))
    ip = Column(String(255))
    fecha_creacion = Column(DateTime)

class Ejecucion_Boletin(Base):
    __tablename__ = 'ejecucion_boletin'

    id = Column(Integer, primary_key=True, server_default=text("nextval('ejecucion_boletin_id_seq'::regclass)"))
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    fecha_ejecucion = Column(DateTime)
    exito = Column(Boolean)
    
class Areatematica(Base):
    __tablename__ = 'areatematica'

    id = Column(Integer, primary_key=True, server_default=text("nextval('areatematica_id_seq'::regclass)"))
    fuente = Column(String(255))
    nombre = Column(String(500), nullable=False)
    descripcion = Column(String(500), nullable=False)

    parents = relationship(
        'Areatematica',
        secondary='areatematica_areatematica',
        primaryjoin='Areatematica.id == areatematica_areatematica.c.areatematicaid',
        secondaryjoin='Areatematica.id == areatematica_areatematica.c.areatematicaidhijo'
    )

class Investigador(Base):
    __tablename__ = 'investigador'

    id = Column(Integer, primary_key=True, unique=True, server_default=text("nextval('investigador_id_seq'::regclass)"))
    nombre = Column(String(500))
    email = Column(String(800), nullable=False, unique=True)
    perfil = Column(Boolean)

t_areatematica_areatematica = Table(
    'areatematica_areatematica', metadata,
    Column('areatematicaid', ForeignKey('areatematica.id'), primary_key=True, nullable=False),
    Column('areatematicaidhijo', ForeignKey('areatematica.id'), primary_key=True, nullable=False)
)

class Calificacionarea(Base):
    __tablename__ = 'calificacionarea'

    id = Column(Integer, primary_key=True, unique=True, server_default=text("nextval('calificacionarea_id_seq'::regclass)"))
    idinvestigador = Column(ForeignKey('investigador.id'), nullable=False)
    idarea = Column(ForeignKey('areatematica.id'))
    puntuacion = Column(Float)

    areatematica = relationship('Areatematica')
    investigador = relationship('Investigador')

class Calificacionconvocatoria(Base):
    __tablename__ = 'calificacionconvocatoria'

    id = Column(Integer, primary_key=True, server_default=text("nextval('calificacionconvocatoria_id_seq'::regclass)"))
    idconvocatoriasgi = Column(Integer, nullable=False, index=True)
    titulo = Column(String(1000), nullable=False)
    idinvestigador = Column(ForeignKey('investigador.id'), nullable=False)
    puntuacion = Column(Float, nullable=False)

    investigador = relationship('Investigador')

class Notificacioninvestigador(Base):
    __tablename__ = 'notificacioninvestigador'

    id = Column(Integer, primary_key=True, unique=True, server_default=text("nextval('notificacioninvestigador_id_seq'::regclass)"))
    idinvestigador = Column(ForeignKey('investigador.id'), nullable=False, index=True)
    idconvocatoriasgi = Column(Integer, nullable=False, index=True)
    feedback = Column(Boolean, nullable=False)
    fechacreacion = Column(DateTime, nullable=False)

    investigador = relationship('Investigador')