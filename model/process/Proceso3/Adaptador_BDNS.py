from model.process.Proceso3.Adaptador_Convocatoria import Adaptador_Convocatoria
from model.process.Proceso3.BDNS import BDNS

import requests
import time
import json

class Adaptador_BDNS(Adaptador_Convocatoria):
    
    def __init__(self):
        self.BDNS = BDNS()
        self.result = {}

    def buscar(self, *args):
        if len(args) == 0:
            self.result = self.BDNS.search_with_date(time.strftime('%d/%m/%Y'), time.strftime('%d/%m/%Y'))
        elif len(args) == 1 and isinstance(args[0], str):
            self.result = self.BDNS.search_with_date(time.strftime('%d/%m/%Y'), time.strftime('%d/%m/%Y'), args[0])
        else:
            raise Exception("Se ha introducido un parámetro que no es válido para esta función")

    def buscar_fecha(self, fecha_desde: str, fecha_hasta: str, *args):
        if len(args) == 0:
            self.result = self.BDNS.search_with_date(time.strptime(fecha_desde, '%d/%m/%Y'), time.strptime(fecha_hasta, '%d/%m/%Y'))
        elif len(args) == 1 and isinstance(args[0], str):
            self.result = self.BDNS.search_with_date(time.strptime(fecha_desde, '%d/%m/%Y'), time.strptime(fecha_hasta, '%d/%m/%Y'), args[0])
        else:
            raise Exception("Se ha introducido un parámetro que no es válido para esta función")

    def buscar_recursos(self, bdns_num):
        return self.BDNS.obtain_resources_bdns(bdns_num)

    def ampliar_info(self, bdns_num):
        return self.BDNS.obtain_data_bdns(bdns_num)

    def notify(self):
        return self.BDNS.notify()