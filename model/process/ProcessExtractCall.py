from rpa_robot.ControllerSettings import ControllerSettings
from model.process.Process3.Execution_Model import Execution_Model
from model.process.Process3.Adapter_BDNS import Adapter_BDNS
from model.process.Process3.Adapter_Europe import Adapter_Europe
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.UtilsProcess import UtilsProcess

import datetime
import time
import requests
import json

NAME = "Extract Convocatorias"
DESCRIPTION = "Proceso que extrae las últimas convocatorias de las fuentes de datos dadas"
REQUIREMENTS = ['rpaframework', 'playwright', 'selenium', 'bs4']
ID = ProcessID.EXTRACT_CALLS.value
cs = ControllerSettings()


class ProcessExtractCall(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None, ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION, id_schedule,
                                id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

    def execute(self):
        """
        Ejecución del subproceso búsqueda de convocatorias BDNS, CAIXA y Europa H2020.
        """
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        self.log.start_log(time.time())
        emails = self.parameters['receivers']
        self.update_log(
            "El proceso de extracción de convocatorias ha empezado", True)
        self.log.completed = 0

        body = {}
        resources = []
        library = []
        adapter_bdns = Adapter_BDNS(self.ip_api, self.port_api)
        library.append(adapter_bdns)
        adapter_europe = Adapter_Europe(self.ip_api, self.port_api)
        library.append(adapter_europe)

        if 'bdns' in self.parameters.keys():
            self.update_log(
                "Detectamos que el proceso quiere buscar directamente una BDNS. Comprobamos primero si está en BBDD.", True)
            if self.ip_api and self.port_api:
                bbdd_url = "http://" + self.ip_api + ":" + self.port_api + \
                    "/api/orchestrator/register/convocatoria?url=https://www.pap.hacienda.gob.es/bdnstrans/GE/es/convocatoria/" + \
                    self.parameters['bdns']
                response = requests.get(bbdd_url)
                if response.ok:
                    self.update_log(
                        "La convocatoria está en nuestra base de datos", True)
                # Esta parte es competencia del subproceso extraer concesiones
                self.update_log("Extraemos la información ampliada de la convocatoria con número: " +
                                self.parameters['bdns'] + ' y descargamos sus recursos (pdf).', True)
                try:
                    self.update_log(
                        str(adapter_bdns.expand_info(self.parameters['bdns'])))
                    resources = adapter_bdns.obtain_resources(
                        self.parameters['bdns'])
                except:
                    self.update_log(
                        "Error al obtener los datos de la convocatoria con BDNS número: " + self.parameters['bdns'], True)
            else:
                self.update_log(
                    "ERROR no ha sido posible consultar si existe en base de datos.", True)
        else:
            for item in library:
                if 'search' in self.parameters.keys():
                    try:
                        if 'start_date' in self.parameters.keys() and 'end_date' in self.parameters.keys():
                            self.update_log("Buscamos la convocatoria por las fechas indicadas: desde " +
                                            self.parameters['start_date'] + " hasta " + self.parameters['end_date'] + " con las palabras claves = " + self.parameters['search'] + ". ", True)
                            item.search_date(
                                self.parameters['start_date'], self.parameters['end_date'], self.parameters['search'])
                        else:
                            self.update_log(
                                "Buscamos la convocatoria diaria", True)
                            item.search(self.parameters['search'])
                        if type(item).__name__ == "Adapter_Europe":
                            body = item.notify()
                        else:
                            self.update_log(item.notify(), True)
                    except:
                        self.update_log(
                            "Error en la ejecución del subproceso " + type(item).__name__ + " ", True)
                else:
                    try:
                        if 'start_date' in self.parameters.keys() and 'end_date' in self.parameters.keys():
                            self.update_log("Buscamos la convocatoria por las fechas indicadas: desde " +
                                            self.parameters['start_date'] + " hasta " + self.parameters['end_date'] + ". ", True)
                            item.search_date(
                                self.parameters['start_date'], self.parameters['end_date'])
                        else:
                            self.update_log(
                                "Buscamos la convocatoria diaria", True)
                            item.search()
                        if type(item).__name__ == "Adapter_Europe":
                            body = item.notify()
                        else:
                            self.update_log(item.notify(), True)
                    except:
                        self.update_log(
                            "Error en la ejecución del subproceso " + type(item).__name__ + " ", True)

            # Inyectamos los datos en el SGI
            self.inyect_sgi()
            message = "Este mensaje se ha generado automáticamente:\n\n\n" + \
                '\n' + str(body)
            self.update_log("Fin de la ejecución de la extracción, mandamos por correo los resultados", True)
            utils = UtilsProcess(self.log.id_schedule, self.log.id,
                                 self.id_robot, self.priority, self.log.log_file_path)
            state = utils.send_email(
                emails, message, "Convocatorias encontradas. RPA", resources, self)

            if state == "ERROR":
                self.update_log("Login error", True)
                self.update_log(
                    "No se han enviado las convocatorias europeas al email correspondiente. ", True)
                self.log.state = "ERROR"
                self.log.completed = 100
                self.log.end_log(time.time())
                return
            elif state == "OK":
                adapter_europe.change_notify()

        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED

    def inyect_sgi(self):
        """
        Método para la inyección de convocatorias en el sistema SGI que no estén marcadas como inyectadas en la base de datos interna.
        """
        url = "http://" + self.ip_api + ":" + self.port_api + \
            "/api/orchestrator/register/convocatorias?notificada=false&_from=BDNS"
        response = requests.get(url)
        if response.ok:
            self.update_log("Encontramos que hay una colección de la BDNS para inyectar en el SGI.", True)
            sgi = cs.get_sgi(self.ip_api, self.port_api)
            for item in json.loads(response.text):
                insert = {}
                if item['unidad_gestion'] == "OTRI":
                    insert['unidadGestionRef'] = 1
                else:
                    insert['unidadGestionRef'] = 3
                insert['titulo'] = "ROBOT " + item['titulo']
                insert['formularioSolicitud'] = 'PROYECTO'
                if item['modelo_ejecucion'] == Execution_Model.FACTURACION.value:
                    insert['modeloEjecucion'] = {"id": 2}
                elif item['modelo_ejecucion'] == Execution_Model.PRESTAMO.value:
                    insert['modeloEjecucion'] = {"id": 4}
                else:
                    insert['modeloEjecucion'] = {"id": 1}
                insert['fechaProvisional'] = datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%SZ")
                insert['observaciones'] = item['entidad_convocante'] + \
                    ' ' + item['entidad_gestora']
                try:
                    if sgi:
                        res = sgi.post_announcement(json.dumps(insert))
                        self.update_log(
                            "Inyectamos convocatoria en el SGI", True)
                    else:
                        self.update_log(
                            "No ha sido posible inyectar la convocatiria en Hércules-SGI.")
                except Exception as e:
                    self.update_log(
                        "No se ha podido inyectar en el SGI la convocatoria de la BDNS con título: " + item['titulo'])

                if res:
                    headers = {'Content-Type': 'application/json'}
                    url_update = "http://" + \
                        self.ip_api + ":" + self.port_api + \
                        "/api/orchestrator/register/convocatoria/" + \
                        str(item['id'])
                    requests.patch(
                        url_update, headers=headers, data='{"notificada":true, "id_sgi":' + str(json.loads(res)['id']) + '}')
                    self.update_log(
                        "Actualizamos nuestra base de datos con la notificación", True)

                    if sgi:
                        res_converter_announcement = sgi.get_companies(
                            "nombre=ik=\"" + item['entidad_gestora'] + "\"")
                        if res_converter_announcement != "":
                            try:
                                body = {"convocatoriaId": json.loads(res)['id'], "entidadRef": str(
                                    json.loads(res_converter_announcement)[0]['id'])}
                                sgi.post_convener_announcement(
                                    json.dumps(body))
                                sgi.post_financing_entity_announcement(
                                    json.dumps(body))
                                self.update_log(
                                    "Insertamos entidad convocante y financiadora en la convocatoria del SGI", True)
                            except Exception as e:
                                self.update_log("No se ha podido establecer las entidades convocantes/financiadoras en el SGI de la convocatoria, se adjuntarán en el campo de observaciones: " + json.loads(
                                    res)['titulo'] + ". Error: " + str(e) + "\n -- RESPONSE POST CONVOCATORIA: " + str(res) + "\n -- ENTRADA BASE DE DATOS: " + str(item), True)
                    else:
                        self.update_log(
                            "ERROR No ha sido posible insertar la entidad convocante y financiadora en la convocatoria de Hércules-SGI", True)

            self.update_log(
                "Finalización de las insercciones de BDNS", True)
        else:
            self.update_log("No hay una colección de BDNS que insertar en el SGI", True)

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
