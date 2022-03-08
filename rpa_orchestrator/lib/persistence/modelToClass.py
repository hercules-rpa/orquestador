from datetime import datetime
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
        file = File(id=f.id, name=f.name, absolute_path=f.absolute_path, directory=f.directory, time=datetime.fromisoformat(str(f.time)))
        files.append(file)
    return files

def toProcess(process_db):
    process = []
    for p in process_db:
        p_dict = {}
        p_dict['id'] = p.id
        p_dict['class'] = p._class
        p_dict['name'] = p.name
        p_dict['requirements'] = p.requirements.split()
        p_dict['description'] = p.description
        process.append(p_dict)
    return process

        
