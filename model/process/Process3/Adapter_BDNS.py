from model.process.Process3.Adapter_Call import Adapter_Call
from model.process.Process3.BDNS import BDNS

import time

class Adapter_BDNS(Adapter_Call):
    """
    Clase Adaptador BDNS que adapta su contenido para la búsqueda de convocatorias en la BDNS.
    """
    def __init__(self, server, port):
        self.BDNS = BDNS(server, port)
        self.result = {}
        

    def search(self, *args: list) -> None:
        """
        Método para buscar por día actual las convocatorias de la BDNS.

        :param args list: Argumento variable con el listado de palabras clave para buscar.
        :return None.
        """
        if len(args) == 0:
            self.result = self.BDNS.search_with_date(time.localtime(), time.localtime())
        elif len(args) == 1 and isinstance(args[0], str):
            self.result = self.BDNS.search_with_date(time.localtime(), time.localtime(), args[0])
        else:
            raise Exception("Se ha introducido un parámetro que no es válido para esta función")

    def search_date(self, start_date: str, end_date: str, *args: list) -> None:
        """
        Método para buscar por rango de fechas las convocatorias de la BDNS.

        :param start_date str: Fecha en formato string desde dónde se empieza la búsqueda.
        :param end_date str: Fecha en formato string desde dónde se acaba la búsqueda.
        :param args list: Argumento variable con el listado de palabras clave para buscar.
        :return None.
        """
        if len(args) == 0:
            self.result = self.BDNS.search_with_date(time.strptime(start_date, '%Y-%m-%d'), time.strptime(end_date, '%Y-%m-%d'))
        elif len(args) == 1 and isinstance(args[0], str):
            self.result = self.BDNS.search_with_date(time.strptime(start_date, '%Y-%m-%d'), time.strptime(end_date, '%Y-%m-%d'), args[0])
        else:
            raise Exception("Se ha introducido un parámetro que no es válido para esta función")

    def obtain_resources(self, bdns_num: int) -> list:
        """
        Método para descargar los archivos de una convocatoria.

        :param bdns_num int: Número de la BDNS.
        :return array con las rutas donde se encuentran esos archivos.
        """
        return self.BDNS.obtain_resources_bdns(bdns_num)

    def expand_info(self, bdns_num: int) -> dict:
        """
        Método para obtener la información ampliada de una convocatoria.

        :param bdns_num int: Número de la BDNS.
        :return Diccionario donde se encuentra toda la información de esa convocatoria.        
        """
        return self.BDNS.obtain_data_bdns(bdns_num)

    def notify(self) -> str:
        """
        Método de actualización del proceso.

        :return Devuelve en formato string un log de cómo se ha ejecutado el proceso hasta el momento que se invoca
        """
        return self.BDNS.notify()