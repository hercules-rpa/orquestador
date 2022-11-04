# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, ARRAY, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, server_default=text("nextval('event_id_seq'::regclass)"))
    body = Column(String(255), nullable=False)
    msgtype = Column(String(255), nullable=False)
    time = Column(DateTime, nullable=False)
    sender = Column(String(255), nullable=False)
    read = Column(Boolean, nullable=False)


class Process(Base):
    __tablename__ = 'process'

    id = Column(Integer, primary_key=True, nullable=False)
    _class = Column('class', String(255))
    name = Column(String(255), nullable=False)
    requirements = Column(String(255))
    description = Column(String(255), nullable=False)
    visible = Column(Boolean, nullable=False)
    setting = Column(Boolean, nullable=False)


class Robot(Base):
    __tablename__ = 'robot'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    ip_address = Column(String(255), nullable=False)
    mac     = Column(String(255))
    address = Column(String(255))
    registrations = Column(String(255))
    python_version = Column(String(255))
    os = Column(String(255))
    features = Column(Text)
    connected = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    created = Column(DateTime, nullable=False)


class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(Integer, primary_key=True, server_default=text("nextval('schedule_id_seq'::regclass)"))
    id_robot = Column(String(255))
    schedule_json = Column(Text, nullable=False)
    active = Column(Boolean, nullable=False)
    created = Column(DateTime,nullable=False)
    next_run = Column(DateTime)


class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True, server_default=text("nextval('log_id_seq'::regclass)"))
    id_schedule = Column(ForeignKey('schedule.id', ondelete='CASCADE'), nullable=False)
    id_process = Column(ForeignKey('process.id'), nullable=False)
    id_robot = Column(String(255), nullable=False)
    log_file_path = Column(String(255), nullable=False)
    data = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    state = Column(String(255))
    completed = Column(Integer, nullable=False)
    finished = Column(Boolean, nullable=False)


    process = relationship('Process')
    schedule = relationship('Schedule')

class File(Base):
    __tablename__ = 'file_cdn'
    id = Column(Integer, primary_key=True, server_default=text("nextval('file_cdn_id_seq'::regclass)"))
    name = Column(String(255), nullable=False)
    url_cdn = Column(String(255), nullable=False)

class GlobalSettings(Base):
    __tablename__ = 'global_settings'
    id = Column(Integer, primary_key=True, server_default=text("nextval('global_settings_id_seq'::regclass)"))
    edma_host_sparql = Column(String(255), nullable=False)
    edma_host_servicios = Column(String(255), nullable=False)
    edma_port_sparql = Column(Integer, nullable=False)
    sgi_user = Column(String(255),nullable=False)
    sgi_password = Column(String(1000), nullable=False)
    sgi_ip = Column(String(255), nullable=False)
    sgi_port = Column(Integer, nullable=False)
    database_ip = Column(String(255), nullable=False)
    database_port = Column(Integer, nullable=False)
    ftp_user = Column(String(255),nullable=False)
    ftp_password = Column(String(1000), nullable=False)
    ftp_port = Column(Integer, nullable=False)

class AMQPSettings(Base):
    __tablename__ = 'amqp_settings'

    id = Column(Integer, primary_key=True, server_default=text("nextval('amqp_settings_id_seq'::regclass)"))
    user = Column(String(1000), nullable=False)
    password = Column(String(1000), nullable=False)
    host = Column(String(1000), nullable=False)
    port = Column(Integer, nullable=False)
    subscriptions = Column(ARRAY(Text()))
    exchange_name = Column(String(100), nullable=False)
    queue_name = Column(String(100), nullable=False)


class DBPersistenceSettings(Base):
    __tablename__ = 'dbpersistence_settings'

    id = Column(Integer, primary_key=True, server_default=text("nextval('dbpersistence_settings_id_seq'::regclass)"))
    user = Column(String(1000), nullable=False)
    password = Column(String(1000), nullable=False)
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    database = Column(String(100), nullable=False)

class DBProcessSettings(Base):
    __tablename__ = 'dbprocess_settings'

    id = Column(Integer, primary_key=True, server_default=text("nextval('dbprocess_settings_id_seq'::regclass)"))
    user = Column(String(1000), nullable=False)
    password = Column(String(1000), nullable=False)
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    database = Column(String(100), nullable=False)

class DBBISettings(Base):
    __tablename__ = 'dbbi_settings'

    id = Column(Integer, primary_key=True, server_default=text("nextval('dbbi_settings_id_seq'::regclass)"))
    user = Column(String(1000), nullable=False)
    password = Column(String(1000), nullable=False)
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    keyspace = Column(String(100), nullable=False)

class OrchestratorSettings(Base):
    __tablename__ = 'orchestrator_settings'

    id = Column(Integer, primary_key=True, server_default=text("nextval('orchestrator_settings_id_seq'::regclass)"))
    id_orch = Column(String(1000), nullable=False)
    name = Column(String(1000), nullable=False)
    company = Column(String(1000), nullable=False)
    pathlog_store = Column(String(1000), nullable=False)
    cdn_url = Column(String(1000), nullable=False)

class ProcessSettings(Base):
    __tablename__ = 'process_settings'

    id = Column(Integer, primary_key=True, server_default=text("nextval('process_settings_id_seq'::regclass)"))
    salaprensa_url = Column(String(255),nullable=False)
    ucc_url = Column(String(255),nullable=False)
    boe_url = Column(String(255),nullable=False)
    bdns_url = Column(String(255),nullable=False)
    bdns_search = Column(String(255),nullable=False)
    europe_url = Column(String(255),nullable=False)
    europe_link = Column(String(255),nullable=False)

class RobotSchedule(Base):
    __tablename__ = 'robot_schedule'

    robotid = Column(String(255), primary_key=True, nullable=False)
    scheduleid = Column(ForeignKey('schedule.id'), primary_key=True, nullable=False)

    schedule = relationship('Schedule')