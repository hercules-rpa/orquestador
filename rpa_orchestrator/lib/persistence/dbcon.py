from logging import log
from model.GlobalSettings import GlobalSettings
from sqlalchemy import create_engine
from sqlalchemy import Column, String, desc, asc, and_, or_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from rpa_orchestrator.lib.Schedule import next_run
from rpa_orchestrator.lib.ScheduleProcess import ScheduleProcess
from rpa_robot.robot import Robot
from model.Event import Event
from model.Log import Log
from model.File  import File
from datetime import datetime, timedelta
import rpa_orchestrator.lib.persistence.modelToClass as modelToClass
import rpa_orchestrator.lib.persistence.models as model
import json


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ControllerDBPersistence(metaclass=Singleton):
    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.db = create_engine("postgresql://"+user +
                                ":"+password+"@"+host+":"+port+"/"+database)
        self.base = declarative_base()
        self.Session = sessionmaker(self.db)

    def dump(self, objects):
        session = self.Session()
        for object in objects:
            ans = None
            if isinstance(object, Robot):
                ans = model.Robot(id=object.id, name=object.name, address=object.address, registrations=object.registrations, ip_address=object.ip_address, mac=object.mac, features=','.join(
                    object.features), os=object.os, python_version=object.python_version, last_seen=datetime.now().isoformat(), connected=(datetime.fromtimestamp(object.connected)).isoformat(), created=datetime.now().isoformat())
                exists = session.query(model.Robot).filter_by(
                    id=object.id).first()

                if not exists:
                    session.add(ans)
                    session.commit()
                else:
                    exists.name = ans.name
                    exists.ip_address = ans.ip_address
                    exists.mac = ans.mac
                    exists.os = ans.os
                    exists.python_version = ans.python_version
                    exists.features = ans.features
                    exists.last_seen = ans.last_seen
                    exists.connected = ans.connected
                    session.commit()

            elif isinstance(object, Event):
                ans = model.Event(body=object.body, msgtype=object.msgtype.value, time=(
                    datetime.fromtimestamp(object.time)).isoformat(), sender=object.sender, read=object.read)
                if not object.id:
                    session.add(ans)
                    session.commit()
                    session.refresh(ans)
                    object.id = ans.id
                else:
                    exists = session.query(model.Event).filter_by(
                        id=object.id).first()
                    if exists:
                        exists.read = object.read
                        session.commit()

            elif isinstance(object, ScheduleProcess):
                ans = model.Schedule(id_robot=object.id_robot, schedule_json=object.schedule_json,
                                     active=True, created=object.created.isoformat())
                if not object.id:
                    session.add(ans)
                    session.commit()
                    session.refresh(ans)
                    object.id = ans.id
                else:
                    exists = session.query(model.Schedule).filter_by(
                        id=object.id).first()
                    if exists:
                        exists.schedule_json = ans.schedule_json
                        exists.active = object.is_active()
                        exists.next_run = object.get_next_run()
                        session.commit()

            elif isinstance(object, Log):
                ans = model.Log(id_schedule=object.id_schedule, id_process=object.id_process, id_robot=object.id_robot, log_file_path=object.log_file_path,
                                data=object.data, start_time=object.start_time, end_time=object.end_time, state=object.state, completed=object.completed, finished=object.finished)
                ans2 = model.RobotSchedule(
                    robotid=object.id_robot, scheduleid=object.id_schedule)
                if not object.id:
                    session.add(ans)
                    exists = session.query(model.RobotSchedule).filter_by( 
                        robotid=object.id_robot, scheduleid=object.id_schedule).first()
                    if not exists:
                        session.add(ans2) #Actualizamos el estado del robot
                    session.commit()
                    session.refresh(ans)
                    object.id = ans.id
                else:
                    exists = session.query(model.Log).filter_by(
                        id=object.id).first()
                    if exists:
                        exists.data = ans.data
                        exists.state = ans.state
                        exists.start_time = (datetime.fromtimestamp(
                            ans.start_time)).isoformat()
                        if object.end_time:
                            exists.end_time = (datetime.fromtimestamp(
                                ans.end_time)).isoformat()
                        exists.finished  = ans.finished
                        exists.completed = ans.completed
                        session.commit()

            elif isinstance(object, File):
                ans = model.File(id = object.id, name = object.name, url_cdn = object.url_cdn)
                if not object.id:
                    session.add(ans)
                    session.commit()
                    session.refresh(ans)
                    object.id = ans.id

            elif isinstance(object, model.GlobalSettings):
                exists = session.query(model.GlobalSettings).filter_by(id=object.id).first()
                if not exists:
                    session.add(object)
                    session.commit()
                    session.refresh(object)


        session.close()

    def read_all_logs(self):
        session = self.Session()
        logs_db = session.query(model.Log).all()
        session.close()
        return modelToClass.toLog(logs_db)

    def read_log_byid(self, id):
        session = self.Session()
        log_db = session.query(model.Log).filter_by(id=id).first()
        session.close()
        if log_db:
            return modelToClass.toLog([log_db])[0]
        return None

    def read_logs_byidschedule(self, id):
        session = self.Session()
        logs_db = session.query(model.Log).filter_by(
            id_schedule=id).order_by(desc(model.Log.id_schedule))
        session.close()
        return modelToClass.toLog(logs_db)

    def read_logs_byidrobot(self, id):
        session = self.Session()
        logs_db = session.query(model.Log).filter(
            and_(model.Log.id_robot == id, model.Log.start_time != None)).all()
        session.close()
        return modelToClass.toLog(logs_db)

    def read_logs_byidrobot_last(self, id, nlast):
        session = self.Session()
        logs_db = session.query(model.Log).filter_by(id_robot=id).filter(
            model.Log.end_time.isnot(None)).order_by(desc(model.Log.end_time)).limit(nlast).all()
        session.close()
        return modelToClass.toLog(logs_db)

    def read_logs_byidrobot_lastproblems(self, id, nlast):
        session = self.Session()
        if id:
            logs_db = session.query(model.Log).filter_by(id_robot=id).filter(model.Log.end_time.isnot(
                None)).filter(model.Log.state == "ERROR").order_by(desc(model.Log.end_time))
        else:
            logs_db = session.query(model.Log).filter(model.Log.end_time.isnot(None)).filter(
                model.Log.state == "ERROR").order_by(desc(model.Log.end_time))
        if nlast == 0:
            logs_db = logs_db.all()
        else:
            logs_db = logs_db.limit(nlast)
    #        logs_db = logs_db.all()
        session.close()
        return modelToClass.toLog(logs_db)

    def read_logs_problem_count(self):
        session = self.Session()
        problems = session.query(model.Log).filter(
            model.Log.state == "ERROR").count()
        session.close()
        return problems

    def read_all_schedules(self, filters=None):
        session = self.Session()
        schedules_db = session.query(model.Schedule)
        if filters:
            for (key, value) in filters.items():
                try:
                    if key == 'limit':
                        continue
                    if isinstance(value, bool) or value is None:
                        schedules_db = schedules_db.filter(
                            getattr(model.Schedule, key).is_(value))
                    else:
                        schedules_db = schedules_db.filter(
                            getattr(model.Schedule, key) == value)
                except:
                    print("No existe la columna "+key)
                    return []
            if 'limit' in filters:
                schedules_db = schedules_db.limit(filters['limit'])

        schedules_db = schedules_db.all()
        session.close()
        return modelToClass.toSchedule(schedules_db)

    def read_events(self, filters=None):
        session = self.Session()
        events_db = session.query(model.Event)
        if filters:
            for (key, value) in filters.items():
                try:
                    events_db = events_db.filter(
                        getattr(model.Event, key) == value)
                except:
                    print("No existe la columna "+key)
                    return []

        events_db = events_db.all()
        session.close()
        return modelToClass.toEvent(events_db)

    def read_schedule_byid(self, id):
        session = self.Session()
        schedule_db = session.query(model.Schedule).filter_by(id=id).first()
        session.close()
        if schedule_db:
            return modelToClass.toSchedule([schedule_db])[0]
        return None

    def read_files(self,id):
        session = self.Session()
        if id:
            file_db = session.query(model.File).filter_by(id=id).first()
            session.close()
            if file_db:
                return modelToClass.toFile([file_db])[0]
        else:
            file_db = session.query(model.File).all()
            session.close()
            return modelToClass.toFile(file_db)    
        return []


    def get_global_settings_by_id(self, id=1):
        session = self.Session()
        global_settings = session.query(model.GlobalSettings).filter_by(id=id).first()
        session.close()
        if global_settings:
            return modelToClass.toGlobal_Settings([global_settings])[0]
        return None
    
    def update_global_settings(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.GlobalSettings).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (global settings)")
                session.close()
                return False
        session.close()
        return False


    def get_amqp_settings_by_id(self, id=1):
        session = self.Session()
        settings = session.query(model.AMQPSettings).filter_by(id=id).first()
        session.close()
        if settings:
            return modelToClass.toAMQP_Settings([settings])[0]
        return None
    
    def update_amqp_settings(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.AMQPSettings).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (amqp settings)")
                session.close()
                return False
        session.close()
        return False

    def get_dbpersistence_settings_by_id(self, id):
        session = self.Session()
        settings = session.query(model.DBPersistenceSettings).filter_by(id=id).first()
        session.close()
        if settings:
            return modelToClass.toDBPersistence_Settings([settings])[0]
        return None
    
    def update_dbpersistence_settings(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.DBPersistenceSettings).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (amqp settings)")
                session.close()
                return False
        session.close()
        return False


    def get_dbprocess_settings_by_id(self, id=1):
        session = self.Session()
        settings = session.query(model.DBProcessSettings).filter_by(id=id).first()
        session.close()
        if settings:
            return modelToClass.toDBProcess_Settings([settings])[0]
        return None
    
    def update_dbprocess_settings(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.DBProcessSettings).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (amqp settings)")
                session.close()
                return False
        session.close()
        return False

    def get_dbbi_settings_by_id(self, id=1):
        session = self.Session()
        settings = session.query(model.DBBISettings).filter_by(id=id).first()
        session.close()
        if settings:
            return modelToClass.toDBBI_Settings([settings])[0]
        return None
    
    def update_dbbi_settings(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.DBBISettings).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (amqp settings)")
                session.close()
                return False
        session.close()
        return False
        

    def get_orchestrator_settings_by_id(self, id=1):
        session = self.Session()
        settings = session.query(model.OrchestratorSettings).filter_by(id=id).first()
        session.close()
        if settings:
            return modelToClass.toOrchestrator_Settings([settings])[0]
        return None
    
    def update_orchestrator_settings(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.OrchestratorSettings).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (orchestrator settings)")
                session.close()
                return False
        session.close()
        return False



    def get_process_settings_by_id(self, id):
        session = self.Session()
        settings = session.query(model.ProcessSettings).filter_by(id=id).first()
        session.close()
        if settings:
            return modelToClass.toProcess_Settings([settings])[0]
        return None
    
    def update_process_settings(self, id, new_parameters):
        session = self.Session()
        exists = session.query(model.ProcessSettings).filter_by(id=id).first()
        if exists:
            try: 
                for (key, value) in new_parameters.items():
                    setattr(exists, key, value)
                session.commit()
                session.close()
                return True
            except:
                print("No existe el campo "+key+" o el valor es erroneo (process settings)")
                session.close()
                return False
        session.close()
        return False

    def read_process_dynamic(self, filter=None, value=None):
        session = self.Session()
        process_db = session.query(model.Process)
        if filter:
            process_db = process_db.filter(
                getattr(model.Process, filter) == value)
        else:
            process_db = session.query(model.Process).all()

        session.close()
        return modelToClass.toProcess(process_db)

    # Persistencia

    def read_robots_feed(self):
        session = self.Session()
        robots_db = session.query(model.Robot).all()
        session.close()
        return modelToClass.toRobot(robots_db)

    def read_schedules_feed(self):
        session = self.Session()
        schedules_db = session.query(model.Schedule).filter(
            model.Schedule.active == True).all()
        schdules_db_fixed = []
        for sch in schedules_db:
            s = modelToClass.toSchedule([sch])[0]
            if not sch.next_run:
                sch.next_run = datetime.now()-timedelta(days=1)
            if datetime.fromisoformat(str(sch.next_run)) <= datetime.now() and not s.get_forever():
                sch.active = False
                session.commit()
            else:
                schdules_db_fixed.append(s)

        session.close()
        return schdules_db_fixed
