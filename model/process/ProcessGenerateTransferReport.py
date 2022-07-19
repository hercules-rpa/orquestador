import json
import time
from datetime import date, datetime, timedelta

import requests
from model.process.Proceso1.Subprocesos.ProcessExtractAnnouncements import \
    ProcessExtractAnnouncements
from model.process.Proceso1.Subprocesos.ProcessExtractArticles import \
    ProcessExtractArticles
from model.process.Proceso1.Subprocesos.ProcessExtractInvenciones import \
    ProcessExtractInvenciones
from model.process.Proceso1.Subprocesos.ProcessExtractNews import \
    ProcessExtractNews
from model.process.Proceso1.Subprocesos.ProcessExtractProjectsAndContracts import \
    ProcessExtractProjectsAndContracts
from model.process.Proceso1.Subprocesos.ProcessExtractThesis import \
    ProcessExtractThesis
from model.process.ProcessCommand import ProcessCommand, ProcessID, Pstatus
from model.process.ProcessSendMail import ProcessSendMail
from model.SGI import SGI
from model.process.Proceso1.Subprocesos.ProcessExtractOTC import ProcessExtractOTC

NAME = "Process Generate Transfer Report"
DESCRIPTION = "Proceso que genera un informe para el boletín de transferencia."
REQUIREMENTS = []
ID = ProcessID.GENERATETRANSFERREPORT.value


class ProcessGenerateTransferReport(ProcessCommand):
    SGI = SGI()

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def enviar_email(self, emails, body, subject):
        params = {}
        params["user"] = "noreply@um.es"
        params["smtp_server"] = "smtp.gmail.com"
        params["mime_subtype"] = "html"
        params["receivers"] = []
        for r in emails:
            user = {}
            user["sender"] = "noreply@um.es"
            user["receiver"] = r['receiver']
            user["subject"] = subject
            user["body"] = body
            user["attached"] = []
            params["receivers"].append(user)

        psm = ProcessSendMail(self.log.id_schedule,
                              self.log.id, self.id_robot, "1", None, params)
        psm.add_data_listener(self)
        psm.execute()
        return psm.log.state

    def extract_articles(self, start_date, end_date):
        results = []
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        try:
            pextractnews = ProcessExtractArticles(self.log.id_schedule,
                                                  self.log.id, self.id_robot, "1", None, params)
            pextractnews.add_data_listener(self)
            pextractnews.execute()
            results = pextractnews.result

        except Exception as e:
            print(repr(e))
            self.notificar_actualizacion(
                "Error al obtener los artículos científicos.")
            self.log.state = "ERROR"

        return results

    """
    Método encargado de extraer convocatorias utilizando un rango de fechas
    """

    def extract_announcements(self, start_date, end_date):
        results: str = ''
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        process = ProcessExtractAnnouncements(self.log.id_schedule,
                                              self.log.id, self.id_robot, "1", None, params)
        process.add_data_listener(self)
        process.execute()
        results = process.result
        return results

    def extract_invenciones(self, start_date, end_date):
        """
        Método encargado de los elementos de la propiedad industrial
        """
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        process = ProcessExtractInvenciones(self.log.id_schedule,
                                            self.log.id, self.id_robot, "1", None, params)
        process.add_data_listener(self)
        process.execute()
        return process.result

    def extract_tecnologicalOffers(self, start_date, end_date):  
        results = []
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        try:
            pextractoffer = ProcessExtractOTC(self.log.id_schedule,
                                                  self.log.id, self.id_robot, "1", None, params)
            pextractoffer.add_data_listener(self)
            pextractoffer.execute()
            results = pextractoffer.result

        except Exception as e:
            print(repr(e))
            self.notificar_actualizacion(
                "Error al obtener la oferta tecnológica.")
            self.log.state = "ERROR"
        return results

    def extract_thesis(self, start_date, end_date):
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        process = ProcessExtractThesis(self.log.id_schedule,
                                       self.log.id, self.id_robot, "1", None, params)
        process.add_data_listener(self)
        process.execute()
        return process.result

    """
    Método que extrae proyectos y contratos utilizando un rango de fechas.
    """

    def extract_projects_contracts(self, start_date, end_date):
        results = []
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        process = ProcessExtractProjectsAndContracts(self.log.id_schedule,
                                                     self.log.id, self.id_robot, "1", None, params)
        process.add_data_listener(self)
        process.execute()
        results = process.result

        return results

    """
    Método que extrae noticias utilizando un rango de fechas.
    """

    def extract_news(self, start_date, end_date):
        news = []
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        try:
            pextractnews = ProcessExtractNews(self.log.id_schedule,
                                              self.log.id, self.id_robot, "1", None, params)
            pextractnews.add_data_listener(self)
            pextractnews.execute()
            news = pextractnews.result
        except:
            self.notificar_actualizacion("Error al obtener las noticias.")
            self.log.state = "ERROR"

        return news

    def msg_news(self, news: list):
        msg = '<b>' + 'NOTICIAS: '
        if news:
            num = len(news)
            if num > 1:
                msg += 'Se han obtenido ' + \
                    str(num) + ' noticias. </b>' + '<br>'
            else:
                msg += 'Se ha obtenido 1 noticia. </b> <br>'

            cont = 1
            for new in news:
                msg += '<b>NOTICIA ' + str(cont) + ': </b> <br>'
                msg += 'Título: ' + new.title + '<br>'
                msg += 'Autor: ' + new.author + '<br>'
                if new.date:
                    msg += 'Fecha: ' + new.date + '<br>'
                msg += 'Url: <a href="' + new.url + '" target="_blank">' + 'noticia' + \
                    str(cont) + '</a><br>'
                cont += 1
        else:
            msg += "No se han obtenido noticias. </b> <br>"
        return msg

    def msg_articles(self, results: list):
       # return '<b>ARTÍCULOS CIENTÍFICOS: Se han obtenido 3 artículos científicos.</b><br><b>ARTÍCULO CIENTÍFICO 1: </b><br>Nombre: AAATítulo de la publicación -otros<br>Autores: <br>- Antonio Fernando Skarmeta Gomez ORCID: 0000-0002-5525-1259<br>- Nombre Apellidos aaa<br>Fecha: 24/02/2022<br>Url: <a href="http://gnoss/C6D8CADB-BACA-4B77-9C14-E786ED62E66C" target="_blank">http://gnoss/C6D8CADB-BACA-4B77-9C14-E786ED62E66C</a><br><b>ARTÍCULO CIENTÍFICO 2: </b><br>Nombre: Título de la publicación -revista<br>Nombre revista: Harm Reduction Journal<br>Autores: <br>- Antonio Fernando Skarmeta Gomez ORCID: 0000-0002-5525-1259<br>Fecha: 24/02/2022<br>Url: <a href="http://gnoss/75BCED58-A7A3-4CFB-896B-E623C1998105" target="_blank">http://gnoss/75BCED58-A7A3-4CFB-896B-E623C1998105</a><br><b>ARTÍCULO CIENTÍFICO 3: </b><br>Nombre: p Evaluating Federated Learning for intrusion detection in Internet of Things: Review and challengesXY<br>Autores: <br>- Pablo Fernandez Saura<br>- Jorge Bernal Bernabe ORCID: 0000-0002-7538-4788<br>- Antonio Fernando Skarmeta Gomez ORCID: 0000-0002-5525-1259<br>- Jose Luis Hernandez Ramos ORCID: 0000-0001-7697-116X<br>- Enrique Marmol Campos<br>- Aurora Gonzalez Vidal ORCID: 0000-0002-4398-0243<br>- Gianmarco Baldini<br>Fecha: 11/02/2022<br>Áreas científicas: Multidisciplinary, General Artificial Intelligence, General Medicine, Hardware and Architecture, General Medicine<br>Url: <a href="http://gnoss/9F89A166-B7D4-4AC8-91CC-68D4B6D7F82A" target="_blank">http://gnoss/9F89A166-B7D4-4AC8-91CC-68D4B6D7F82A</a><br>'
        msg: str = '<b>ARTÍCULOS CIENTÍFICOS: '
        if results:
            num = len(results)
            if num > 1:
                msg += 'Se han obtenido ' + \
                    str(num) + ' artículos científicos.' + '</b><br>'
            else:
                msg += 'Se ha obtenido 1 artículo científico. </b><br>'

            cont = 1
            for art in results:
                try:
                    msg += '<b>ARTÍCULO CIENTÍFICO ' + str(cont) + ': </b><br>'
                    msg += 'Nombre: ' + art.doc + '<br>'
                    if art.magazine:
                        msg += 'Nombre revista: ' + str(art.magazine) + '<br>'
                    msg += 'Autores: <br>'
                    if art.authors:
                        for author in art.authors:
                            try:
                                msg += '- ' + author.name
                                if author.orcid:
                                    msg += ' ORCID: ' + author.orcid
                                msg += '<br>'
                            except:
                                self.notificar_actualizacion('ERROR al añadir los datos de un autor al artículo ' + str(cont))
                            msg += '<br>'
                    msg += 'Fecha: ' + art.date + '<br>'
                    if art.areas:
                        msg += 'Áreas científicas: ' + art.areas + '<br>'
                    msg += 'Url: <a href="' + art.url + '" target="_blank">' + art.url + '</a><br>'
                except Exception as e:
                    self.notificar_actualizacion(str(e))
                    self.notificar_actualizacion('ERROR al construir el mensaje del artículo ' + str(cont))                
                cont += 1
        else:
            msg += "No se han obtenido artículos científicos.</b><br>"
        return msg

    def msg_otc(self, results: list):
        msg: str = '<b>OFERTA TECNOLÓGICA: '
        if results:
            num = len(results)
            if num > 1:
                msg += 'Se han obtenido ' + \
                    str(num) + ' elementos.' + '</b><br>'
            else:
                msg += 'Se ha obtenido 1 elemento. </b><br>'

            cont = 1
            for art in results:
                try:
                    msg += '<b>OFERTA TECNOLÓGICA ' + str(cont) + ': </b><br>'
                    msg += 'Título: ' + art.title + '<br>'
                    if art.description:
                        msg += 'Descripción: ' + art.description + '<br>'
                    msg += 'Investigadores: <br>'
                    if art.researchers:
                        for author in art.researchers:
                            try:
                                msg += '- ' + author.name + '<br>'
                            except:
                                self.notificar_actualizacion('ERROR al añadir los datos de un investigador a la oferta tecnológica ' + str(cont))
                            msg += '<br>'

                    msg += 'Fecha: ' + art.date + '<br>'
                    
                    msg += 'Url: <a href="' + art.url + '" target="_blank">' + art.url + '</a><br>'
                except Exception as e:
                    self.notificar_actualizacion(str(e))
                    self.notificar_actualizacion('ERROR al construir el mensaje de la oferta tecnológica ' + str(cont))                
                cont += 1
        else:
            msg += "No se han obtenido ofertas tecnológicas.</b><br>"
        return msg

    def persist_execution(self, start_date, end_date, success):
        now = date.today().strftime('%Y/%m/%d')
        payload = json.dumps(
            [{
                "fecha_inicio": time.mktime(time.strptime(start_date.strftime('%Y/%m/%d'), '%Y/%m/%d')),
                "fecha_fin": time.mktime(time.strptime(end_date.strftime('%Y/%m/%d'), '%Y/%m/%d')),
                "fecha_ejecucion": time.mktime(time.strptime(now, '%Y/%m/%d')),
                "exito": success
            }])

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(
            'http://10.208.99.12:5000/api/orchestrator/register/ejecuciones_boletines', headers=headers, data=payload)
        return response

    def get_last_execution(self):
        self.notificar_actualizacion(
            'Obteniendo datos relacionados con la última ejecución del proceso.')
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.get(
            'http://10.208.99.12:5000/api/orchestrator/register/ultima_ejecucion_boletin', headers)
        if response and response.status_code == 200:
            return response
        return None

    def get_dates_by_last_execution(self, start_date, end_date):
        """
        Método que calcula el rango de fechas en base a la última ejecución del proceso si ésta falló.
        Si no falló el rango de fechas no se modifica.
        """
        if start_date and end_date and start_date <= end_date:
            last_execution = self.get_last_execution()
            if last_execution and last_execution.status_code == 200:
                execution = json.loads(last_execution.text)
                if not execution['exito']:
                    self.notificar_actualizacion(
                        'La última ejecución del proceso finalizó con errores.')
                    start_ex = datetime.strptime(time.strftime(
                        "%Y-%m-%d", time.localtime(execution['fecha_inicio'])), "%Y-%m-%d")
                    end_ex = datetime.strptime(time.strftime(
                        "%Y-%m-%d", time.localtime(execution['fecha_fin'])), "%Y-%m-%d")

                    if start_ex <= end_ex:
                        if start_ex < start_date and start_ex < end_date:
                            self.notificar_actualizacion(
                                'Modificación de la fecha de inicio por la fecha de inicio de la última ejecución al ser menor que la elegida.')
                            start_date = start_ex
                            print(str(start_date))
                        if end_ex > end_date and end_ex >= start_date:
                            self.notificar_actualizacion(
                                'Modificación de la fecha de fin por ser mayor la fecha de fin de la última ejecución fallida.')
                            end_date = end_ex
                        print(str(end_date))
        return (start_date, end_date)

    def execute(self):
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0
        self.notificar_actualizacion(
            "El proceso de generación del informe del boletín de transferencia ha comenzado.")

        msg: str = ''
        dates = self.calculate_dates()
        start_date:datetime = dates[0]
        end_date:datetime = dates[1]

       # dates = self.get_dates_by_last_execution(start_date, end_date)
        start_date = dates[0]
        end_date = dates[1]

        if start_date and end_date and start_date <= end_date:
            start_str = start_date.strftime("%Y%m%d%H%M%S")
            end_date = end_date.replace(hour=23, minute=59)
            end_str = end_date.strftime("%Y%m%d%H%M%S")

            offers = self.extract_tecnologicalOffers(start_str, end_str)
            msg += self.msg_otc(offers)
            msg += '<br>'
            
            #thesis = self.extract_thesis(start_date, end_date)
            thesis = None
            if thesis and thesis[1]:
                msg += thesis[1]
                msg += '<br>'

            articles = self.extract_articles(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            msg += self.msg_articles(articles)
            msg += '<br>'

            news = self.extract_news(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            msg += self.msg_news(news)
            msg += '<br>'

            start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            msg += self.extract_announcements(start_str, end_str)[1]
            msg += '<br>'

            elements = self.extract_projects_contracts(start_str, end_str)
            if elements:
                if elements[0]:
                    msg += elements[0][0]
                    msg += '<br>'
                if elements[1]:
                    msg += elements[1][0]
                    msg += '<br>'

            elements = self.extract_invenciones(start_str, end_str)
            if elements:
                msg += elements[0][1]
                msg += '<br>'
                msg += elements[1][1]
                msg += '<br>'

            try:
                receivers = self.parameters['receivers']
                if msg:
                    msg = '<!DOCTYPE html><html><body>' + msg + '</body><br></html>'
                    self.notificar_actualizacion('Se procede a enviar el informe por correo electrónico.')
                    state = self.enviar_email(receivers, msg, "RPA: Infome boletín de transferencia.")
                
                if state == "ERROR":
                    self.notificar_actualizacion('ERROR al enviar el correo electrónico.')
                    self.log.state = "ERROR"
                else:
                    self.log.state = None
                    self.notificar_actualizacion('El informe ha sido enviado correctamente por correo electrónico.')

            except:
                self.notificar_actualizacion(
                    'ERROR: Debe indicar los destinatarios del Informe de Transferencia.')
                self.log.state = "ERROR"

        else:
            self.notificar_actualizacion(
                'Rango de fechas erróneo. Para la ejecución del proceso la fecha de inicio debe ser menor o igual a la fecha de fin.')
            self.log.state = "ERROR"

       # self.persist_execution(start_date, end_date, self.log.state != "ERROR")

        self.log.completed = 100
        self.notificar_actualizacion(
            "El proceso de generación del informe del boletín de transferencia ha finalizado.")
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED

    def kill(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass
