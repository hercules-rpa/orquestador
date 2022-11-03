import json
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessSendMail import ProcessSendMail
import re

"""
Clase utilizada para añadir métodos que sirven de utilidad para los procesos
"""
class UtilsProcess():
    def __init__(self, id_schedule:str = None, id_log:str = None, id_robot:str = None, 
    priority:str = None, log_file_path:str = None):
        self.id_schedule = id_schedule
        self.id_robot = id_robot
        self.id_log = id_log
        self.priority = priority
        self.log_file_path = log_file_path

    def send_email(self, emails, body, subject, attached:list=[],mime_subtype:str = None, port:int =25, process:ProcessCommand=None):
        """
        Método encargado de enviar un correo electrónico.
        :param emails lista de direcciones de correos electrónicos
        :param body cuerpo del mensaje
        :param subject asunto del mensaje
        :param attached lista de ficheros adjuntos
        :param mime_subtype atributo myme para el envío de mensajes html
        :param port puerto utilizado para el envío correo electrónico
        :param process proceso que realiza la llamada a este método
        :return código de error del proceso SendEmail
        """
        params = {}
        params["user"] = "noreply@um.es"
        params["smtp_server"] = "smtp.um.es"
        params["port"] = port
        if mime_subtype:
            params["mime_subtype"] = mime_subtype
        params["receivers"] = []
        for r in emails:
            user = {}
            user["sender"] = "noreply@um.es"
            user["receiver"] = r['receiver']
            user["subject"] = subject
            user["body"] = body
            user["attached"] = attached
            params["receivers"].append(user)
        psm = ProcessSendMail(self.id_schedule,
                              self.id_log, self.id_robot, self.priority, self.log_file_path, params)
        if process:
            psm.add_data_listener(process)
        psm.execute()
        return psm.log.state

    def send_email_html(self,emails, body, subject, attached:list=[], port:int=25, process:ProcessCommand=None):
        """
        Método encargado de enviar un correo electrónico.
        :param emails lista de direcciones de correos electrónicos
        :param body cuerpo del mensaje
        :param subject asunto del mensaje
        :param attached lista de ficheros adjuntos
        :param port puerto utilizado para el envío correo electrónico
        :param process proceso que realiza la llamada
        :return código de error del proceso SendEmail
        """
        return self.send_email(emails, body, subject, attached,'html', port, process)

    def is_match(self, regex:str, content:str) -> bool:
        """
        Método que evalúa si se cumple un patrón dentro de una cadena de caracteres.
        :param regex patrón a cumplir
        :param content contenido a analizar
        :return bool True si cumple el patrón, False si no.
        """
        result:bool = False
        if regex and content:
            reg = re.compile(regex)
            if reg.match(content):
                result = True
        return result

    def get_configurations(self, filename):
        """
        Método que obtiene la configuración del robot.
        :param filename nombre del fichero donde se debe buscar la configuración.
        :return str devuelve la configuración en formato str
        """
        try:
            with open(filename, encoding="utf-8") as json_robot:
                config = json.load(json_robot)
                return config
        except:
            print("ERROR no se ha encontrado el fichero de configuración.")
        return None

    