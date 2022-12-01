from abc import ABC, abstractmethod
import time
from datetime import datetime, timedelta
from model.Log import Log
from enum import Enum
import json
import Utils
import requests

from model.RPA import RPA
from rpa_robot.ControllerRobot import ControllerRobot


class Pstatus(Enum):
    INITIALIZED = 1
    RUNNING = 2
    PAUSED = 3
    KILLED = 4
    FINISHED = 5


class ProcessID(Enum):
    HOLA_MUNDO = 1
    COMPOSE_TEST = 2
    SEND_MAIL = 3
    SELENIUM_TSLA = 4
    EXTRACT_TABLES = 5
    DOWNLOAD_FILES = 6
    EXTRACT_OFFER = 7
    EXTRACT_RESULT = 8
    EXTRACT_CALLS = 9
    EXTRACT_REGULATORY_BASES = 10
    EXTRACT_XML = 11
    EXTRACT_NEWS_TRANSFER_REPORT = 12
    GENERATE_TRANSFER_REPORT = 13
    PDF_TO_TABLE = 14
    EXTRACT_INFO_PDF = 15
    EXTRACT_AWARD = 16
    EXTRACT_ARTICLES_TRANSFER_REPORT = 17
    GENERATE_SEXENIO = 18
    EXTRACT_PROJECTS_AND_CONTRACTS_TRANSFER_REPORT = 19
    EXTRACT_CALLS_TRANSFER_REPORT = 20
    EXTRACT_INVENTIONS_TRANSFER_REPORT = 21
    GENERATE_ACCREDITATION = 22
    EXTRACT_THESIS_TRANSFER_REPORT = 23
    EXTRACT_OTC_TRANSFER_REPORT = 24
    RECOMMENDATION = 25
    COLLABORATIVE_FILTERING = 27
    BASED_CONTENT = 28
    COLLABORATIVE_GRAPH = 29
    HYBRID_ENGINE = 30
    REMINDER_PROFILE = 26
    EXECUTE_COMMAND = 97
    RESTART_ROBOT = 98


class ProcessCommand(ABC):
    def __init__(self, id, name, requirements, description, id_schedule, id_log, id_robot, priority, log_file_path, parameters, 
    ip_api=None, port_api=None):
        self.name = name
        self.requirements = requirements
        self.description = description
        self.id = id
        self.id_robot = id_robot
        self.log = Log(id_log, id_schedule, self.id,
                       id_robot, log_file_path, self.name)
        self.state = Pstatus.INITIALIZED
        self.priority = priority
        self.parameters = parameters
        self.ip_api = ip_api
        self.port_api = port_api      
        self.result = None
        self.cr = ControllerRobot() 
        self.rpa:RPA = None
        if self.cr.robot:
            self.rpa:RPA = RPA(self.cr.robot.token)

    def add_log_listener(self, listener):
        self.log.add_log_listener(listener)

    def add_data_listener(self, listener):
        self.log.add_data_listener(listener)

    def update_log(self, data, timestamp=False):
        if  not self.log.finished:
            if (timestamp is True):
                self.log.update_log("["+Utils.time_to_str(time.time())+"]" +
                                    " Process"+str(self.id)+"@robot:"+self.id_robot+" "+data+"\n")
            else:
                self.log.update_log(data)
        else:
            print("Se intenta escribir en el log cuando ya ha sido cerrado (end_log)")

    def notify_log_data(self, log, new_data):
        self.update_log(new_data.rstrip()+" (Child of " +
                        self.name+" id_process = "+str(self.id)+")\n", False)

    def format_date(self, str_date, format_start, format_end) -> str:
        """
        Método encargado de formatear una fecha
        :param str_date fecha en formato str
        :param format_start formato de la fecha original
        :param format_end formado de la fecha que se desea
        :return str fecha formateada
        """
        result: str = ''
        try:
            result = datetime.strptime(
                str_date, format_start).strftime(format_end)
        except:
            self.notify_update('ERROR: conversión errónea: format_date: ' + str_date +
                               ' formato_entrada: ' + format_start + ' formato salida: ' + format_end)

        return result

    def notify_update(self, msg):
        """
        Método encargado de notificar un mensaje por pantalla e insertarlo en el log
        :param msg mensaje a insertar
        """
        self.update_log(msg, True)
        print(msg)

    def update_elements(self, elements: list, url: str, notificada: bool):
        """
        Método que realiza la actualización de un elemento en base de datos
        :param elements lista de elementos
        :param url dirección url para realizar la actualización
        :param notificada True si el elemento ha sido notificado y False si no.
        """
        if elements:
            payload = json.dumps(
                {
                    "notificada": notificada
                })

            if url:
                if not url.endswith('/'):
                    url = url + '/'

                for element in elements:
                    if element.id and element.id != 0:
                        self.rpa.patch(url + str(element.id),
                                    data=payload)
            else:
                print('ERROR no ha sido posible persistir la colección de elementos')

    def calculate_dates(self):
        """
        Método que calcula el rango de fechas en base a los parámetros de entrada del proceso.
        :return tuple tupla donde el primer elemento es la fecha de inicio y el segundo la fecha de fin
        """
        start_date: datetime = None
        end_date: datetime = None
        try:
            self.notify_update(
                'Obteniendo el rango de fechas en base a los parámetros de entrada del proceso.')
            if 'period' in self.parameters:
                period = self.parameters['period']
                end_date = datetime.now()
                start_date = end_date - timedelta(days=period)
            else:
                if 'start_date' in self.parameters:
                    date1 = self.parameters['start_date']
                    print(date1)
                    start_date = datetime.strptime(date1, "%Y-%m-%d")
                else:
                    start_date = datetime.now()

                if 'end_date' in self.parameters:
                    date1 = self.parameters['end_date']
                    print(date1)
                    end_date = datetime.strptime(date1, "%Y-%m-%d")
                else:
                    end_date = datetime.now()

            self.notify_update(
                'Rango de fechas obtenido correctamente.')

        except Exception as e:
            print(e)
            self.notify_update(
                'ERROR en el cálculo del rango de fechas.')
            self.log.state = "ERROR"

        return (start_date, end_date)
        
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def kill(self):
        pass
