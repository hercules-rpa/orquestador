from datetime import datetime
from threading import Thread
from controller.ControllerAMQP import ControllerAMQP as controller
from rpa_robot.ExecProcess import ExecProcess
from model.interfaces.ListenerMsg import ListenerMsg
from model.interfaces.ListenerLog import ListenerLog
from model.interfaces.ListenerProcess import ListenerProcess
from customjson.JSONEncoder import JSONEncoder
from getmac import get_mac_address as gma
from rpa_robot.ControllerRobot import ControllerRobot
import model.messages as messages
import importlib
import asyncio
import sys
import json
import pkg_resources
import platform
import requests
import psutil
import time
import uuid
from uuid import getnode as get_mac
import traceback

TIME_WAIT_INIT = 60
TIME_KEEP_ALIVE = 60
UUID = uuid.uuid1()

class Robot(ListenerMsg, ListenerLog, ListenerProcess):

    def __init__(self, id, name, address, registrations, ip_api='localhost', port_api=5000, frontend = None, online=False, connected=datetime.now().timestamp(), features=[pkg.key for pkg in pkg_resources.working_set], state="Iddle", process_running=None, process_list=[]):
        self.id = str(id)
        self.name = str(name)
        self.address = str(address)
        self.registrations = str(registrations)
        self.ip_api = str(ip_api)
        self.port_api = str(port_api)
        self.frontend = frontend
        self.ip_address = None
        # "".join(c + ":" if i % 2 else c for i,c in enumerate(hex(get_mac())[2:].zfill(12)))[:-1]
        self.mac = gma()
        self.token = str(UUID)
        self.python_version = sys.version
        self.online = online
        self.connected = connected
        self.features = features
        self.os = platform.system()
        self.state = state
        self.performance = [psutil.cpu_percent(), psutil.virtual_memory(
        ).percent, psutil.disk_usage('/').percent]  # CPU, RAM, DISK
        self.process_running = process_running
        # Procesos pendientes, cuando se vaya a ejecutar uno lo quitamos de esta lista y lo pasamos a process_running
        self.process_list = process_list
        self.process_pause = []
        
        ControllerRobot(self)

    def __instance_process(self, process_dict):
        # hacer algo en este caso para hacerlo robusto, enviar error proceso al orquestador. COMPROBAR SI EL ORQUESTADOR CONOCE ESE PROCESO, Y SI SE VERIFICA PEDIR QUE ACTUALICE EL REPOSITORIO AL ROBOT
        try:
            module = importlib.import_module(
                messages.ROUTE_MODULE_PROCESS+process_dict['classname'])
            class_ = getattr(module, process_dict['classname'])
            instance = class_(process_dict['id_schedule'], process_dict['id_log'], process_dict['id_robot'],
                            process_dict['priority'], process_dict['log_file'], process_dict['parameters'],
                            self.ip_api, self.port_api)
            return instance
        except Exception as e:
            print("El proceso no ha podido ser instanciado")
            print(traceback.format_exc())
            print(str(e))
            return None

    def __execute_process(self, process):
        self.state = "RUNNING "+process.name
        self.process_running = process
        print("El robot va a ejecutar el proceso: ", process.name)
        asyncio.run((self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(
            messages.MSG_EXEC_PROCESS, **({"ROBOT": json.loads(JSONEncoder().encode(self))}))))))
        process.add_log_listener(self)

        # p = Thread(target=process.execute)
        # p.start()
        execProcess = ExecProcess(process=process, listener=self)
        p = Thread(target=execProcess.exec)
        p.start()

    def __resume_process(self, process):
        self.state = "RUNNING "+process.name
        self.process_running = process
        #print("El robot va a reanudar el proceso: ",process.name)
        asyncio.run((self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(
            messages.MSG_RESUME_PROCESS, **({"ROBOT": json.loads(JSONEncoder().encode(self))}))))))
        process.add_log_listener(self)
        p = Thread(target=process.resume)
        p.start()

    def __exec_process_pending(self):
        if(self.process_running is None):  # LOGICA DE IDDLE
            if(len(self.process_pause) > 0):
                (self.__resume_process(self.process_pause.pop(0)))
            elif(len(self.process_list) > 0):
                (self.__execute_process(self.process_list.pop(0)))
        # else:
            # LOGICA DEL PAUSE
            # CREAR CERROJO EN LA CONSULTA DE PROCESS_RUNNING, se puede dar el caso de que se ponga a None cuando se hace el if. (ha pasado)
            # if(len(self.process_list) > 0):
            #    process = self.process_list[0]
            #    if(process.priority < self.process_running.priority):
            #        self.process_running.pause()
            #        self.process_pause.append(self.process_running)
            #        (self.__execute_process(self.process_list.pop(0)))

    def __pause(self):
        self.state = "PAUSE"
        self.process_running.pause()
        self.process_pause.append(self.process_running)
        self.process_running = None
        self.state = "Iddle"

    def __remove_process(self, id_schedule):
        try:
            process_remove = [x for x in self.process_list if int(
                x.log.id_schedule) == int(id_schedule)]
            if len(process_remove) == 0:
                return False

            for i in process_remove:
                self.process_list.remove(i)
        except:
            return False
        return process_remove[0].id

    def __kill_process(self, id_log):
        self.process_running.kill()
        self.process_running = None
        self.state = "Iddle"

    def __sort_by_priority(self, process):
        return process.priority

    async def __send_message(self, route, msg):
        await controller().send_message(route, msg)

    async def add_subscription(self, route):
        await controller().add_subscription(route)

    def notify_log(self, log):
        if(log.finished):
            self.state = "Iddle"
            self.process_running = None
        asyncio.run((self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(
            dict(messages.MSG_LOG, **({"LOG": json.loads(JSONEncoder().encode(log))}))))))
        asyncio.run(self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(
            messages.MSG_UPDATE_INFO, **({"ROBOT": json.loads(JSONEncoder().encode(self))})))))

    def notify_create_process(self, process):
        msg = messages.MSG_CREATE_PROCESS
        msg['PROCESS'] = process
        msg['FROM'] = self.id
        asyncio.run(self.__send_message(
            messages.ROUTE_ORCHESTRATOR, json.dumps(dict(msg))))

    async def notify_msg(self, msg):
        print("llega: ", msg)
        await self.handle_msg(msg)

    async def handle_msg(self, msg):
        msg = json.loads(msg)
        type_msg = msg['TYPE_MSG']
        if(type_msg == messages.INIT):
            await self.handle_msgInit(msg)
        elif(type_msg == messages.KILL_PROCESS):
            await self.handle_msgKillProcess(msg)
        elif(type_msg == messages.START_ORCH):
            await self.handle_msgStartOrch(msg)
        elif(type_msg == messages.PAUSE_ROBOT):
            await self.handle_msgPause(msg)
        elif(type_msg == messages.REMOVE_PROCESS):
            await self.handle_msgRemoveProcess(msg)
        elif(type_msg == messages.REQUEST_EXEC_PROCESS):
            await self.handle_msgReqExecProcess(msg)
        elif(type_msg == messages.RESUME_PROCESS):
            await self.handle_msgResumeRobot(msg)
        elif(type_msg == messages.UPDATE_INFO):
            await self.handle_msgUpdateInfo(msg)

    async def handle_msgInit(self, msg):
        print("Conexion establecida")
        global time_keep
        time_keep = datetime.now()
        self.online = True

    async def handle_msgStartOrch(self, mgs):
        print("Orquestador conectado")
        await self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(messages.MSG_INIT_ROBOT, **({"ROBOT": json.loads(JSONEncoder().encode(self))}))))
        await self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(messages.MSG_KEEP_ALIVE, **({"ROBOT": json.loads(JSONEncoder().encode(self))}))))

    async def handle_msgReqExecProcess(self, msg):
        process = msg['PROCESS']
        process_instance = self.__instance_process(process)
        if process_instance:
            print("El robot almacena el proceso: ", process_instance.name,
                ' en la cola, tiene prioridad: ', process_instance.priority)
            self.process_list.append(process_instance)
            self.process_list.sort(key=self.__sort_by_priority)
            await self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(messages.MSG_PENDING_PROCESS, **({"ROBOT": json.loads(JSONEncoder().encode(self))}))))
        else:
            print("El robot elimina el proceso")
            await self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(messages.MSG_UPDATE_INFO, **({"ROBOT": json.loads(JSONEncoder().encode(self))}))))

    async def handle_msgUpdateInfo(self, msg):
        await self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(messages.MSG_UPDATE_INFO, **({"ROBOT": json.loads(JSONEncoder().encode(self))}))))

    async def handle_msgPause(self, msg):
        self.pause()

    async def handle_msgResumeRobot(self, msg):
        self.resume()

    async def handle_msgKillProcess(self, msg):
        id_schedule = msg['SCHEDULE']
        self.__remove_process(id_schedule)
        self.__kill_process(id_schedule)
        await self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(messages.MSG_UPDATE_INFO, **({"ROBOT": json.loads(JSONEncoder().encode(self))}))))

    async def handle_msgRemoveProcess(self, msg):
        id_schedule = msg['SCHEDULE']
        process = self.__remove_process(id_schedule)
        if(process):
            print("Proceso eliminado")
            await self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(messages.MSG_UPDATE_INFO, **({"ROBOT": json.loads(JSONEncoder().encode(self))}))))
        else:
            print("Se ha intentado eliminar un proceso que no existe")
            await self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(messages.MSG_UPDATE_INFO, **({"ROBOT": json.loads(JSONEncoder().encode(self))}))))

    def run(self):
        play = True
        global time_keep
        time_orch = datetime.now()
        time_seconds = 30
        print("STARTING CONNECTION")
        if(self.ip_address == None):
            try:
                self.ip_address = requests.get(
                    'http://'+self.ip_api+':'+self.port_api+'/api/orchestrator/getip').json()['ip']
            except:
                print("Connection exception")
        asyncio.run(self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(
            messages.MSG_INIT_ROBOT, **({"ROBOT": json.loads(JSONEncoder().encode(self))})))))
        while (play):
            # Actualizamos cpu, ram, disk y features en tiempo real. Pensar si meterlo en otro sitio que se ejecute cada minuto o algo asi.
            self.performance = [psutil.cpu_percent(), psutil.virtual_memory(
            ).percent, psutil.disk_usage('/').percent]  # CPU, RAM, DISK
            self.features = [pkg.key for pkg in pkg_resources.working_set]
            if (not self.online and time_seconds >= TIME_WAIT_INIT):
                if(self.ip_address == None):
                    try:
                        self.ip_address = requests.get(
                            'http://'+self.ip_api+':'+self.port_api+'/api/orchestrator/getip').json()['ip']
                    except:
                        print("Connection exception")
                print("sending init")

                asyncio.run(self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(
                    messages.MSG_INIT_ROBOT, **({"ROBOT": json.loads(JSONEncoder().encode(self))})))))
                time_orch = datetime.now()
                time_keep = datetime.now()
            elif(self.online):
                if ((datetime.now() - time_keep).seconds > TIME_KEEP_ALIVE):
                    print("Mandamos Keep Alive ", datetime.now())
                    asyncio.run(self.__send_message(messages.ROUTE_ORCHESTRATOR, json.dumps(dict(
                        messages.MSG_KEEP_ALIVE, **({"ROBOT": json.loads(JSONEncoder().encode(self))})))))
                    time_keep = datetime.now()

                if((len(self.process_list) > 0 or len(self.process_pause) > 0) and self.state != "PAUSE"):
                    self.__exec_process_pending()

            time_seconds = (datetime.now() - time_orch).seconds
            time.sleep(1)
