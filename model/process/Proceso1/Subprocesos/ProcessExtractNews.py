
import time
from datetime import datetime
from model.process.Proceso1.Entidades.New import New
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus
from model.process.ProcessExtractXml import ProcessExtractXml

NAME = "Extract Noticias"
DESCRIPTION = "Proceso que extrae las noticias de la UCC y SALA DE PRENSA de la Universidad de Murcia."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_NEWS.value


class ProcessExtractNews(ProcessCommand):
    directory = "dest/xml/"
    URL_SALAPRENSA = "https://www.um.es/web/sala-prensa/notas-de-prensa?p_p_id=com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_GNs6DmEJkR1y&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=getRSS&p_p_cacheability=cacheLevelPage&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_GNs6DmEJkR1y_currentURL=%2Fweb%2Fsala-prensa%2Fnotas-de-prensa&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_GNs6DmEJkR1y_portletAjaxable=true"
    URL_UCC = "https://www.um.es/web/ucc/inicio?p_p_id=com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_qQfO4ukErIc3&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=getRSS&p_p_cacheability=cacheLevelPage&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_qQfO4ukErIc3_currentURL=%2Fweb%2Fucc%2F&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_qQfO4ukErIc3_portletAjaxable=true"

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def get_newsnodes(self, params):
        """Obtiene los nodos xml relacionados con las noticias"""
        psm = ProcessExtractXml(self.log.id_schedule,
                                self.log.id, self.id_robot, "1", None, params)
        psm.add_data_listener(self)
        psm.execute()
        return psm.result

    def set_properties(self, noticia: New, tagName, nodo): 
        """
        Método para informar las propiedades de una noticia
        """
        try:
            if tagName == 'title':
                noticia.title = nodo[0][0].firstChild.data
            if tagName == 'link' or tagName == 'id':
                noticia.url = nodo[0][0].firstChild.data
            if tagName == 'dc:creator':
                noticia.author = nodo[0][0].firstChild.data
            if tagName == 'dc:date':
                value = nodo[0][0].firstChild.data
                noticia.date = value[8:10] + '/' + value[5:7] + '/' + value[0:4]
        except:
            self.notificar_actualizacion(
                'ERROR: obtención del nodo ' + tagName + ' incorrecta')
        return noticia

    def process_news(self, news, start_date: datetime, end_date: datetime) -> list:
        """
        Método que filtra las noticias en base a un rango de fechas
        """
        result = []
        if news:
            for new in news:
                if new[1]:
                    noticia = New()
                    for hijo in new[1]:
                        noticia = self.set_properties(
                            noticia, hijo[0][0].tagName, hijo)
                    # Comprobar que la fecha esté dentro del rango
                    date = datetime.strptime(noticia.date, "%d/%m/%Y")
                    if date >= start_date and date <= end_date:
                        result.append(noticia)

        return result

    def get_news(self, start: str, end: str) -> list:
        """Obtiene la lista de noticias"""
        result = []
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        # 1. Obtener noticias de ucc
        params = {}
        params["url"] = self.URL_UCC
        params["filename"] = self.directory + "ucc.xml"
        entries = ["title", "id", "dc:creator", "dc:date"]
        params["nodos"] = {"entry": entries}

        self.notificar_actualizacion('Comienza la obtención de la información de la UCC.')
        elements = self.process_news(
            self.get_newsnodes(params), start_date, end_date)
        if elements:
            self.notificar_actualizacion('Se han obtenido ' + str(len(elements)) + ' elementos de la UCC.')
            result = elements

        # 2. Obtener noticias de sala de prensa
        params["url"] = self.URL_SALAPRENSA
        params["filename"] = self.directory + "salaprensa.xml"
        entries = ["title", "link", "dc:creator", "dc:date"]
        params["nodos"] = {"item": entries}
        
        self.notificar_actualizacion('Comienza la obtención de la información de Noticias Sala de Prensa.')

        elements = self.process_news(
            self.get_newsnodes(params), start_date, end_date)
        if elements:
            self.notificar_actualizacion('Se han obtenido ' + str(len(elements)) + ' elementos de Notas de Prensa.')
            result += elements

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

        self.notificar_actualizacion(
            "El proceso de obtención de noticias de la UCC y sala de prensa de la Universidad de Murcia ha comenzado.")

        self.log.completed = 50
        news = self.get_news(
            self.parameters['start_date'], self.parameters['end_date'])

        self.log.completed = 100
        self.notificar_actualizacion(
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
