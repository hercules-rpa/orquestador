
import time
from datetime import datetime
from rpa_robot.ControllerSettings import ControllerSettings
from model.process.Process1.Entities.New import New
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus
from model.process.ProcessExtractXml import ProcessExtractXml

NAME = "Extract News"
DESCRIPTION = "Proceso que extrae las noticias de la UCC y SALA DE PRENSA de la Universidad de Murcia."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_NEWS_TRANSFER_REPORT.value
cs = ControllerSettings()

class ProcessExtractNews(ProcessCommand):
    directory = "dest/xml/"
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

    def get_newsnodes(self, params):
        """
        Obtiene los nodos xml relacionados con las noticias
        :param params parámetros para la obtención de los nodos
        :return list lista de nodos obtenidos
        """
        psm = ProcessExtractXml(self.log.id_schedule, self.log.id, self.id_robot, self.priority, self.log.log_file_path, params)
        psm.execute()
        return psm.result

    def set_properties(self, new: New, tagName, node): 
        """
        Método para hidratar las propiedades de una noticia
        :param noticia objeto que contiene la información de una noticia
        :param tagName nombre de la etiqueta del nodo a tratar
        :param nodo nodo a tratar
        """
        try:
            if tagName == 'title':
                new.title = node[0][0].firstChild.data
            if tagName == 'link' or tagName == 'id':
                new.url = node[0][0].firstChild.data
            if tagName == 'dc:creator':
                new.author = node[0][0].firstChild.data
            if tagName == 'dc:date':
                value = node[0][0].firstChild.data
                new.date = value[8:10] + '/' + value[5:7] + '/' + value[0:4]
        except:
            self.notify_update(
                'ERROR: obtención del nodo ' + tagName + ' incorrecta')
        return new

    def process_news(self, news, start_date: datetime, end_date: datetime) -> list:
        """
        Método que filtra las noticias en base a un rango de fechas
        :param news lista de elementos
        :param start_date fecha de inicio del rango
        :param end_date fecha de fin del rango 
        :return list lista de elementos
        """
        result = []
        if news:
            for element in news:
                if element[1]:
                    new = New()
                    for child in element[1]:
                        new = self.set_properties(
                            new, child[0][0].tagName, child)
                    date = datetime.strptime(new.date, "%d/%m/%Y")
                    if date >= start_date and date <= end_date:
                        result.append(new)

        return result

    def get_news(self, start: str, end: str) -> list:
        """
        Método que consulta las noticias a partir de un rango de fechas.
        :param start fecha de inicio
        :param end fecha de fin
        :return list noticias obtenidas
        """
        result = []
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        params = {}
        
        conf = cs.get_process_settings(self.ip_api, self.port_api)
        if 'ucc_url' in conf:                  
            params["url"] = conf['ucc_url']
            params["filename"] = self.directory + "ucc.xml"
            entries = ["title", "id", "dc:creator", "dc:date"]
            params["nodos"] = {"entry": entries}

            self.notify_update('Comienza la obtención de la información de la UCC.')
            elements = self.process_news(
                self.get_newsnodes(params), start_date, end_date)
            if elements:
                self.notify_update('Se han obtenido ' + str(len(elements)) + ' elementos de la UCC.')
                result = elements
        else:
            self.notify_update('ERROR no ha sido posible obtener las noticias de "UCC"')

        # 2. Obtener noticias de sala de prensa
        if 'salaprensa_url' in conf: 
            params["url"] = conf['salaprensa_url']
            params["filename"] = self.directory + "salaprensa.xml"
            entries = ["title", "link", "dc:creator", "dc:date"]
            params["nodos"] = {"item": entries}
            
            self.notify_update('Comienza la obtención de la información de Noticias Sala de Prensa.')

            elements = self.process_news(
                self.get_newsnodes(params), start_date, end_date)
        
            if elements:
                self.notify_update('Se han obtenido ' + str(len(elements)) + ' elementos de Notas de Prensa.')
                result += elements
        else:
            self.notify_update('ERROR no ha sido posible obtener las noticias de "SALA PRENSA"')

        return result

    def execute(self):
        """
        Método encargado de la ejecución del proceso
        """
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0

        self.notify_update(
            "El proceso de obtención de noticias de la UCC y sala de prensa de la Universidad de Murcia ha comenzado.")

        self.log.completed = 50
        news = self.get_news(
            self.parameters['start_date'], self.parameters['end_date'])

        self.log.completed = 100
        self.notify_update(
            "El proceso de obtención de noticias de la UCC y sala de prensa de la Universidad de Murcia ha finalizado.")
        self.result = news
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
