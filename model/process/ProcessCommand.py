from abc import ABC, abstractmethod
import time
from datetime import datetime
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
    SEND_MAIL = 3        
    DOWNLOAD_FILES = 6
    EXTRACT_CONVOCATORIA = 9
    EXTRACT_BASESREGULADORAS = 10
    EXTRACT_XML = 11
    EXTRACT_NEWS = 12
    GENERATETRANSFERREPORT = 13
    PDF_TO_TABLE = 14
    EXTRACT_INFO_PDF = 15

class ProcessClassName(Enum):
    HOLA_MUNDO               = "ProcessHolaMundo"
    SEND_MAIL                = "ProcessSendMail"
    SELENIUM_TSLA            = "ProcessSeleniumTSLA"
    DOWNLOAD_FILES           = "ProcessDownload"
    EXTRACT_CONVOCATORIA     = "ProcessExtractConvocatoria"
    EXTRACT_BASESREGULADORAS = "ProcessExtractBasesReguladoras"
    EXTRACT_XML              = "ProcessExtractXml"
    EXTRACT_NEWS             = "ProcessExtractNews"
    GENERATETRANSFERREPORT   = "ProcessGenerateTransferReport"
    PDF_TO_TABLE             = "ProcessPdfToTable"
    EXTRACT_INFO_PDF         = "ProcessExtractInfoPDF"

class ProcessCommand(ABC):
    def __init__(self, id,name, requirements, description, id_schedule, id_log, id_robot, priority, log_file_path, parameters):
        self.name           = name
        self.requirements   = requirements
        self.description    = description
        self.id             = id
        self.id_robot       = id_robot
        self.log            = Log(id_log,id_schedule,self.id,id_robot,log_file_path,self.name)
        self.state          = Pstatus.INITIALIZED
        self.priority       = priority
        self.parameters     = parameters
        self.result         = None


    def add_log_listener(self,listener):
        self.log.add_log_listener(listener)

    def add_data_listener(self,listener):
        self.log.add_data_listener(listener)

    def update_log(self,data, timestamp = False):
        if(timestamp is True):
            self.log.update_log("["+Utils.time_to_str(time.time())+"]"+" Process"+str(self.id)+"@robot:"+self.id_robot+" "+data+"\n")
        else:
            self.log.update_log(data)
    
    def notify_log_data(self,log,new_data):
        self.update_log(new_data.rstrip()+" (Child of "+self.name+" id_process = "+str(self.id)+")\n",False)

    def formatear_fecha(self, fecha: datetime):
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

    def notificar_actualizacion(self, msg):
        print(msg)
        self.update_log(msg, True)

    def update_element(self, elements: list, url:str, notificada: bool):
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

            for new in elements:
                response = requests.patch(url + str(new.id), headers=headers, data=payload)
                print(response.text)
        
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

