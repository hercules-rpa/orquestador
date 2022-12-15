import asyncio
import json
import traceback
import hashlib
import logging 
import sys
import os

from model.GlobalSettings import GlobalSettings
from model.OrchestratorSettings import OrchestratorSettings
from model.DBBISettings import DBBISettings
from model.DBProcessSettings import DBProcessSettings
from model.AMQPSettings import AMQPSettings
from model.ProcessSettings import ProcessSettings

import rpa_orchestrator.lib.Schedule as schedule
from model.File import File
import rpa_orchestrator.lib.persistence.dbcon as db
import rpa_orchestrator.lib.bi.dbcon as dbbi
import model.messages as messages
import collections
from model.Event import Event, MSG_TYPE
from rpa_orchestrator.lib.ScheduleProcess import ScheduleProcess
from controller.ControllerAMQP import ControllerAMQP
from model.interfaces.ListenerMsg import ListenerMsg
from datetime import datetime
from model.Log import Log
from customjson.JSONDecoder import JSONDecoder
from customjson.JSONEncoder import JSONEncoder
from threading import Lock
from random import random, seed, randint, choice

TIME_KEEP_ALIVE = 120
TIME_REMOVE_ROBOT = 280

DIRECTORY_PROCESS_FORM = "model/process/forms/"

log_orch = logging.getLogger(__name__)
log_orch.setLevel(logging.INFO)

infoHandler = logging.StreamHandler(sys.stdout)
infoHandler.setLevel(logging.INFO)

errorHandler = logging.StreamHandler(sys.stderr)
errorHandler.setLevel(logging.ERROR)

log_orch.addHandler(infoHandler)
log_orch.addHandler(errorHandler)

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Orchestrator(ListenerMsg, metaclass=Singleton):
    def __init__(self, id_orch, name, company, pathlog_store, cdn_url):
        self.controller = ControllerAMQP()
        self.robot_list = {}
        self.schedule_list = []  # lista de ejecuciones planificadas.
        self.log_list = collections.deque(maxlen=1000)
        self.event_list = collections.deque(maxlen=1000)
        self.id = id_orch
        self.name = name
        self.company = company
        self.pathlog_store = pathlog_store
        try:
            log_file_handler = logging.FileHandler(filename=os.path.join(self.pathlog_store, 'General.log'), encoding='utf-8')
            log_file_handler.setLevel(logging.INFO)
            log_file_handler.mode = 'w'        
            log_orch.addHandler(log_file_handler)
        except:
            print("No se ha podido crear el archivo General.log")
        self.cdn_url = cdn_url
        self.lock = Lock()
        self.process = {}
        self.db = db.ControllerDBPersistence()
        self.dbbi = dbbi.ControllerDBBI()
        self.token_revoke = []

    def reload_robot(self):
        robots = self.db.read_robots_feed()
        self.robot_list = {}
        for robot in robots:
            self.robot_list[robot[0].id] = (robot[0], robot[1])

    def reload_schedule(self):
        self.lock.acquire()
        try:
            schedules = self.db.read_schedules_feed()
            self.schedule_list = []
            for s in schedules:
                self.schedule_list.append(s)
                s.time_to_schedule()
                self.db.dump([s])
        except Exception as e:
            log_orch.error(str(e))
        finally:
            self.lock.release()

    def reload_process(self):
        process_json = self.db.read_process_dynamic()
        self.process = {}
        for p in process_json:
            self.process[str(p['id'])] = p

    def restart(self):
        pass

    async def notify_msg(self, msg):
        await self.handle_msg(msg)

    async def handle_msg(self, msg):
        msg = json.loads(msg)
        type_msg = msg['TYPE_MSG']
        if(type_msg == messages.INIT):
            await self.handle_msgInit(msg)
        elif(type_msg == messages.KEEP_ALIVE):
            await self.handle_msgKeepAlive(msg)
        elif(type_msg == messages.MSG_CREATE_PROCESS):
            await self.handle_msgCreateProcess(msg)
        elif(type_msg == messages.MSG_EXEC_PROCESS):
            await self.handle_msgExecProcess(msg)
        elif(type_msg == messages.LOG):
            await self.handle_msgLog(msg)
        elif(type_msg == messages.NOTIFY):
            await self.handle_msgNotify(msg)
        elif(type_msg == messages.UPDATE_INFO):
            await self.handle_msgUpdateInfo(msg)
        elif(type_msg == messages.PENDING_PROCESS):
            await self.handle_msgPendingProcess(msg)

    async def handle_msgInit(self, msg):
        robot = JSONDecoder().decode(json.dumps(msg['ROBOT']))
        self.robot_list[robot.id] = (robot, datetime.now())
        robot.online = True
        log_orch.info("Robot "+ robot.name + " con id " + str(robot.id) +
              " inicia la conexion con el orquestador. " + robot.address)
        event = Event(body="Robot "+robot.name +
                      " inicia la conexion con el orquestador. ", msgtype=MSG_TYPE.CONNECTION)
        self.event_list.append(event)
        self.db.dump([robot, event])
        self.dbbi.dump_robot(robot, self.id, self.name, self.company)
        self.dbbi.dump_robot_performance(
            robot, self.id, self.name, self.company)
        await self.__send_message(messages.ROUTE_ROBOT+robot.id, json.dumps(messages.MSG_INIT_ORC))

    async def handle_msgKeepAlive(self, msg):
        robot = JSONDecoder().decode(json.dumps(msg['ROBOT']))
        if robot.id in self.robot_list and not self.robot_list[robot.id][0].online:
            event = Event(body="Robot "+robot.name +
                          " se ha reconectado. ", msgtype=MSG_TYPE.CONNECTION)
            self.robot_list[robot.id][0].online = True
            self.db.dump([robot, event])
            self.event_list.append(event)
        if robot.id in self.robot_list and self.robot_list[robot.id][0].token == robot.token and self.robot_list[robot.id][0].online:
            event = Event(body="Robot "+robot.name +
                          " ha mandado Keep Alive. ", msgtype=MSG_TYPE.CONNECTION)
            self.robot_list[robot.id] = (robot, datetime.now())
            self.dbbi.dump_robot_performance(
                robot, self.id, self.name, self.company)
            self.db.dump([event])
            log_orch.info("Keep Alive " + str(robot.id) + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    async def handle_msgExecProcess(self, msg):
        robot = JSONDecoder().decode(json.dumps(msg['ROBOT']))
        self.robot_list[robot.id] = (robot, datetime.now())
        event = Event(body="Robot "+robot.name+" está ejecutando el proceso " +
                      robot.process_running['name'], msgtype=MSG_TYPE.PROCESS_EXEC)
        self.db.dump([event])
        self.dbbi.dump_robot(robot, self.id, self.name, self.company)
        self.event_list.append(event) 
        log_orch.info("Robot " + str(robot.id) + " va a ejecutar" + robot.process_running['name'])

    async def handle_msgPendingProcess(self, msg):
        robot = JSONDecoder().decode(json.dumps(msg['ROBOT']))
        self.robot_list[robot.id] = (robot, datetime.now())

    async def handle_msgLog(self, msg):
        log = JSONDecoder().decode(json.dumps(msg['LOG']))
        log_orch.info("Robot " + str(log.id_robot) + " ha mandado el log (" + str(log.id)+ ") del proceso"+ log.process_name)
        self.__update_log(log)

    async def handle_msgUpdateInfo(self, msg):
        robot = JSONDecoder().decode(json.dumps(msg['ROBOT']))
        self.robot_list[robot.id] = (robot, datetime.now())
        self.db.dump([robot])
        self.dbbi.dump_robot(robot, self.id, self.name, self.company)
        self.dbbi.dump_robot_performance(
            robot, self.id, self.name, self.company)

    async def handle_msgCreateProcess(self, msg):
        process = msg['PROCESS']
        if not "exclude_robots" in process:  # temporal
            process['exclude_robots'] = []
        result = self.add_process(json.dumps(process))

        if result is None:
            event = Event(
                body="Robot ID"+msg["FROM"]+" crear proceso por AMQP, pero falla. ", msgtype=MSG_TYPE.ERROR)
            log_orch.error("Error creando proceso por AMQP")
            log_orch.error(process)
        else:
            event = Event(body="Robot ID"+msg["FROM"]+" crea proceso por AMQP. id schedule "+str(
                result), msgtype=MSG_TYPE.PROCESS_CREATE)
            log_orch.info("El robot " + msg['FROM']+" manda a crear el proceso id_schedule "+result)
        self.db.dump([event])

    async def handle_msgNotify(self, msg):
        pass

    async def __send_message(self, route, msg):
        await self.controller.send_message(route, msg)

    async def send_update_info(self, id_robot):
        await self.__send_message(messages.ROUTE_ROBOT+id_robot, json.dumps(messages.MSG_UPDATE_INFO))

    def send_remove_process(self, id_schedule, id_robot):
        asyncio.run(self.__send_message(messages.ROUTE_ROBOT+id_robot, json.dumps(
            dict(messages.MSG_REMOVE_PROCESS, **({"SCHEDULE": id_schedule})))))

    async def send_kill_process(self, id_schedule, id_robot):
        await self.__send_message(messages.ROUTE_ROBOT+id_robot, (json.dumps(messages.MSG_KILL_PROCESS, **({"SCHEDULE": id_schedule}))))

    async def send_pause_robot(self, id_robot):
        await self.__send_message(messages.ROUTE_ROBOT+id_robot, json.dumps(messages.MSG_PAUSE_ROBOT))

    async def send_resume_robot(self, id_robot):
        await self.__send_message(messages.ROUTE_ROBOT+id_robot, json.dumps(messages.MSG_RESUME_ROBOT))

    def send_restart_robot(self, id_robot):
        asyncio.run(self.__send_message(messages.ROUTE_ROBOT+id_robot, json.dumps(messages.MSG_RESTART_ROBOT)))

    async def __send_process_json(self, id_schedule, id_robot, process_json):
        process_json = json.loads(process_json)
        if(not id_robot):
            if not 'exclude_robots' in process_json:  # Temporal
                exclude_robots = []
            else:
                exclude_robots = process_json['exclude_robots']
            priority = process_json['priority']
            required = self.get_process_requirements_by_id(
                process_json['id_process'])
            robot = self.__choose_robot(exclude_robots, priority, required)
            if(not robot):  # No enviamos nada porque no tenemos a quien enviarselo
                return None, None
            id_robot = robot.id
        if not self.robot_list[id_robot][0].online:
            return None, None
        dt_string = datetime.now().strftime("%d-%m-%Y-%H%M%S")
        # Añadimos el id de ejecucion
        process_json['id_schedule'] = id_schedule
        process_json['log_file'] = dt_string + \
            self.get_process_class_name_by_id(
                process_json['id_process'])+".log"
        log = Log(id_schedule=id_schedule, id_process=process_json['id_process'], id_robot=id_robot,
                  log_file_path=process_json['log_file'], process_name=self.get_process_name_by_id(process_json['id_process']))
        self.db.dump([log])
        process_json['id_log'] = log.id
        process_json['id_robot'] = id_robot
        process_json['classname'] = self.get_process_class_name_by_id(
            process_json['id_process'])
        log_orch.info(process_json)
        await self.__send_message(messages.ROUTE_ROBOT+id_robot, json.dumps(dict(messages.MSG_REQUEST_PROCESS, **({"PROCESS": process_json}))))
        return id_robot, log.id

    def __update_log(self, log):
        log_memory = None
        try:
            log_memory = next(x for x in self.log_list if x.id == log.id)
            log_memory.data = log.data
            log_memory.end_time = log.end_time
            log_memory.state = log.state
            log_memory.finished = log.finished
            log_memory.completed = log.completed
        except:
            log_memory = log
            self.log_list.append(log_memory)
        log_memory.write_log(self.pathlog_store)
        self.db.dump([log_memory])
        if(log_memory.finished):
            log_orch.info("La ejecucion del proceso "+ log.process_name+" con id log "+str(log.id)+ " ha terminado")
            event = Event(body="Robot "+self.robot_list[log.id_robot][0].name+" ha terminado de ejecutar el proceso "+str(
                self.get_process_name_by_id(log.id_process)), msgtype=MSG_TYPE.PROCESS_EXEC)
            self.db.dump([event])
            self.lock.acquire()
            try:
                schedule_process = next(
                    x for x in self.schedule_list if x.id == log_memory.id_schedule)
                schedule_process.id_robot_temp = None
                self.db.dump([schedule_process])
                self.dbbi.dump_execution(
                    schedule_process, log_memory, self.id, self.name, self.company)
                if not schedule_process.get_forever():
                    self.schedule_list.remove(schedule_process)

            except Exception as e:
                log_orch.error("Ha llegado un log de un proceso ya terminado y eliminado.")
                log_orch.error(str(e))
                log_orch.error(traceback.format_exc())
            finally:
                self.lock.release()

    async def do_job_schedule(self, id_schedule, process_json, forever):
        self.lock.acquire()
        try:
            schedule_process = next(
                x for x in self.schedule_list if x.id == id_schedule)
            id_robot, id_log = await self.__send_process_json(schedule_process.id, schedule_process.id_robot, process_json)
            schedule_process.id_robot_temp = id_robot
            schedule_job = schedule.get_jobs(id_schedule)[0]
            if not id_robot and not id_log:
                event = Event(body="El proceso "+self.get_process_name_by_id(schedule_process.get_processid()) +
                              " no se va a ejecutar porque no hay ningun robot capaz de hacerlo", msgtype=MSG_TYPE.PROCESS_ERROR)
                self.db.dump([event, schedule_process])
                return

            if not forever:
                schedule.cancel_job(schedule_job)
            self.db.dump([schedule_process])
        except Exception as e:
            log_orch.error(
                "Schedule error en el lanzamiento, problema en base de datos o en un robot?")
            log_orch.error(str(e))
        finally:
            self.lock.release()

    def __choose_robot(self, exclude_robots, priority_process, required):
        candidate = None
        candidates = []
        cand_equal = []
        for (key, value) in self.robot_list.items():
            robot = value[0]
            if robot.online and not (set(required) - set(robot.features)) and not robot.id in exclude_robots:
                if robot.state == "Iddle" and len(robot.process_list) == 0:
                    # Cogemos el primero que este iddle y no tenga nada pendiente
                    candidates.append(robot)
                else:
                    if len(robot.process_list) > 0:
                        if int(robot.process_list[0]['priority']) <= int(priority_process):
                            candidates.append(robot)
                    else:
                        candidates.append(robot)
        for i in candidates:
            if candidate is None:
                candidate = i
                cand_equal.append(i)
            elif len(candidate.process_list) > len(i.process_list):
                candidate = i
                cand_equal.clear()
                cand_equal.append(i)
            elif len(candidate.process_list) == len(i.process_list):
                cand_equal.append(i)
        if len(cand_equal) > 0:
            return choice(cand_equal)
        return None

    def get_capable_robots(self, process):
        robots_capable = []
        required = set(process['required'])
        for (key, value) in self.robot_list.items():
            if (value[0].online):
                installed = set(value[0].features)
                missing = required - installed
                if not missing:
                    robots_capable.append(key)
        return robots_capable

    def __is_capable(self, required, robot):
        installed = set(robot.features)
        required = set(required)
        missing = required - installed
        if not missing:
            return True
        return False

    def __is_any_capable(self, required):
        required = set(required)
        for (key, value) in self.robot_list.items():
            if (value[0].online):
                installed = set(value[0].features)
                missing = required - installed
                if not missing:
                    return True
        return False

    # def is_robot_schedule(self, id_robot, id_schedule):
    #     robot = self.robot_list[id_robot][0]
    #     if robot.process_running:
    #         if robot.process_running['log'].id_schedule == id_schedule:
    #             return True
    #     else:
    #         for p in robot.process_list:
    #             if p['log'].id_schedule == id_schedule:
    #                 return True
    #     return False

    def get_process_by_id(self, id_process):
        if str(id_process) in self.process:
            return self.process[str(id_process)]
        return None

    def get_process_class_name_by_id(self, id_process):
        if str(id_process) in self.process:
            return self.process[str(id_process)]['class']
        return None

    def get_process_requirements_by_id(self, id_process):
        if str(id_process) in self.process:
            return self.process[str(id_process)]['requirements']
        return None

    def get_process_name_by_id(self, id_process):
        if str(id_process) in self.process:
            return self.process[str(id_process)]['name']
        return None

    def get_process_description_by_id(self, id_process):
        if str(id_process) in self.process:
            return self.process[str(id_process)]['description']
        return None
    
    def get_process_visible_by_id(self, id_process):
        if str(id_process) in self.process:
            return self.process[str(id_process)]['visible']
        return None
    
    
    def get_process_setting_by_id(self, id_process):
        if str(id_process) in self.process:
            return self.process[str(id_process)]['setting']
        return None

    def get_log(self, id_log=None):
        import rpa_orchestrator.lib.messagesjson.logjson as logjson
        return logjson.get_log(id_log)

    def get_schedule(self, id_schedule):
        import rpa_orchestrator.lib.messagesjson.schedulejson as schjson
        return schjson.get_schedule(id_schedule)

    def get_robot_problems(self, id_robot=False):
        import rpa_orchestrator.lib.messagesjson.robotjson as robotjson
        return robotjson.get_robot_problems(id_robot)

    def get_robot(self, id_robot):
        import rpa_orchestrator.lib.messagesjson.robotjson as robotjson
        return robotjson.get_robot(id_robot)

    def get_process(self, id_process=None, visible = None):
        import rpa_orchestrator.lib.messagesjson.processjson as process
        return process.get_process(id_process, visible)

    def get_process_form(self, id_process) -> json:
        try:
            with open(DIRECTORY_PROCESS_FORM+self.get_process_class_name_by_id(id_process)+".json", "r") as json_file:
                data = json.load(json_file)
                return data
        except:
            log_orch.error("No existe el formulario del proceso solicitado " +
                  str(id_process)+" se envia vacio")
            return []

    def get_events(self, filters=None):
        events_json = self.db.read_events(filters)
        return JSONEncoder().encode([x for x in events_json])

    def get_all_schedules(self, filters=None):
        import rpa_orchestrator.lib.messagesjson.schedulejson as schjson
        return schjson.get_all_schedules(filters)

    def get_all_process(self) -> json:
        return self.process

    def get_all_robots(self):
        import rpa_orchestrator.lib.messagesjson.robotjson as robotjson
        return robotjson.get_all_robots()

    def get_all_logs(self):
        import rpa_orchestrator.lib.messagesjson.logjson as logjson
        return logjson.get_log()

    def get_all_logs_by_idschedule(self, id_schedule):
        import rpa_orchestrator.lib.messagesjson.logjson as logjson
        return logjson.get_all_logs_by_idschedule(id_schedule)

    def get_all_logs_by_idrobot(self, id_robot):
        import rpa_orchestrator.lib.messagesjson.logjson as logjson
        return logjson.get_all_logs_by_idrobot(id_robot)

    def get_file(self, id_file=None) -> File:
        file = self.db.read_files(id_file)
        return file
    
    def get_global_settings(self) -> GlobalSettings:
        global_settings = self.db.read_global_settings()
        return global_settings

    def get_global_settings_by_id(self,id) -> GlobalSettings:
        global_settings = self.db.get_global_settings_by_id(id)
        return global_settings

    def update_global_settings(self,id,new_parameters):
        return self.db.update_global_settings(id,new_parameters)

    def get_amqp_settings_by_id(self,id) -> AMQPSettings:
        amqp_settings = self.db.get_amqp_settings_by_id(id)
        return amqp_settings

    def update_amqp_settings(self,id,new_parameters):
        return self.db.update_amqp_settings(id,new_parameters)
    
    def get_dbprocess_settings_by_id(self,id) -> DBProcessSettings:
        dbprocess_settings = self.db.get_dbprocess_settings_by_id(id)
        return dbprocess_settings

    def update_dbprocess_settings(self,id,new_parameters):
        return self.db.update_dbprocess_settings(id,new_parameters)

    def get_dbbi_settings_by_id(self,id) -> DBBISettings:
        dbbi_settings = self.db.get_dbbi_settings_by_id(id)
        return dbbi_settings

    def update_dbbi_settings(self,id,new_parameters):
        return self.db.update_dbbi_settings(id,new_parameters)

    def get_orchestrator_settings_by_id(self,id) -> OrchestratorSettings:
        orchestrator_settings = self.db.get_orchestrator_settings_by_id(id)
        return orchestrator_settings

    def update_orchestrator_settings(self,id,new_parameters):
        return self.db.update_orchestrator_settings(id,new_parameters)

    def get_process_settings_by_id(self,id) -> ProcessSettings:
        process_settings = self.db.get_process_settings_by_id(id)
        return process_settings

    def update_process_settings(self,id,new_parameters):
        return self.db.update_process_settings(id,new_parameters)

    def is_token_valid(self, id_robot, token):
        if id_robot in self.robot_list and self.robot_list[id_robot][0].token == token:
            return True
        return False

    def get_username(self, username):
        username = self.db.get_username(username)
        return username

    def user_login(self, username, password):
        user = self.db.user_login(username, hashlib.md5(password.encode()).hexdigest())
        if not user:
            return None
        return user

    def update_username_token(self, username, access_token):
        return self.db.update_username_token(username, access_token)

    def get_main_stats(self):
        import rpa_orchestrator.lib.messagesjson.statsjson as stats
        return stats.get_main_stats()

    def set_schedule(self, id_schedule, process_json) -> bool:
        try:
            process_dict = json.loads(process_json)
            schedule_process = next(
                x for x in self.schedule_list if x.id == int(id_schedule))
            process_dict['process']['id_process'] = schedule_process.get_processid()
            process_dict['process']['parameters'] = json.loads(
                schedule_process.schedule_json)['process']['parameters']
            self.remove_schedule(id_schedule)
            schedule_process = ScheduleProcess(id=schedule_process.id, id_robot=process_dict['process']['id_robot'], schedule_json=json.dumps(
                process_dict), function=self.do_job_schedule)
            
            schedule_process.time_to_schedule()
            self.db.dump([schedule_process])
            self.schedule_list.append(schedule_process)
            return True
        except Exception as e:
            log_orch.error("Error intentando modificar el proceso")
            log_orch.error(str(e))
            return False

    def set_event_read(self, id_event):
        event = self.db.read_events({'id': id_event})
        if len(event) == 0:
            return False
        event[0].read = True
        self.db.dump(event)
        return True
        
    def add_file(self, file):
        self.db.dump([file])


    def add_process(self, process_json):
        self.lock.acquire()
        try:
            json_edit = json.loads(process_json)
            id_robot = json_edit['process']['id_robot']
            # Comprobamos si existe el proceso
            if not self.get_process_class_name_by_id(json_edit['process']['id_process']):
                log_orch.warning("No existe el proceso")
                return None
            if id_robot:
                if not id_robot in self.robot_list:
                    log_orch.warning("No existe ese robot")
                    return None
                robot = self.robot_list[id_robot][0]
                if not robot or not robot.online or not self.__is_capable(self.get_process_requirements_by_id(json_edit['process']['id_process']), robot):
                    log_orch.warning(
                        "No se puede ejecutar el proceso porque no existe el robot, no esta online o no es capaz de hacer ese proceso")
                    return None
            if(not id_robot and self.__is_any_capable(self.get_process_requirements_by_id(json_edit['process']['id_process'])) == 0):
                log_orch.warning("No hay robot para ejecutar")
                return None
            schedule_process = ScheduleProcess(
                id_robot=id_robot, schedule_json=process_json, function=self.do_job_schedule)
            self.db.dump([schedule_process])
            self.schedule_list.append(schedule_process)
            id_schedule = schedule_process.time_to_schedule()
            self.db.dump([schedule_process])
            return id_schedule
        except Exception as e:
            log_orch.error(msg="Error al añadir el proceso " + str(e))
        finally:
            self.lock.release()

    def remove_schedule(self, id_schedule):
        self.lock.acquire()
        try:
            try:
                schedule_process = next(
                    x for x in self.schedule_list if x.id == int(id_schedule))
                schedule_process.set_forever(False)
            except:
                log_orch.error(str(e))
                return False

            schedule_job = schedule.get_jobs(int(id_schedule))[0]
            schedule.cancel_job(schedule_job)
            id_robot = schedule_process.id_robot
            id_robots = []
            if not id_robot:
                for (key, value) in self.robot_list.items():
                    for i in value[0].process_list:
                        if i['log'].id_schedule == int(id_schedule):
                            id_robots.append(value[0].id)
            else:
                id_robots.append(id_robot)

            for i in id_robots:
                self.send_remove_process(id_schedule, i)

            log = self.db.read_logs_byidschedule(schedule_process.id)
            if len(log) > 0:
                log = log[0]
                if log.finished:
                    self.schedule_list.remove(schedule_process)
            else:
                self.schedule_list.remove(schedule_process)

            self.db.dump([schedule_process])
            self.dbbi.dump_execution(schedule_process, None,
                                     self.id, self.name, self.company)
            return True
        except Exception as e:
            log_orch.error(str(e))
        finally:
            self.lock.release()

    def remove_process_robot(self, id_robot, id_schedule):
        if id_robot in self.robot_list:
            robot = self.robot_list[id_robot][0]
            if robot.online:
                for p in robot.process_list:
                    if int(p['log'].id_schedule) == id_schedule:
                        self.send_remove_process(id_schedule, robot.id)
                        return True
        return False

    def run(self):
        asyncio.run(self.__send_message(messages.ROUTE_ROBOT +
                    "general", json.dumps(messages.MSG_START_ORCH)))
        log_orch.info("Se inicia el orquestador. " +  datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        while True:
            for (key, value) in self.robot_list.items():
                if((datetime.now() - value[1]).seconds > TIME_KEEP_ALIVE and value[0].online):
                    value[0].online = False
                    event = Event(
                        body="Robot "+value[0].name+" se ha desconectado. ", msgtype=MSG_TYPE.CONNECTION)
                    self.db.dump([event, value[0]])
                    self.dbbi.dump_robot(
                        value[0], self.id, self.name, self.company)
                    self.event_list.append(event)

            asyncio.run(schedule.run_pending())
