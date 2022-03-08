import json
from model.process.ProcessExtractXml import ProcessExtractXml
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.ProcessSendMail import ProcessSendMail
import os
import requests
import time
import xml.dom.minidom
from datetime import datetime, timedelta
from pathlib import Path
from model.process.BaseReguladora import BaseReguladora

NAME = "Extract Bases Reguladoras"
DESCRIPTION = "Proceso que extrae las bases reguladoras del BOE seleccionando un rango de fechas y envía los resultados por correo electrónico."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_BASESREGULADORAS.value


class ProcessExtractBasesReguladoras(ProcessCommand):
    boe_url = 'https://boe.es'
    # Incluya la carpeta de destino de su sistema
    destino_local_raiz = 'dest'
    destino_local_xml = '/xml'
    boe_api_sumario = boe_url + '/diario_boe/xml.php?id='
    BOE_ID = 'BOE-S-'
    URL_PERSIST = "http://10.208.99.12:5000/api/orchestrator/register/basesreguladoras"
    URL_UPDATE = "http://10.208.99.12:5000/api/orchestrator/register/basereguladora"
    URL_GET = "http://10.208.99.12:5000/api/orchestrator/register/basesreguladoras?notificada=false"

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, DESCRIPTION, REQUIREMENTS,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def get_bbrrnodes(self, url, id_boe):
        """Obtiene los nodos xml relacionados con las bases reguladoras"""
        params = {}
        params["url"] = url
        params["filename"] = self.destino_local_raiz + \
            self.destino_local_xml + "/" + "index" + id_boe + ".xml"
        entries = ["titulo", "urlPdf"]
        params["nodos"] = {"item": entries}

        psm = ProcessExtractXml(self.log.id_schedule,
                                self.log.id, self.id_robot, "1", None, params)
        psm.add_data_listener(self)
        psm.execute()
        return psm.result

    def item_valido(self, titulo):
        titulo_lower = titulo.lower()
        if ('investigación' in titulo_lower or 'transferencia' in titulo_lower or
            'i+d' in titulo_lower) and (
                ('base reguladora' in titulo_lower or 'bases reguladoras' in titulo_lower) or
                ('regula' in titulo_lower and 'real decreto' in titulo_lower)):
            return True
        return False

    def set_properties(self, bbrr: BaseReguladora, tagName: str, nodo):
        if tagName == 'titulo':
            bbrr.titulo = nodo[0][0].firstChild.data
        if tagName == 'urlPdf':
            bbrr.url = nodo[0][0].firstChild.data
        return bbrr

    def obtener_sumario(self, date):
        result = []
        strDate = date.__str__()
        anio = strDate[:4]
        mes = strDate[5:7]
        dia = strDate[8:10]

        boe_id = self.BOE_ID + anio+mes+dia
        url = self.boe_api_sumario + boe_id

        nodes = self.get_bbrrnodes(url, boe_id)
        if nodes:
            for item in nodes:
                bbrr = BaseReguladora(id_boe=item[0].attributes['id'].value)
                for hijo in item[1]:
                    bbrr = self.set_properties(bbrr, hijo[0][0].tagName, hijo)

                if self.item_valido(bbrr.titulo):
                    result.append(bbrr)

        return result

    def obtener_sumarios(self, start, end):
        date = datetime.strptime(start, "%d/%m/%Y")
        end_date = datetime.strptime(end, "%d/%m/%Y")
        result = []
        if date <= end_date:
            while(date <= end_date):
                entidades = self.obtener_sumario(date)
                if entidades:
                    result = result + entidades
                date = date + timedelta(days=1)
        else:
            self.notificar_actualizacion("Rango de fechas incorrecto.", True)
        return result

    def enviar_email(self, emails, body, subject):
        params = {}
        params["user"] = "epictesting21@gmail.com"
        params["password"] = "epicrobot"
        params["smtp_server"] = "smtp.gmail.com"
        params["receivers"] = []
        for r in emails:
            user = {}
            user["sender"] = "epictesting21@gmail.com"
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

    def persistir_bbrr(self, bbrr: BaseReguladora, notificada: bool):
        if bbrr.id_boe:
            payload = json.dumps(
                [{
                    "id_base": bbrr.id_boe,
                    "titulo": bbrr.get_titulotruncado(),
                    "url": bbrr.get_url(),
                    "notificada": notificada
                }])

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(self.URL_PERSIST, headers=headers, data=payload)
            return response

    def get_noNotificadas(self):
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.get(self.URL_GET, headers)
        result = []
        if response.status_code == 200:
            json_dicti = json.loads(response.text)

            for key in json_dicti:
                if key != "message":
                    bbrr = BaseReguladora(
                        key['id'], key['id_base'], key['titulo'], key['url'])
                    result.append(bbrr)

            if result:
                self.notificar_actualizacion(
                    "No se han obtenido bases reguladoras no enviadas en procesos anteriores.")
        return result

    def end_process(self, state_ugi, state_otri, bbrr_ugi: list, bbrr_otri: list):
        error: bool = False
        msgerror: str = ""

        if state_otri == "ERROR" and state_ugi == "ERROR":
            error = True
            msgerror = "El proceso de Extraer Bases Reguladoras ha finalizado con un error en el envío de los correos electrónicos."

        if state_otri == "ERROR":
            error = True
            msgerror = "El proceso de Extraer Bases Reguladoras ha finalizado con un error en el envío del correo electrónico a la OTRI."
        else:
            self.update_element(bbrr_otri, self.URL_UPDATE, True)

        if state_ugi == "ERROR":
            error = True
            msgerror = "El proceso de Extraer Bases Reguladoras ha finalizado con un error en el envío del correo electrónico a la UGI."
        else:
            self.update_element(bbrr_ugi, self.URL_UPDATE, True)

        if error:
            self.notificar_actualizacion(msgerror)
            self.log.state = "ERROR"
        else:
            self.notificar_actualizacion(
                "El proceso de Extraer Bases reguladoras ha finalizado.")

        self.log.completed = 100
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = pstatus.FINISHED

    def execute(self):
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0

        # 1. obtengo el rango de fechas para extraer las bases reguladoras
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

        self.notificar_actualizacion(
            "El proceso de extracción de bases reguladoras ha comenzado.")
        result = self.obtener_sumarios(start_date, end_date)

        # consulta de las bbrr no notificadas en procesos anteriores
        noNotificadas = self.get_noNotificadas()
        if noNotificadas:
            result = result + noNotificadas

        self.log.completed = 33
        msg_ugi: str = ""
        msg_otri: str = ""
        bbrr_ugi: list = []
        bbrr_otri: list = []
        state_otri: str = ''
        state_ugi: str = ''

        if result:
            # 2. Almacenamos en BBDD

            for bbrr in result:
                urlbase = bbrr.get_url()
                if 'transferencia' in bbrr.titulo:
                    msg_otri += bbrr.id_boe + ': ' + bbrr.titulo + \
                        '\n' + 'url: ' + urlbase + '\n' + '\n'
                    bbrr_otri.append(bbrr)
                else:  # incluye investigación o I+D
                    msg_ugi += bbrr.id_boe + ': ' + bbrr.titulo + \
                        '\n' + 'url: ' + urlbase + '\n' + '\n'
                    bbrr_ugi.append(bbrr)

                response = self.persistir_bbrr(bbrr, False)
                try:
                    if response.text:
                        json_dicti = json.loads(response.text)
                        if json_dicti['status'] == 'ok':
                            bbrr.id = str(json_dicti['BaseReguladora'][0])
                except:
                    self.notificar_actualizacion("Error al obtener el identificador de la base reguladora.")
                

            self.log.completed = 66

            # 3. Enviamos por correo la información obtenida
            self.notificar_actualizacion(
                "Fin de la ejecución de los algoritmos, procedemos a mandar la información por correo electrónico.")

            if msg_otri:
                try:
                    self.notificar_actualizacion("Se han obtenido " + str(len(bbrr_otri)) + " resultados." +
                                                 '\n' + "Resultados enviados a la OTRI:" + '\n' + msg_otri)

                    state_otri = self.enviar_email(self.parameters['receivers_otri'], "Se han obtenido " + str(
                        len(bbrr_otri)) + " resultados." + '\n' + msg_otri, "RPA - Bases Reguladoras obtenidas (OTRI)")
                except:
                    self.notificar_actualizacion(
                        "No se han obtenido bases reguladoras para la OTRI.")
            else:
                self.notificar_actualizacion(
                    "No se han obtenido bases reguladoras para la OTRI.")

            if msg_ugi:
                try:
                    self.notificar_actualizacion("Se han obtenido " + str(len(bbrr_ugi)) + " resultados." +
                                                 '\n' + "Resultados enviados a la UGI:" + '\n' + msg_ugi)
                    state_ugi = self.enviar_email(self.parameters['receivers_ugi'], "Se han obtenido " + str(
                        len(bbrr_ugi)) + " resultados." + '\n' + msg_ugi, "RPA - Bases Reguladoras obtenidas (UGI)")
                except:
                    self.notificar_actualizacion(
                        "No se ha indicado correos electrónicos para enviar a la UGI.")
            else:
                self.notificar_actualizacion(
                    "No se han obtenido bases reguladoras para la UGI.")

        self.end_process(state_ugi, state_otri, bbrr_ugi, bbrr_otri)

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
