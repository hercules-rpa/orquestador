from abc import ABC, abstractmethod
import os
import time
from datetime import datetime, timedelta
from urllib import response
from model.Log import Log
from enum import Enum
import json
import Utils
import asyncio
import requests


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
    EXTRACT_CONVOCATORIA = 9
    EXTRACT_BASESREGULADORAS = 10
    EXTRACT_XML = 11
    EXTRACT_NEWS = 12
    GENERATETRANSFERREPORT = 13
    PDF_TO_TABLE = 14
    EXTRACT_INFO_PDF = 15
    EXTRACT_CONCESION = 16
    EXTRACT_ARTICLES = 17
    SEXENIOS = 18
    EXTRACT_PROJECTS_AND_CONTRACTS = 19
    EXTRACT_ANNOUNCEMENTS = 20
    EXTRACT_INVENCIONES = 21
    ACREDITACIONES = 22
    EXTRACT_THESIS = 23
    EXTRACT_OTC = 24
    RECOMMENDATION = 25
    COLLABORATIVE_FILTERING = 26
    BASED_CONTENT = 27
    GRAFO_COLABORACION = 28
    MOTOR_HIBRIDO = 29
    RECORDATORIO_PERFIL = 30
    TRANVIA_DAILY = 99


class ProcessClassName(Enum):
    HOLA_MUNDO = "ProcessHolaMundo"
    COMPOSE_TEST = "ProcessComposeTest"
    SEND_MAIL = "ProcessSendMail"
    SELENIUM_TSLA = "ProcessSeleniumTSLA"
    EXTRACT_TABLES = "ProcessExtractTables"
    DOWNLOAD_FILES = "ProcessDownload"
    EXTRACT_OFFER = "ProcessExtractOffer"
    EXTRACT_RESULT = "ProcessExtractResult"
    EXTRACT_CONVOCATORIA = "ProcessExtractConvocatoria"
    EXTRACT_BASESREGULADORAS = "ProcessExtractBasesReguladoras"
    EXTRACT_XML = "ProcessExtractXml"
    EXTRACT_NEWS = "ProcessExtractNews"
    TRANVIA_DAILY = "ProcessTranviaDaily"
    EXTRACT_CONCESION = "ProcessExtractConcesion"
    GENERATETRANSFERREPORT = "ProcessGenerateTransferReport"
    PDF_TO_TABLE = "ProcessPdfToTable"
    EXTRACT_INFO_PDF = "ProcessExtractInfoPDF"
    EXTRACT_ARTICLES = "ProcessExtractArticles"
    SEXENIOS = "ProcessSexenios"
    ACREDITACIONES = "ProcessAcreditaciones"
    EXTRACT_PROJECTS_AND_CONTRACTS = "ProcessExtractProjectsAndContracts"
    EXTRACT_ANNOUNCEMENTS = "ProcessExtractAnnouncements"
    EXTRACT_INVENCIONES = "ProcessExtractInvenciones"
    EXTRACT_THESIS = "ProcessExtractThesis"
    RECOMMENDATION = "ProcessSistemaRecomendacion"


class ProcessCommand(ABC):
    def __init__(self, id, name, requirements, description, id_schedule, id_log, id_robot, priority, log_file_path, parameters):
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
        self.result = None

    def add_log_listener(self, listener):
        self.log.add_log_listener(listener)

    def add_data_listener(self, listener):
        self.log.add_data_listener(listener)

    def update_log(self, data, timestamp=False):
        if(timestamp is True):
            self.log.update_log("["+Utils.time_to_str(time.time())+"]" +
                                " Process"+str(self.id)+"@robot:"+self.id_robot+" "+data+"\n")
        else:
            self.log.update_log(data)

    def notify_log_data(self, log, new_data):
        self.update_log(new_data.rstrip()+" (Child of " +
                        self.name+" id_process = "+str(self.id)+")\n", False)

    def format_date(self, str_date, format_start, format_end) -> str:
        result: str = ''
        try:
            result = datetime.strptime(
                str_date, format_start).strftime(format_end)
        except:
            self.notificar_actualizacion('ERROR: conversión errónea: format_date: ' + str_date +
                                         ' formato_entrada: ' + format_start + ' formato salida: ' + format_end)

        return result

    def notificar_actualizacion(self, msg):
        self.update_log(msg, True)

    def format_date_process(self, fecha: datetime):
        result: str
        if fecha.day < 10:
            result = '0' + str(fecha.day) + '/'
        else:
            result = str(fecha.day) + '/'
        if fecha.month < 10:
            result += '0' + str(fecha.month) + '/'
        else:
            result += str(fecha.month) + '/'
        result += str(fecha.year)

        return result

    def update_elements(self, elements: list, url: str, notificada: bool):
        if elements:
            payload = json.dumps(
                {
                    "notificada": notificada
                })

            headers = {
                'Content-Type': 'application/json'
            }

            if not url.endswith('/'):
                url = url + '/'

            for element in elements:
                requests.patch(url + str(element.id),
                               headers=headers, data=payload)

    def calculate_dates(self):
        """
        Método que calcula el rango de fechas en base a los parámetros de entrada del proceso.
        """
        start_date: datetime = None
        end_date: datetime = None
        try:
            self.notificar_actualizacion(
                'Obteniendo el rango de fechas en base a los parámetros de entrada del proceso.')
            if 'period' in self.parameters:
                period = self.parameters['period']
                end_date = datetime.now()
                start_date = end_date - timedelta(days=period)
            else:
                if 'start_date' in self.parameters:
                    date1 = self.parameters['start_date']
                    start_date = datetime.strptime(date1, "%Y-%m-%d")
                else:
                    start_date = datetime.now()

                if 'end_date' in self.parameters:
                    date1 = self.parameters['end_date']
                    end_date = datetime.strptime(date1, "%Y-%m-%d")
                else:
                    end_date = datetime.now()

            self.notificar_actualizacion(
                'Rango de fechas obtenido correctamente.')

        except Exception as e:
            print(e)
            self.notificar_actualizacion(
                'ERROR en el cálculo del rango de fechas.')
            self.log.state = "ERROR"

        return (start_date, end_date)

    def ping(self, host):
        """
        response = os.system("ping -c 1 " + host)    
        if response == 0:
            return True
        else:
            return True
        """
        return True

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
