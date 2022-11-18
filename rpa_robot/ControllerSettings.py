
import json
from model.RPA import RPA
from model.EDMA import EDMA
from model.SGI import SGI
from rpa_robot.ControllerRobot import ControllerRobot

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class ControllerSettings(metaclass=Singleton):
    cr = ControllerRobot()
    def get_globals_settings(self, ip_api:str, port_api:str):
        """
        Método que obtiene los parámetros de configuración globales.
        :param ip_api dirección IP de la API
        :param port_api puerto de la API
        :return respuesta recibida
        """
        result = None
        if ip_api and port_api:
            url = 'http://'+ip_api+':'+port_api+'/api/orchestrator/global_settings'
            response = RPA(self.cr.robot.token).get(url)
            if response and response.status_code == 200:
                result = response.text
        return result

    def get_url_upload_cdn(self, ip_api, port_api) -> str:
        result = None
        if ip_api and port_api:
            response = RPA(self.cr.robot.token).get('http://'+ip_api+':'+port_api+'/api/orchestrator/cdn/url')
            if response and response.status_code == 200:
                dict = json.loads(response.text)
                if dict:
                    result = dict['url_upload_cdn']
        return result


    def get_process_settings(self, ip_api, port_api):
        """
        Método que obtiene los parámetros de configuración de los procesos.
        :param ip_api dirección IP de la API
        :param port_api puerto de la API
        :return dict diccionario con parámetros recibidos
        """
        result = None
        if ip_api and port_api:
            url = 'http://'+ip_api+':'+port_api+'/api/orchestrator/process_settings'
            response = RPA(self.cr.robot.token).get(url)
            if response and response.status_code == 200:
                result = json.loads(response.text)
        return result
    
    def get_edma(self, ip_api, port_api) -> EDMA:
        """
        Método que obtiene los parámetros de configuración para consultar Hércules-EDMA.
        :param ip_api dirección IP de la API
        :param port_api puerto de la API
        :return EDMA clase instanciada o None 
        """
        response = self.get_globals_settings(ip_api, port_api)
        if response:
            dict = json.loads(response)
            if dict:
                return EDMA(dict['edma_host_sparql'], str(dict['edma_port_sparql']))
        return None

    def get_sgi(self, ip_api, port_api) -> SGI:
        """
        Método que obtiene los parámetros de configuración para consultar Hércules-SGI.
        :param ip_api dirección IP de la API
        :param port_api puerto de la API
        :return SGI clase instanciada o None 
        """
        response = self.get_globals_settings(ip_api, port_api)
        if response:
            dict = json.loads(response)
            if dict:
                return SGI(dict['sgi_ip'], dict['sgi_user'], dict['sgi_password'])
        return None