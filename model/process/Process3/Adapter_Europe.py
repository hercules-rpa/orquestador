from model.process.Process3.Adapter_Call import Adapter_Call
from model.process.Process3.GrantsEuropeExtractor import GrantsEuropeExtractor
from model.RPA import RPA
from rpa_robot.ControllerRobot import ControllerRobot

import time
import requests
import json


class Adapter_Europe(Adapter_Call):
    """
    Clase del adaptador para Convocatorias de Europa.
    """
    def __init__(self, server, port):
        self.europe = GrantsEuropeExtractor(server, port)
        self.result = []
        self.server = server
        self.port = port
        cr = ControllerRobot()
        self.rpa = RPA(cr.robot.token)

    def search(self, *args: list) -> None:
        """
        Método para buscar por día actual las convocatorias de la BDNS.

        :param args list: Argumento variable con el listado de palabras clave para buscar.
        :return None.
        """
        self.result = []
        self.result = self.europe.search_europe()
        
    
    def search_date(self, start_date: str, end_date: str, *args: list) -> None:
        """
        Método para buscar por rango de fechas las convocatorias de la BDNS.

        :param start_date str: Fecha en formato string desde dónde se empieza la búsqueda.
        :param end_date str: Fecha en formato string desde dónde se acaba la búsqueda.
        :param args list: Argumento variable con el listado de palabras clave para buscar.
        :return None.
        """
        self.result = []
        self.result = self.europe.search_europe_date(start_date, end_date)

    def notify(self) -> str:
        """
        Método de actualización del proceso.

        :return Devuelve en formato string un log de cómo se ha ejecutado el proceso hasta el momento que se invoca
        """
        output = ""
        bbdd_url = "http://" + self.server + ":" + self.port +"/api/orchestrator/register/convocatorias?notificada=false&_from=EUROPA2020"
        response = self.rpa.get(bbdd_url)
        if response.ok:
            array = json.loads(response.text)
            output += "Número Total de convocatorias: " + str(len(array))
            for item in array:
                output += "\n\nConvocatoria con nombre: " + item['titulo'] + "\n\t URL: " + item['url'] + ". \n\t Fecha de publicación: " + time.strftime('%d/%m/%Y', time.localtime(item['fecha_publicacion'])) + ". \n\t Fecha Fin: " + time.strftime('%d/%m/%Y', time.localtime(item['fecha_creacion']))
            return output
        return output

    def change_notify(self) -> None:
        """
        Método para cambiar en la base de datos interna las convocatorias notificadas.
        """
        return self.europe.change_notify()