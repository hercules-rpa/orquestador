
import time
from datetime import date, datetime
import requests
import json
from model.process.New import New
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus
from model.process.ProcessExtractXml import ProcessExtractXml

NAME = "Extract Noticias"
DESCRIPTION = "Proceso que extrae las noticias de la UCC y SALA DE PRENSA de la Universidad de Murcia."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_NEWS.value


class ProcessExtractNews(ProcessCommand):
    URL_PERSIST = 'http://10.208.99.12:5000/api/orchestrator/register/noticias'
    URL_GET = 'http://10.208.99.12:5000/api/orchestrator/register/noticias?notificada=false'
    directory = "dest/xml/"
    URL_SALAPRENSA = "https://www.um.es/web/sala-prensa/notas-de-prensa?p_p_id=com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_GNs6DmEJkR1y&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=getRSS&p_p_cacheability=cacheLevelPage&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_GNs6DmEJkR1y_currentURL=%2Fweb%2Fsala-prensa%2Fnotas-de-prensa&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_GNs6DmEJkR1y_portletAjaxable=true"
    URL_UCC = "https://www.um.es/web/ucc/inicio?p_p_id=com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_qQfO4ukErIc3&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=getRSS&p_p_cacheability=cacheLevelPage&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_qQfO4ukErIc3_currentURL=%2Fweb%2Fucc%2F&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_qQfO4ukErIc3_portletAjaxable=true"

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, DESCRIPTION, REQUIREMENTS,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def persist_new(self, new: New, notificada: bool):
        payload = json.dumps([
            {
                "titulo": new.title,
                "autor": new.author,
                "url": new.url,
                "fecha": new.date,
                "notificada": notificada
            }])

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(
            self.URL_PERSIST, headers=headers, data=payload)
        return response

    def get_noNotificadas(self):
        """Obtiene las noticias no notificadas en procesos anteriores"""
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.get(self.URL_GET, headers)
        result = []
        if response.status_code == 200:
            json_dicti = json.loads(response.text)

            for key in json_dicti:
                if key != "message":
                    mktime = float(key['fecha'])
                    date = time.strftime('%d/%m/%Y', time.localtime(mktime))
                    new = New(
                        key['id'], key['titulo'], date, key['autor'], key['url'])
                    result.append(new)

            if result:
                self.notificar_actualizacion(
                    "No se han obtenido noticias no enviadas en procesos anteriores.")

        return result

    def get_newsnodes(self, params):
        """Obtiene los nodos xml relacionados con las noticias"""
        psm = ProcessExtractXml(self.log.id_schedule,
                                self.log.id, self.id_robot, "1", None, params)
        psm.add_data_listener(self)
        psm.execute()
        return psm.result

    def set_properties(self, noticia: New, tagName, nodo):
        if tagName == 'title':
            noticia.title = nodo[0][0].firstChild.data
        if tagName == 'link' or tagName == 'id':
            noticia.url = nodo[0][0].firstChild.data
        if tagName == 'dc:creator':
            noticia.author = nodo[0][0].firstChild.data
        if tagName == 'dc:date':
            value = nodo[0][0].firstChild.data
            noticia.date = value[8:10] + '/' + value[5:7] + '/' + value[0:4]
        return noticia

    def get_news(self, start: str, end: str) -> list:
        """Obtiene la lista de noticias"""

        result = []
        start_date = datetime.strptime(start, "%d/%m/%Y")
        end_date = datetime.strptime(end, "%d/%m/%Y")

        # 1. Obtener noticias de ucc
        params = {}
        params["url"] = self.URL_UCC
        params["filename"] = self.directory + "ucc.xml"
        entries = ["title", "id", "dc:creator", "dc:date"]
        params["nodos"] = {"entry": entries}

        news_ucc = self.get_newsnodes(params)
        if news_ucc:
            for new in news_ucc:
                try:
                    noticia = New()
                    for hijo in new[1]:
                        noticia = self.set_properties(
                            noticia, hijo[0][0].tagName, hijo)

                    # Comprobar que la fecha esté dentro del rango
                    date = datetime.strptime(noticia.date, "%d/%m/%Y")
                    if date >= start_date and date <= end_date:
                        result.append(noticia)
                        response = self.persist_new(noticia, False)
                        try:
                            if response.text:
                                json_dicti = json.loads(response.text)
                                if json_dicti['status'] == 'ok':
                                    noticia.id = str(json_dicti['Noticias'][0])
                        except:
                            self.notificar_actualizacion(
                                "Error al obtener el identificador de la noticia.")

                except:
                    print('ERROR: obtención de atributos')

        # 2. Obtener noticias de sala de prensa
        params["url"] = self.URL_SALAPRENSA
        params["filename"] = self.directory + "salaprensa.xml"
        entries = ["title", "link", "dc:creator", "dc:date"]
        params["nodos"] = {"item": entries}

        news_sp = self.get_newsnodes(params)
        if news_sp:
            for new in news_sp:
                try:
                    noticia = New()
                    for hijo in new[1]:
                        noticia = self.set_properties(
                            noticia, hijo[0][0].tagName, hijo)

                    # Comprobar que la fecha esté dentro del rango
                    date = datetime.strptime(noticia.date, "%d/%m/%Y")
                    if date >= start_date and date <= end_date:
                        result.append(noticia)
                        response = self.persist_new(noticia, False)
                        try:
                            if response.text:
                                json_dicti = json.loads(response.text)
                                if json_dicti['status'] == 'ok':
                                    noticia.id = str(json_dicti['Noticias'][0])
                        except:
                            self.notificar_actualizacion(
                                "Error al obtener el identificador de la noticia.")
                except:
                    print('ERROR: obtención de atributos')

        return result

    def execute(self):
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0

        self.notificar_actualizacion(
            "El proceso de obtención de noticias de la UCC y sala de prensa de la Universidad de Murcia ha comenzado.")

        try:
            start_date = self.parameters['start_date']
            if not start_date:
                start_date = self.formatear_fecha(datetime.today())
        except:
            start_date = self.formatear_fecha(datetime.today())

        try:
            end_date = self.parameters['end_date']
            if not end_date:
                end_date = self.formatear_fecha(datetime.today())
        except:
            end_date = self.formatear_fecha(datetime.today())

        self.log.completed = 33
        self.notificar_actualizacion('Obteniendo noticias.')
        news = self.get_news(start_date, end_date)
        self.log.completed = 66

        if news:
            print('noticias totales: ' + str(len(news)))

        self.notificar_actualizacion(
            "Obteniendo noticias no notificadas en procesos anteriores.")
        # consulta de las noticias no notificadas en procesos anteriores
        #noNotificadas = self.get_noNotificadas()
        # if noNotificadas:
        #news = noNotificadas + news

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
