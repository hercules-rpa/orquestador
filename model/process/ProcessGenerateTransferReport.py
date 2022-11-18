import json
import time
from datetime import date, datetime
from rpa_robot.ControllerRobot import ControllerRobot
from rpa_robot.ControllerSettings import ControllerSettings
from model.process.Process1.Subprocess.ProcessExtractCalls import \
    ProcessExtractCalls
from model.process.Process1.Subprocess.ProcessExtractArticles import \
    ProcessExtractArticles
from model.process.Process1.Subprocess.ProcessExtractInventions import \
    ProcessExtractInventions
from model.process.Process1.Subprocess.ProcessExtractNews import \
    ProcessExtractNews
from model.process.Process1.Subprocess.ProcessExtractProjectsAndContracts import \
    ProcessExtractProjectsAndContracts
from model.process.Process1.Subprocess.ProcessExtractThesis import \
    ProcessExtractThesis
from model.process.ProcessCommand import ProcessCommand, ProcessID, Pstatus
from model.process.UtilsProcess import UtilsProcess
from model.RPA import RPA
from model.process.Process1.Subprocess.ProcessExtractOTC import ProcessExtractOTC

NAME = "Process Generate Transfer Report"
DESCRIPTION = "Proceso que genera un informe para el boletín de transferencia."
REQUIREMENTS = []
ID = ProcessID.GENERATE_TRANSFER_REPORT.value
cs = ControllerSettings()


class ProcessGenerateTransferReport(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None, ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

        cr = ControllerRobot()        
        self.rpa:RPA = RPA(cr.robot.token)


    def extract_articles(self, start_date, end_date):
        """
        Método encargado de la extracción de los artículos.
        :param start_date fecha inicio del rango
        :param end_date fecha fin del rango
        :return list lista de artículos obtenidos
        """
        results = []
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        try:
            pextractarticles = ProcessExtractArticles(self.log.id_schedule,
                                                      self.log.id, self.id_robot, "1", None, params, self.ip_api, self.port_api)
            pextractarticles.add_data_listener(self)
            pextractarticles.execute()
            results = pextractarticles.result

        except Exception as e:
            print(repr(e))
            self.notify_update(
                "Error al obtener los artículos científicos.")
            self.log.state = "ERROR"

        return results

    def extract_calls(self, start_date, end_date):
        """
        Método encargado de la obtención de las convocatorias dado un rango de fechas.
        :param start_date fecha inicio del rango
        :param end_date fecha fin del rango
        :return tuple nº de convocatorias obtenidas y mensaje con la información de las convocatorias
        """
        results: str = ''
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        process = ProcessExtractCalls(self.log.id_schedule,
                                      self.log.id, self.id_robot, "1", None, params, self.ip_api, self.port_api)
        process.add_data_listener(self)
        process.execute()
        results = process.result
        return results

    def extract_inventions(self, start_date, end_date):
        """
        Método encargado de los elementos de la propiedad industrial e intelectual
        :param start_date fecha inicio del rango
        :param end_date fecha fin del rango
        :return tuple tupla con los mensajes que se insertarán en el correo electrónico
        """
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        process = ProcessExtractInventions(self.log.id_schedule,
                                           self.log.id, self.id_robot, "1", None, params, self.ip_api, self.port_api)
        process.add_data_listener(self)
        process.execute()
        return process.result

    def extract_tecnologicalOffers(self, start_date, end_date):
        """
        Método encargado de obtener los elementos de la oferta tecnológica utilizando
        Hércules-ED.
        :param start_date fecha inicio del rango
        :param end_date fecha fin del rango
        :return list lista de elementos obtenidos
        """
        results = []
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        try:
            pextractoffer = ProcessExtractOTC(self.log.id_schedule,
                                              self.log.id, self.id_robot, "1", None, params, self.ip_api, self.port_api)
            pextractoffer.add_data_listener(self)
            pextractoffer.execute()
            results = pextractoffer.result

        except Exception as e:
            print(repr(e))
            self.notify_update(
                "Error al obtener la oferta tecnológica.")
            self.log.state = "ERROR"
        return results

    def extract_thesis(self, start_date, end_date):
        """
        Método encargado de la obtención de tesis doctorales utilizando un rango de fechas
        :param start_date fecha inicio del rango
        :param end_date fecha fin del rango
        :return tuple nº de elementos y mensaje que se insertará en el correo electrónico
        """
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        process = ProcessExtractThesis(self.log.id_schedule,
                                       self.log.id, self.id_robot, "1", None, params, self.ip_api, self.port_api)
        process.add_data_listener(self)
        process.execute()
        return process.result

    def extract_projects_contracts(self, start_date, end_date):
        """
        Método encargado de la obtención de proyectos y contratos utilizando un rango de fechas
        :param start_date fecha inicio del rango
        :param end_date fecha fin del rango
        :return tuple cada elemento contiene una tupla con el nº de elementos obtenidos y el mensaje a enviar
        """
        results = []
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        process = ProcessExtractProjectsAndContracts(self.log.id_schedule,
                                                     self.log.id, self.id_robot, "1", None, params, self.ip_api, self.port_api)
        process.add_data_listener(self)
        process.execute()
        results = process.result

        return results

    def extract_news(self, start_date, end_date):
        """
        Método que extrae noticias utilizando un rango de fechas.
        :param start_date fecha inicio del rango
        :param end_date fecha fin del rango
        :return list lista con los elementos obtenidos
        """
        news = []
        params = {}
        params["start_date"] = start_date
        params["end_date"] = end_date
        try:
            pextractnews = ProcessExtractNews(self.log.id_schedule,
                                              self.log.id, self.id_robot, "1", None, params, self.ip_api, self.port_api)
            pextractnews.add_data_listener(self)
            pextractnews.execute()
            news = pextractnews.result
        except:
            self.notify_update("Error al obtener las noticias.")
            self.log.state = "ERROR"

        return news

    def msg_news(self, news: list):
        """
        Método que construye el mensaje utilizando la lista de noticias.
        :param news lista de noticias
        :return str sección noticias para adjuntar en el correo electrónico final
        """
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
        """
        Método que construye el mensaje utilizando la lista de artículos.
        :param news lista de artículos
        :return str sección artículos para adjuntar en el correo electrónico final
        """
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
                    if art.magazine and str(art.magazine) != 'nan':
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
                                self.notify_update(
                                    'ERROR al añadir los datos de un autor al artículo ' + str(cont))
                    msg += 'Fecha: ' + art.date + '<br>'
                    if art.areas:
                        msg += 'Áreas científicas: ' + art.areas + '<br>'
                    msg += 'Url: <a href="' + art.url + \
                        '" target="_blank">articulo' + str(cont) + '</a><br>'
                except Exception as e:
                    self.notify_update(str(e))
                    self.notify_update(
                        'ERROR al construir el mensaje del artículo ' + str(cont))
                cont += 1
        else:
            msg += "No se han obtenido artículos científicos.</b><br>"
        return msg

    def msg_otc(self, results: list):
        """
        Método que construye el mensaje utilizando la lista de ofertas tecnológicas.
        :param news lista de ofertas tecnológicas
        :return str sección oferta tecnológica para adjuntar en el correo electrónico final
        """
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
                                self.notify_update(
                                    'ERROR al añadir los datos de un investigador a la oferta tecnológica ' + str(cont))
                    msg += 'Fecha: ' + art.date + '<br>'

                    msg += 'Url: <a href="' + art.url + \
                        '" target="_blank">otc-' + str(cont) + '</a><br>'
                except Exception as e:
                    self.notify_update(str(e))
                    self.notify_update(
                        'ERROR al construir el mensaje de la oferta tecnológica ' + str(cont))
                cont += 1
        else:
            msg += "No se han obtenido ofertas tecnológicas.</b><br>"
        return msg

    def persist_execution(self, start_date, end_date, success):
        """
        Método encargado de la persistencia en base de datos de los datos
        de la ejecución del proceso.
        :param start_date fecha inicio rango
        :param end_date fecha fin rango
        :param success True si el proceso se ha ejecutado correctamente.
        """
        response = None
        try:
            now = date.today().strftime('%Y/%m/%d')
            payload = json.dumps(
                [{
                    "fecha_inicio": time.mktime(time.strptime(start_date.strftime('%Y/%m/%d'), '%Y/%m/%d')),
                    "fecha_fin": time.mktime(time.strptime(end_date.strftime('%Y/%m/%d'), '%Y/%m/%d')),
                    "fecha_ejecucion": time.mktime(time.strptime(now, '%Y/%m/%d')),
                    "exito": success
                }])
            
            response = self.rpa.post('http://' + self.ip_api + ':' + self.port_api + '/api/orchestrator/register/ejecuciones_boletines',
            payload)

        except:
            self.notify_update(
                "ERROR al persistir los datos de la ejecución del proceso")
        return response

    def get_last_execution(self):
        """
        Método que obtiene los datos de la última ejecución del proceso.
        :return json datos de la ejecución
        """
        self.notify_update(
            'Obteniendo datos relacionados con la última ejecución del proceso.')
        result = None
        try:
            response = self.rpa.get(
                'http://'+self.ip_api+':'+self.port_api+'/api/orchestrator/register/ultima_ejecucion_boletin')
            if response and response.status_code != 200:
                result = response
        except:
            self.notify_update(
                "ERROR no ha sido posible obtener los datos de la última ejecución del proceso")
        return result

    def get_dates_by_last_execution(self, start_date, end_date):
        """
        Método que calcula el rango de fechas en base a la última ejecución del proceso si ésta falló.
        Si no falló el rango de fechas no se modifica.
        :param start_date fecha inicio
        :param end_date fecha fin
        :return tuple tupla con el inicio y fin calculados
        """
        try:
            start = start_date
            end = end_date
            if start_date and end_date and start_date <= end_date:
                last_execution = self.get_last_execution()
                if last_execution and last_execution.status_code == 200:
                    execution = json.loads(last_execution.text)
                    if not execution['exito']:
                        self.notify_update(
                            'La última ejecución del proceso finalizó con errores.')
                        start_ex = datetime.strptime(time.strftime(
                            "%Y-%m-%d", time.localtime(execution['fecha_inicio'])), "%Y-%m-%d")
                        end_ex = datetime.strptime(time.strftime(
                            "%Y-%m-%d", time.localtime(execution['fecha_fin'])), "%Y-%m-%d")

                        if start_ex <= end_ex:
                            if start_ex < start_date and start_ex < end_date:
                                self.notify_update(
                                    'Modificación de la fecha de inicio por la fecha de inicio de la última ejecución al ser menor que la elegida.')
                                start = start_ex
                            if end_ex > end_date and end_ex >= start_date:
                                self.notify_update(
                                    'Modificación de la fecha de fin por ser mayor la fecha de fin de la última ejecución fallida.')
                                end = end_ex
        except Exception as e:
            print(repr(e))
            self.notify_update(
                'ERROR al calcular el rango de fechas utilizando la última ejecución.')

        return (start, end)

    def execute(self):
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0
        self.notify_update(
            "El proceso de generación del informe del boletín de transferencia ha comenzado.")

        msg: str = ''
        dates = self.calculate_dates()
        start_date: datetime = dates[0]
        end_date: datetime = dates[1]

        dates = self.get_dates_by_last_execution(start_date, end_date)
        start_date = dates[0]
        end_date = dates[1]

        if start_date and end_date and start_date <= end_date:
            start_str = start_date.strftime("%Y%m%d%H%M%S")
            end_date = end_date.replace(hour=23, minute=59)
            end_str = end_date.strftime("%Y%m%d%H%M%S")
            self.log.completed = 10
            offers = self.extract_tecnologicalOffers(start_str, end_str)
            self.log.completed = 20
            msg += self.msg_otc(offers)
            msg += '<br>'
            self.log.completed = 30
            thesis = self.extract_thesis(start_date, end_date)
            if thesis and thesis[1]:
                msg += thesis[1]
                msg += '<br>'
            self.log.completed = 40
            articles = self.extract_articles(start_date.strftime(
                "%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            msg += self.msg_articles(articles)
            msg += '<br>'
            self.log.completed = 50
            news = self.extract_news(start_date.strftime(
                "%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            msg += self.msg_news(news)
            msg += '<br>'
            self.log.completed = 60
            start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            calls = self.extract_calls(start_str, end_str)
            if calls and calls[1]:
                msg += calls[1]
                msg += '<br>'
            self.log.completed = 70
            elements = self.extract_projects_contracts(start_str, end_str)
            if elements:
                if elements[0]:
                    msg += elements[0][0]
                    msg += '<br>'
                if elements[1]:
                    msg += elements[1][0]
                    msg += '<br>'
            self.log.completed = 80
            elements = self.extract_inventions(start_str, end_str)
            if elements:
                msg += elements[0][1]
                msg += '<br>'
                msg += elements[1][1]
                msg += '<br>'
            self.log.completed = 90
            try:
                receivers = self.parameters['receivers']
                if msg:
                    msg = '<!DOCTYPE html><html><body>Estimado/a Sr./Sra.: <br>' + \
                        'Se ha obtenido información que puede ser de su interés.<br><br>' + \
                        msg + '</body><br></html>'
                    self.notify_update(
                        'Se procede a enviar el informe por correo electrónico.')
                    utils = UtilsProcess(
                        self.log.id_schedule, self.log.id, self.id_robot, self.priority, self.log.log_file_path)
                    state = utils.send_email_html(
                        receivers, msg, "RPA: Infome boletín de transferencia.", process=self)

                self.notify_update('Mensaje a enviar: ' + msg)
                if state == "ERROR":
                    self.notify_update(
                        'ERROR al enviar el correo electrónico.')
                    self.log.state = "ERROR"
                else:
                    self.notify_update(
                        'El informe ha sido enviado correctamente por correo electrónico.')

            except:
                self.notify_update(
                    'ERROR: Debe indicar los destinatarios del Informe de Transferencia.')
                self.log.state = "ERROR"

        else:
            self.notify_update(
                'Rango de fechas erróneo. Para la ejecución del proceso la fecha de inicio debe ser menor o igual a la fecha de fin.')
            self.log.state = "ERROR"

        try:
            self.persist_execution(start_date, end_date,
                                   self.log.state != "ERROR")
        except Exception as e:
            print(repr(e))
            self.notify_update(
                'ERROR al persistir los datos de la ejecución del proceso en BBDD.')

        self.log.completed = 100
        self.notify_update(
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
