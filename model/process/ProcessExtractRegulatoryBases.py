import json
import os
import time
from datetime import datetime, timedelta
from rpa_robot.ControllerSettings import ControllerSettings
from model.process.Process3.BaseReguladora import RegulatoryBase
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.UtilsProcess import UtilsProcess
from module_cognitive_treelogic.ExtractXML import ExtractXml

NAME = "Extract Bases Reguladoras"
DESCRIPTION = "Proceso que extrae las bases reguladoras del BOE seleccionando un rango de fechas y envía los resultados por correo electrónico."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_REGULATORY_BASES.value
cs = ControllerSettings()


class ProcessExtractRegulatoryBases(ProcessCommand):
    destino_local_xml = 'dest/xml'

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

    def get_nodes(self, params, delete_file: bool = True) -> list:
        """
        Método encargado de obtener los nodos.
        :param params lista de parámetros
        :param delete_file True si es necesario eliminar el fichero xml origen
        :return lista de nodos
        """
        psm = ExtractXml(params)
        url = ''
        if 'url' in params:
            url = params['url']

        filename = params['filename']
        psm.get_document(url, filename)
        secciones = psm.get_dictionary(
            filename, 'seccion', 'nombre', ['departamento'])
        departamentos = psm.get_dictionary(
            filename, 'departamento', 'nombre', ['item'])
        items = psm.get_dictionary(
            filename, 'item', 'id', ['titulo', 'urlPdf'])

        if delete_file and os.path.exists(filename):
            os.remove(filename)

        return [secciones, departamentos, items]

    def get_bbrrnodes(self, url, id_boe) -> list:
        """
        Método que obtiene los nodos xml relacionados con las bases reguladoras
        :param url dirección url de descarga del BOE 
        :param id_boe identificador del BOE
        :return list lista de nodos obtenidos
        """
        params = {}
        params["url"] = url
        params["filename"] = self.destino_local_xml + \
            "/" + "index" + id_boe + ".xml"
        return self.get_nodes(params)

    def is_valid(self, title):
        """
        Comprueba si un item es válido en base a los requisitos establecidos.
        :param title título del item
        :return True si es válido o False si no lo es
        """
        titulo_lower = title.lower()
        if ('investigación' in titulo_lower or 'transferencia' in titulo_lower or
            'i+d' in titulo_lower) and (
                ('base reguladora' in titulo_lower or 'bases reguladoras' in titulo_lower) or
                ('regula' in titulo_lower and 'real decreto' in titulo_lower)):
            return True
        return False

    def process_results(self, nodes) -> list:
        """
        Método encargado de procesas los nodos obtenidos
        :param nodos lista de nodos xml obtenidos
        :return list lista de objetos de tipo BaseReguladora
        """
        result = []
        if nodes:
            sections = nodes[0]
            departaments = nodes[1]
            items = nodes[2]
            if sections:
                section_names = sections.keys()
                ids = []
                for section in section_names:
                    dptos = sections[section]
                    if dptos:
                        for ndpto in dptos:
                            departament_names = ndpto.attributes['nombre'].value
                            if departament_names in departaments:
                                nitems = departaments[departament_names]
                                if nitems:
                                    for item in nitems:
                                        id = item.attributes['id'].value
                                        if id in items:
                                            childrens = items[id]
                                            if childrens:
                                                bbrr = RegulatoryBase(
                                                    id_boe=id, section=section, departament=departament_names)
                                                for hijo in childrens:
                                                    bbrr.set_properties(
                                                        hijo.tagName, hijo)

                                                if self.is_valid(bbrr.title) and bbrr.id_boe not in ids:
                                                    result.append(bbrr)
                                                    ids.append(bbrr.id_boe)
        return result

    def get_summary(self, date: datetime):
        """
        Obtiene las bases reguladoras del BOE correspondiente
        :param date fecha de publicación del BOE que se quiere obtener
        :return lista de bases reguladoras encontradas
        """
        conf = cs.get_process_settings(self.ip_api, self.port_api)
        nodes: list = None
        if 'boe_url' in conf and conf['boe_url']:
            try:
                year = str(date.year)
                month = str(date.month)
                if date.month < 10:
                    month = '0' + month
                day = str(date.day)
                if date.day < 10:
                    day = '0' + day

                boe_id = 'BOE-S-' + year+month+day
                url = conf['boe_url'] + boe_id
                self.notify_update(
                    'Obteniendo las bases reguladoras de la siguiente url: ' + url)
                nodes = self.get_bbrrnodes(url, boe_id)
            except Exception as e:
                self.notify_update(str(e))
                self.notify_update('ERROR en la obtención del BOE con url: ' + url)
        else:
            self.notify_update('ERROR al obtener la url de consulta de BOE')

        self.notify_update('Comienza el procesamiento de los datos obtenidos.')
        return self.process_results(nodes)

    def get_summaries(self, start_date, end_date):
        """
        Método que obtiene las bases reguladoras a partir de un rango de fechas.
        :param start_date fecha de inicio del rango
        :param end_date fecha de fin de rango
        :return list lista de bases reguladoras obtenidas en el rango de fechas seleccionado
        """
        result = []
        if start_date and end_date and start_date <= end_date:
            date: datetime = start_date
            while (date <= end_date):
                entidades = self.get_summary(date)
                if entidades:
                    result = result + entidades
                date = date + timedelta(days=1)
        else:
            self.notify_update("Rango de fechas incorrecto.")
        return result

    def persist_regulatory_base(self, bbrr: RegulatoryBase, notify: bool):
        """
        Método encargado de la persistencia de una base reguladora
        :param bbrr objeto RegulatoryBase que contiene toda la información de una base reguladora
        :param notificada True si ha sido notificada o False si no.
        :return respuesta a la solicitud de persistencia enviada a la base de datos
        """
        if bbrr.id_boe:
            payload = json.dumps(
                [{
                    "id_base": bbrr.id_boe,
                    "titulo": bbrr.get_short_title(),
                    "url": bbrr.url,
                    "seccion": bbrr.section,
                    "departamento": bbrr.departament,
                    "notificada": notify
                }])

            print(payload)

            response = self.rpa.post(self.ip_api+":"+self.port_api + \
                "/api/orchestrator/register/basesreguladoras", payload)
            print(response.text)
            return response

    def get_not_notify(self):
        """
        Método que obtiene las bases reguladoras no notificadas en procesos anteriores.
        :return list lista de bases reguladoras no notificadas
        """
        result = []
        response = self.rpa.get(self.ip_api+":"+self.port_api + \
            "/api/orchestrator/register/basesreguladoras?notificada=false")
        if response and response.status_code == 200:
            json_dicti = json.loads(response.text)

            for key in json_dicti:
                if key != "message":
                    bbrr = RegulatoryBase(
                        key['id'], key['id_base'], key['titulo'], key['url'], key['seccion'], key['departamento'])
                    result.append(bbrr)

        if result:
            self.notify_update(
                "No se han obtenido bases reguladoras no enviadas en procesos anteriores.")
        return result

    def end_process(self, state_ugi, state_otri, bbrr_ugi: list, bbrr_otri: list):
        """
        Método que realiza las acciones de finalización del proceso.
        :param state_ugi código de error de envío de correo electrónico de la UGI
        :param state_otri código de error de envío de correo electrónico de la OTRI
        :param bbrr_ugi bases reguladoras enviadas a la UGI
        :param bbrr_otri bases reguladoras enviadas a la OTRI
        """
        error: bool = False
        msgerror: str = ""

        url_update = self.ip_api + ':'+ self.port_api + "/api/orchestrator/register/basereguladora"

        if state_otri == "ERROR" and state_ugi == "ERROR":
            error = True
            msgerror = "El proceso de Extraer Bases Reguladoras ha finalizado con un error en el envío de los correos electrónicos."

        if state_otri == "ERROR":
            error = True
            msgerror = "El proceso de Extraer Bases Reguladoras ha finalizado con un error en el envío del correo electrónico a la OTRI."
        else:
            self.update_elements(bbrr_otri, url_update, True)

        if state_ugi == "ERROR":
            error = True
            msgerror = "El proceso de Extraer Bases Reguladoras ha finalizado con un error en el envío del correo electrónico a la UGI."
        else:
            self.update_elements(bbrr_ugi, url_update, True)

        if error:
            self.notify_update(msgerror)
            self.log.state = "ERROR"
        else:
            self.notify_update(
                "El proceso de Extraer Bases reguladoras ha finalizado.")

        self.log.completed = 100
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = pstatus.FINISHED

    def msg_bbrr(self, bbrr: RegulatoryBase, num: int) -> str:
        """
        Método que construye el mensaje con la información la base reguladora.
        :param bbrr RegulatoryBase de la que se obtiene la información
        :param num Número que representa la base reguladora en el mensaje
        :return str mensaje 
        """
        if bbrr:
            msg = '<b> BASE REGULADORA Nº ' + \
                str(num) + '.</b><br>'
            title = bbrr.title
            if len(bbrr.title) > 300:
                title = title[:300] + '...'

            msg += bbrr.id_boe + ': ' + title + '<br>'
            msg += 'Sección: ' + bbrr.section + '<br>'
            msg += 'Departamento: ' + bbrr.departament + '<br>'
            msg += 'Url: <a href="' + \
                bbrr.get_absolute_url() + '" target="_blank">' + \
                bbrr.get_short_url() + '</a><br>'
            return msg
        return None

    def execute(self):
        """
        Método encargado de la ejecución del proceso
        """
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0

        self.notify_update(
            "El proceso de extracción de bases reguladoras ha comenzado.")
        dates = self.calculate_dates()

        self.notify_update(
            "El proceso de obtención de nuevas bases reguladoras ha comenzado.")

        result = self.get_summaries(dates[0], dates[1])

        if result:
            self.notify_update(
                'Se han obtenido ' + str(len(result)) + ' bases reguladoras en total.')
        else:
            self.notify_update(
                'No se han obtenido nuevas bases reguladoras según el rango de fechas indicado.')

        self.notify_update(
            "El proceso de obtención de nuevas bases reguladoras ha finalizado.")

        self.notify_update(
            "El proceso de extracción de bases reguladoras no notificadas ha comenzado.")

        not_notify = self.get_not_notify()
        if not_notify:
            self.notify_update(
                'Se han obtenido ' + str(len(not_notify)) + ' bases reguladoras no notificadas.')
            result = result + not_notify

        self.notify_update(
            "El proceso de extracción de bases reguladoras no notificadas ha finalizado.")

        self.log.completed = 33
        state_otri: str = ''
        state_ugi: str = ''
        msg_ugi: str = ""
        msg_otri: str = ""
        bbrr_ugi: list = []
        bbrr_otri: list = []

        if result:
            msg_num = 'Se han obtenido ' + \
                str(len(result)) + ' bases reguladoras en total.'
            if len(result) == 1:
                msg_num = 'Se ha obtenido 1 base reguladora en total.'

            self.notify_update(msg_num)

            num_otri = 1
            num_ugi = 1
            for bbrr in result:
                if 'transferencia' in bbrr.title:
                    msg = self.msg_bbrr(bbrr, num_otri)
                    if msg:
                        msg_otri += msg
                        num_otri += 1
                        bbrr_otri.append(bbrr)
                else:
                    msg = self.msg_bbrr(bbrr, num_ugi)
                    if msg:
                        msg_ugi += msg
                        num_ugi += 1
                        bbrr_ugi.append(bbrr)

                response = self.persist_regulatory_base(bbrr, True)
                try:
                    if response.text:
                        json_dicti = json.loads(response.text)
                        if json_dicti['status'] == 'ok':
                            bbrr.id = str(json_dicti['BaseReguladora'][0])
                except:
                    self.notify_update(
                        "Error al obtener el identificador de la base reguladora.")

            self.log.completed = 66

            self.notify_update(
                "Fin de la ejecución de los algoritmos, procedemos a mandar la información por correo electrónico.")

            if msg_otri:
                try:
                    msg_num = 'Se ha obtenido 1 base reguladora'
                    if len(bbrr_otri) > 1:
                        msg_num = 'Se han obtenido ' + \
                            str(len(bbrr_otri)) + ' bases reguladoras'
                        msg_otri = ' extraídas del BOE que, pueden resultar de su interés:' + '<br><br>' + msg_otri
                    else:
                        msg_otri = ' extraída del BOE que, puede resultar de su interés:' + '<br><br>' + msg_otri

                    self.notify_update(msg_num + ' que se enviarán a la OTRI.')

                    msg_otri = 'Estimado/a Sr./Sra.: <br> ' + msg_num + msg_otri
                    msg_otri = '<!DOCTYPE html><html><body>' + msg_otri + '<br></body><br></html>'

                    self.notify_update(msg_otri)
                    utils = UtilsProcess(
                        self.log.id_schedule, self.log.id, self.id_robot, self.priority, self.log.log_file_path)
                    state_otri = utils.send_email_html(self.parameters['receivers_otri'], msg_otri,
                                                       "RPA - Bases Reguladoras obtenidas (OTRI)", process=self)
                except:
                    self.notify_update(
                        "No se han obtenido bases reguladoras para la OTRI.")
            else:
                self.notify_update(
                    "No se han obtenido bases reguladoras para la OTRI.")

            if msg_ugi:
                try:
                    msg_num = 'Se ha obtenido 1 base reguladora'
                    if len(bbrr_ugi) > 1:
                        msg_num = 'Se han obtenido ' + \
                            str(len(bbrr_ugi)) + ' bases reguladoras'
                        msg_ugi = ' extraídas del BOE que, pueden resultar de su interés:' + '<br><br>' + msg_ugi
                    else:
                        msg_ugi = ' extraída del BOE que, puede resultar de su interés:' + '<br><br>' + msg_ugi

                    self.notify_update(msg_num + ' que se enviarán a la UGI.')

                    msg_ugi = 'Estimado/a Sr./Sra.: <br> ' + msg_num + msg_ugi
                    msg_ugi = '<!DOCTYPE html><html><body>' + msg_ugi + '<br></body><br></html>'

                    self.notify_update(msg_ugi)
                    utils = UtilsProcess(
                        self.log.id_schedule, self.log.id, self.id_robot, self.priority, self.log.log_file_path)
                    state_ugi = utils.send_email_html(self.parameters['receivers_ugi'], msg_ugi,
                                                      "RPA - Bases Reguladoras obtenidas (UGI)", process=self)
                except:
                    self.notify_update(
                        "No se ha indicado correos electrónicos para enviar a la UGI.")
            else:
                self.notify_update(
                    "No se han obtenido bases reguladoras para la UGI.")

        self.end_process(state_ugi, state_otri, bbrr_ugi, bbrr_otri)

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
