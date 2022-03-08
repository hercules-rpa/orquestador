# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, text
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


class Sgi(Base):
    __tablename__ = 'sgi'

    id = Column(Integer, primary_key=True, server_default=text("nextval('sgi_id_seq'::regclass)"))
    id_sgi = Column(String(255), nullable=False)
    url = Column(String(255))
    fecha_creacion = Column(DateTime, nullable=False)


class Convocatoria(Base):
    __tablename__ = 'convocatoria'

    id = Column(Integer, primary_key=True, server_default=text("nextval('convocatoria_id_seq'::regclass)"))
    fecha_creacion = Column(DateTime)
    fecha_publicacion = Column(DateTime)
    titulo = Column(String(500))
    _from = Column(String(255))
    url = Column(String(1000))
    entidad_gestora = Column(String(1000))
    entidad_convocante = Column(String(1000))
    area_tematica = Column(String(1000))
    observaciones = Column(String(5000))
    sgiid = Column(ForeignKey('sgi.id'))
    basereguladoraid = Column(ForeignKey('basereguladora.id'))
    notificada = Column(Boolean)
    unidad_gestion = Column(String(1000))
    modelo_ejecucion = Column(String(1000))

    basereguladora = relationship('Basereguladora')
    sgi = relationship('Sgi')


class Solicitud(Base):
    __tablename__ = 'solicitud'

    id = Column(Integer, primary_key=True, server_default=text("nextval('solicitud_id_seq'::regclass)"))
    id_solicitud = Column(String(255))
    email = Column(String(255))
    concesion = Column(Boolean)
    referencia_proyecto = Column(String(255))
    ip = Column(String(255))
    fecha_creacion = Column(DateTime)
    sgiid = Column(ForeignKey('sgi.id'))

    sgi = relationship('Sgi')

class Noticia(Base):
    __tablename__ = 'noticia'

    id = Column(Integer, primary_key=True, server_default=text("nextval('noticia_id_seq'::regclass)"))
    titulo = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    autor = Column(String(1000), nullable=False)
    fecha = Column(DateTime)
    notificada = Column(Boolean)