from model.process.Proceso3.Adaptador_Convocatoria import Adaptador_Convocatoria
from model.process.Proceso3.GrantsEuropeExtractor import GrantsEuropeExtractor

import time

class Adaptador_Europa(Adaptador_Convocatoria):

    def __init__(self):
        self.europa = GrantsEuropeExtractor()
        self.result = []

    def buscar(self, *args):
        self.result = []
        self.result = self.europa.search_europe()
        
    
    def buscar_fecha(self, fecha_desde, fecha_hasta, *args):
        self.result = []
        self.result = self.europa.search_europe_date(fecha_desde, fecha_hasta)

    def notify(self):
        output = ""
        output += self.europa.msg_notify
        output += "Número total de convocatorias: " + str(len(self.result))
        for item in self.result:
            output += "\n\nConvocatoria con nombre: " + item['titulo'] + "\n\t URL: " + item['url'] + ". \n\t Fecha de publicación: " + time.strftime('%d/%m/%Y', time.localtime(item['fecha_publicacion'])) + ". \n\t Fecha Fin: " + time.strftime('%d/%m/%Y', time.localtime(item['fecha_creacion']))
        return output

    def cambio_notificadas(self):
        return self.europa.cambio_notificadas()