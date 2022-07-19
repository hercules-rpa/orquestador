from model.process.Proceso3.Adaptador_Convocatoria import Adaptador_Convocatoria
from model.process.Proceso3.GrantsEuropeExtractor import GrantsEuropeExtractor

import time
import requests
import json


class Adaptador_Europa(Adaptador_Convocatoria):
    """
    Clase del adaptador para Convocatorias de Europa.
    """
    def __init__(self, server: str="10.208.99.12"):
        self.europa = GrantsEuropeExtractor()
        self.result = []
        self.server = server

    def buscar(self, *args: list) -> None:
        """
        Método para buscar por día actual las convocatorias de la BDNS.

        :param args list: Argumento variable con el listado de palabras clave para buscar.
        :return None.
        """
        self.result = []
        self.result = self.europa.search_europe(self.server)
        
    
    def buscar_fecha(self, fecha_desde: str, fecha_hasta: str, *args: list) -> None:
        """
        Método para buscar por rango de fechas las convocatorias de la BDNS.

        :param fecha_desde str: Fecha en formato string desde dónde se empieza la búsqueda.
        :param fecha_hasta str: Fecha en formato string desde dónde se acaba la búsqueda.
        :param args list: Argumento variable con el listado de palabras clave para buscar.
        :return None.
        """
        self.result = []
        self.result = self.europa.search_europe_date(fecha_desde, fecha_hasta)

    def notify(self) -> str:
        """
        Método de actualización del proceso.

        :return Devuelve en formato string un log de cómo se ha ejecutado el proceso hasta el momento que se invoca
        """
        output = ""
        bbdd_url = "http://" + self.server + ":5000/api/orchestrator/register/convocatorias?notificada=false&_from=EUROPA2020"
        response = requests.get(bbdd_url)
        if response.ok:
            array = json.loads(response.text)
            output += "Número Total de convocatorias: " + str(len(array))
            for item in array:
                output += "\n\nConvocatoria con nombre: " + item['titulo'] + "\n\t URL: " + item['url'] + ". \n\t Fecha de publicación: " + time.strftime('%d/%m/%Y', time.localtime(item['fecha_publicacion'])) + ". \n\t Fecha Fin: " + time.strftime('%d/%m/%Y', time.localtime(item['fecha_creacion']))
            return output
        return output

    def cambio_notificadas(self) -> None:
        """
        Método para cambiar en la base de datos interna las convocatorias notificadas.
        """
        return self.europa.cambio_notificadas()