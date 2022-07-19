import json
import os
import time
import requests
from datetime import datetime, timedelta
from model.process.ProcessExtractXml import ProcessExtractXml
from model.process.Proceso3.BaseReguladora import BaseReguladora
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.ProcessSendMail import ProcessSendMail

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

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def get_nodes(self, params) -> list:
        psm = ProcessExtractXml(self.log.id_schedule,
                                self.log.id, self.id_robot, "1", None, params)
        #psm.add_data_listener(self)
        #psm.execute()
        url = ''
        if 'url' in params:
            url = params['url']

        filename = params['filename']
        psm.traer_documento(url, filename)
        secciones = psm.obtener_diccionario(filename, 'seccion', 'nombre', ['departamento'])
        departamentos = psm.obtener_diccionario(filename, 'departamento', 'nombre', ['item'])
        items = psm.obtener_diccionario(filename, 'item', 'id', ['titulo', 'urlPdf'])

        if os.path.exists(filename):
            os.remove(filename)

        return [secciones, departamentos, items]

    def get_bbrrnodes(self, url, id_boe) -> list:
        """Obtiene los nodos xml relacionados con las bases reguladoras"""
        params = {}
        params["url"] = url
        params["filename"] = self.destino_local_raiz + \
            self.destino_local_xml + "/" + "index" + id_boe + ".xml"       
        return self.get_nodes(params)

    def item_valido(self, titulo):
        """Comprueba si un item es válido en base a los requisitos establecidos."""
        titulo_lower = titulo.lower()
        if ('investigación' in titulo_lower or 'transferencia' in titulo_lower or
            'i+d' in titulo_lower) and (
                ('base reguladora' in titulo_lower or 'bases reguladoras' in titulo_lower) or
                ('regula' in titulo_lower and 'real decreto' in titulo_lower)):
            return True
        return False

    def process_results(self, nodos) -> list:
        result = []
        if nodos:
            secciones = nodos[0]
            departamentos = nodos[1]
            items = nodos[2]
            if secciones:
                nombre_secciones = secciones.keys()
                ids = []
                for seccion in nombre_secciones:
                    dptos = secciones[seccion]
                    if dptos:
                        for ndpto in dptos:
                            nombre_dpto = ndpto.attributes['nombre'].value
                            if nombre_dpto in departamentos:
                                nitems = departamentos[nombre_dpto]
                                if nitems:
                                    for item in nitems:
                                        id = item.attributes['id'].value
                                        if id in items:                                        
                                            hijos = items[id]
                                            if hijos:
                                                bbrr = BaseReguladora(id_boe=id, seccion = seccion, departamento=nombre_dpto)
                                                for hijo in hijos:
                                                    bbrr.set_properties(hijo.tagName, hijo)
                                                
                                                if self.item_valido(bbrr.titulo) and bbrr.id_boe not in ids:
                                                    result.append(bbrr)
                                                    ids.append(bbrr.id_boe)
        return result


    def get_sumario(self, date:datetime):
        """Obtiene las bases reguladoras del BOE correspondiente"""
        anio = str(date.year)
        mes = str(date.month)
        if date.month < 10:
            mes = '0' + mes
        dia = str(date.day)
        if date.day <10:
            dia = '0' + dia

        boe_id = self.BOE_ID + anio+mes+dia
        url = self.boe_api_sumario + boe_id
        self.notificar_actualizacion('Obteniendo las bases reguladoras de la siguiente url: ' + url)
        
        nodes:list = self.get_bbrrnodes(url, boe_id)
        self.notificar_actualizacion('Comienza el procesamiento de los datos obtenidos.')
        return self.process_results(nodes)

    def get_sumarios(self, start_date, end_date):
        """Obtiene las bases reguladoras a partir de un rango de fechas."""
        result = []
        if start_date <= end_date:
            date = start_date
            while(date <= end_date):
                entidades = self.get_sumario(date)
                if entidades:
                    result = result + entidades
                date = date + timedelta(days=1)
        else:
            self.notificar_actualizacion("Rango de fechas incorrecto.")
        return result

    def send_email(self, emails, body, subject):
        """Función encargada de enviar un correo electrónico."""
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

    def persistir_bbrr(self, bbrr: BaseReguladora, notificada: bool):
        """Función encargada de la persistencia de una base reguladora"""
        if bbrr.id_boe:
            payload = json.dumps(
                [{
                    "id_base": bbrr.id_boe,
                    "titulo": bbrr.get_titulotruncado(),
                    "url": bbrr.url,
                    "notificada": notificada
                }])

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(
                self.URL_PERSIST, headers=headers, data=payload)
            return response

    def get_noNotificadas(self):
        """Función encargada de la obtención de bases reguladoras no notificadas en procesos anteriores."""
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
        """Función que realiza las acciones de finalización del proceso."""
        error: bool = False
        msgerror: str = ""

        if state_otri == "ERROR" and state_ugi == "ERROR":
            error = True
            msgerror = "El proceso de Extraer Bases Reguladoras ha finalizado con un error en el envío de los correos electrónicos."

        if state_otri == "ERROR":
            error = True
            msgerror = "El proceso de Extraer Bases Reguladoras ha finalizado con un error en el envío del correo electrónico a la OTRI."
        else:
            self.update_elements(bbrr_otri, self.URL_UPDATE, True)

        if state_ugi == "ERROR":
            error = True
            msgerror = "El proceso de Extraer Bases Reguladoras ha finalizado con un error en el envío del correo electrónico a la UGI."
        else:
            self.update_elements(bbrr_ugi, self.URL_UPDATE, True)

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

    def msg_bbrr(self, bbrr:BaseReguladora, num:int) -> str:
        if bbrr:
            msg = '<b> BASE REGULADORA Nº ' + \
                        str(num) + '.</b><br>'
            titulo = bbrr.titulo
            if len(bbrr.titulo) > 300:
                titulo = titulo[:300] + '...'
            
            msg += bbrr.id_boe + ': ' + titulo + '<br>'
            msg += 'Sección: ' + bbrr.seccion + '<br>'
            msg += 'Departamento: ' + bbrr.departamento + '<br>'
            msg += 'Url: <a href="' + \
                    bbrr.get_url_absoluta() + '" target="_blank">' + \
                    bbrr.get_url_acortada() + '</a><br>'
            return msg
        return None

    def execute(self):
        """Función encargada de la ejecución del proceso"""
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0

        self.notificar_actualizacion(
            "El proceso de extracción de bases reguladoras ha comenzado.")
        # 1. obtengo el rango de fechas para extraer las bases reguladoras
        dates = self.calculate_dates()
        
        self.notificar_actualizacion(
            "El proceso de obtención de nuevas bases reguladoras ha comenzado.")

        result = self.get_sumarios(dates[0], dates[1])

        if result:
            self.notificar_actualizacion(
                'Se han obtenido ' + str(len(result)) + ' bases reguladoras en total.')
        else:
            self.notificar_actualizacion(
                'No se han obtenido nuevas bases reguladoras según el rango de fechas indicado.')

        self.notificar_actualizacion(
            "El proceso de obtención de nuevas bases reguladoras ha finalizado.")

        # consulta de las bbrr no notificadas en procesos anteriores
        self.notificar_actualizacion(
            "El proceso de extracción de bases reguladoras no notificadas ha comenzado.")
        #noNotificadas = self.get_noNotificadas()
        #if noNotificadas:
            #self.notificar_actualizacion('Se han obtenido ' + str(len(noNotificadas)) + ' bases reguladoras no notificadas.'))
            #result = result + noNotificadas

        self.notificar_actualizacion(
            "El proceso de extracción de bases reguladoras no notificadas ha finalizado.")

        self.log.completed = 33
        msg_ugi: str = ""
        msg_otri: str = ""
        bbrr_ugi: list = []
        bbrr_otri: list = []

        if result:
            msg_num = 'Se han obtenido ' + str(len(result)) + ' bases reguladoras en total.'
            if len(result) == 1:
                msg_num = 'Se ha obtenido 1 base reguladora en total.'

            self.notificar_actualizacion(msg_num)

            # 2. Almacenamos en BBDD
            num_otri = 1
            num_ugi = 1
            for bbrr in result:
                if 'transferencia' in bbrr.titulo:
                    msg = self.msg_bbrr(bbrr, num_otri)
                    if msg:
                        msg_otri += msg
                        num_otri += 1
                        bbrr_otri.append(bbrr)
                else:  # incluye investigación o I+D
                    msg = self.msg_bbrr(bbrr, num_ugi)
                    if msg:
                        msg_ugi += msg
                        num_ugi += 1
                        bbrr_ugi.append(bbrr)

                response = self.persistir_bbrr(bbrr, False)
                try:
                    if response.text:
                        json_dicti = json.loads(response.text)
                        if json_dicti['status'] == 'ok':
                            bbrr.id = str(json_dicti['BaseReguladora'][0])
                except:
                    self.notificar_actualizacion(
                        "Error al obtener el identificador de la base reguladora.")

            self.log.completed = 66

            # 3. Enviamos por correo la información obtenida
            self.notificar_actualizacion(
                "Fin de la ejecución de los algoritmos, procedemos a mandar la información por correo electrónico.")
            
            state_otri: str = ''
            if msg_otri:
                try:
                    msg_num = 'Se ha obtenido 1 base reguladora'
                    if len(bbrr_otri) > 1:
                        msg_num = 'Se han obtenido ' + str(len(bbrr_otri)) + ' bases reguladoras'
                        msg_otri = ' extraídas del BOE que, pueden resultar de su interés:' + '<br><br>' + msg_otri
                    else:
                        msg_otri = ' extraída del BOE que, puede resultar de su interés:' + '<br><br>' + msg_otri

                    self.notificar_actualizacion(msg_num + ' que se enviarán a la OTRI.')

                    msg_otri = 'Estimado/a Sr./Sra.: <br> '+ msg_num + msg_otri                    
                    msg_otri = '<!DOCTYPE html><html><body>' + msg_otri + '<br></body><br></html>'
                    
                    print(msg_otri)

                    state_otri = self.send_email(self.parameters['receivers_otri'], msg_otri,
                                                 "RPA - Bases Reguladoras obtenidas (OTRI)")
                except:
                    self.notificar_actualizacion(
                        "No se han obtenido bases reguladoras para la OTRI.")
            else:
                self.notificar_actualizacion(
                    "No se han obtenido bases reguladoras para la OTRI.")
            
            state_ugi: str = ''
            if msg_ugi:
                try:
                    msg_num = 'Se ha obtenido 1 base reguladora'
                    if len(bbrr_ugi) > 1:
                        msg_num = 'Se han obtenido ' + str(len(bbrr_ugi)) + ' bases reguladoras'
                        msg_ugi = ' extraídas del BOE que, pueden resultar de su interés:' + '<br><br>' + msg_ugi
                    else:
                        msg_ugi = ' extraída del BOE que, puede resultar de su interés:' + '<br><br>' + msg_ugi

                    self.notificar_actualizacion(msg_num + ' que se enviarán a la UGI.')
                    
                    msg_ugi = 'Estimado/a Sr./Sra.: <br> '+ msg_num + msg_ugi                    
                    msg_ugi = '<!DOCTYPE html><html><body>' + msg_ugi + '<br></body><br></html>'
                  
                    print(msg_ugi)

                    state_ugi = self.send_email(self.parameters['receivers_ugi'], msg_ugi,
                                                "RPA - Bases Reguladoras obtenidas (UGI)")
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
