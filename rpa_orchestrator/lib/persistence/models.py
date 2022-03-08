# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, text
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
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True, server_default=text("nextval('file_id_seq'::regclass)"))
    name = Column(String(255), nullable=False)
    absolute_path = Column(String(255), nullable=False)
    directory = Column(String(255), nullable=False)
    time = Column(DateTime)


class RobotSchedule(Base):
    __tablename__ = 'robot_schedule'

    robotid = Column(String(255), primary_key=True, nullable=False)
    scheduleid = Column(ForeignKey('schedule.id'), primary_key=True, nullable=False)

    schedule = relationship('Schedule')