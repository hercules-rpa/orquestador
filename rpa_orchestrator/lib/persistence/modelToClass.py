from datetime import datetime

from model.OrchestratorSettings import OrchestratorSettings
from model.DBBISettings import DBBISettings
from model.DBProcessSettings import DBProcessSettings
from model.AMQPSettings import AMQPSettings
from model.GlobalSettings import GlobalSettings
from model.ProcessSettings import ProcessSettings
from model.User import User

from model.Event import MSG_TYPE
from rpa_orchestrator.lib.ScheduleProcess import ScheduleProcess
from rpa_robot.robot           import Robot
from model.Event                import Event
from model.File                 import File
from model.Log                  import Log
from datetime                   import datetime

def toLog(logs_db) -> Log:
    from rpa_orchestrator.orchestrator import Orchestrator
    logs = []
    for log_db in logs_db:
        log = Log(id=log_db.id, id_schedule=log_db.id_schedule, id_process=log_db.id_process, id_robot=log_db.id_robot, log_file_path=log_db.log_file_path, process_name=Orchestrator().get_process_class_name_by_id(log_db.id_process))
        log.data          = log_db.data
        log.state         = log_db.state
        if log_db.start_time:
            log.start_time = datetime.fromisoformat(str(log_db.start_time)).timestamp()
        else:
            log.start_time = None
        if log_db.end_time:
            log.end_time = datetime.fromisoformat(str(log_db.end_time)).timestamp()
        else:
            log.end_time = None
        log.completed = log_db.completed
        log.finished  = log_db.finished
        logs.append(log)
    return logs


def toSchedule(schs_db):
    from rpa_orchestrator.orchestrator import Orchestrator
    schedules=[]
    for sdb in schs_db:
        schedule = ScheduleProcess(id=sdb.id,id_robot=sdb.id_robot, schedule_json=sdb.schedule_json,function=Orchestrator().do_job_schedule)
        #schedule.next_run = datetime.fromisoformat(str(sdb.next_run))
        schedule.created = datetime.fromisoformat(str(sdb.created))
        schedules.append(schedule)
    return schedules

def toRobot(robots_db):
    robots = []
    for robot_db in robots_db:
        robot = Robot(id=robot_db.id, name=robot_db.name, address=robot_db.address, registrations=robot_db.registrations, online=False, connected=None, features=robot_db.features.split(","))
        robot.os = robot_db.os
        robot.mac=robot_db.mac
        robot.ip_address=robot_db.ip_address
        robot.python_version =robot_db.python_version
        robot.performance = [0] * 3
        robots.append([robot, datetime.fromisoformat(str(robot_db.last_seen))])
    return robots

def toEvent(events_db):
    events = []
    for event_db in events_db:
        event = Event(id=event_db.id, body=event_db.body, msgtype=MSG_TYPE(event_db.msgtype).name, read=event_db.read)
        events.append(event)
    return events

def toFile(files_db):
    files = []
    for f in files_db:
        file = File(id=f.id, name=f.name, url_cdn=f.url_cdn)
        files.append(file)
    return files

def toGlobal_Settings(global_settings_db):
    global_settings = []
    for i in global_settings_db:
        gs = GlobalSettings(edma_host_sparql=i.edma_host_sparql,edma_host_servicios=i.edma_host_servicios,edma_port_sparql=i.edma_port_sparql,sgi_user=i.sgi_user,sgi_password=i.sgi_password,sgi_ip=i.sgi_ip,sgi_port=i.sgi_port,url_upload_cdn=i.url_upload_cdn,url_release=i.url_release)
        global_settings.append(gs)
    return global_settings


def toAMQP_Settings(settings_db):
    settings = []
    for i in settings_db:
        gs = AMQPSettings(username=i.user,password=i.password,host=i.host,port=i.port,subscriptions=i.subscriptions,exchange_name=i.exchange_name,queue_name=i.queue_name)
        settings.append(gs)
    return settings

def toDBProcess_Settings(settings_db):
    settings = []
    for i in settings_db:
        gs = DBProcessSettings(username=i.user,password=i.password,host=i.host,port=i.port,database=i.database)
        settings.append(gs)
    return settings

def toDBBI_Settings(settings_db):
    settings = []
    for i in settings_db:
        gs = DBBISettings(username=i.user,password=i.password,host=i.host,port=i.port,keyspace=i.keyspace)
        settings.append(gs)
    return settings

def toOrchestrator_Settings(settings_db):
    settings = []
    for i in settings_db:
        gs = OrchestratorSettings(id_orch=i.id_orch,name=i.name,company=i.company,pathlog_store=i.pathlog_store,cdn_url=i.cdn_url)
        settings.append(gs)
    return settings

def toProcess_Settings(settings_db):
    settings = []
    for i in settings_db:
        gs = ProcessSettings(salaprensa_url=i.salaprensa_url,ucc_url=i.ucc_url,boe_url=i.boe_url,bdns_url=i.bdns_url,bdns_search=i.bdns_search,europe_url=i.europe_url, europe_link=i.europe_link)
        settings.append(gs)
    return settings

def toUser(settings_db):
    settings = []
    for i in settings_db:
        gs = User(username=i.username,password=i.password,token=i.token)
        settings.append(gs)
    return settings

def toProcess(process_db):
    process = []
    for p in process_db:
        p_dict = {}
        p_dict['id'] = p.id
        p_dict['class'] = p._class
        p_dict['name'] = p.name
        p_dict['requirements'] = p.requirements.split()
        p_dict['description'] = p.description
        p_dict['visible'] = p.visible
        p_dict['setting'] = p.setting
        process.append(p_dict)
    return process

        
