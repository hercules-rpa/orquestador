from model.process.Proceso3.Modelo_Ejecucion import Modelo_Ejecucion
from model.process.Proceso3.Adaptador_BDNS import Adaptador_BDNS
from model.process.Proceso3.Adaptador_Caixa import Adaptador_Caixa
from model.process.Proceso3.Adaptador_Europa import Adaptador_Europa
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.ProcessSendMail import ProcessSendMail
from model.SGI import SGI

import datetime
import time
import requests
import json

NAME            = "Extract Convocatorias"
DESCRIPTION     = "Proceso que extrae las últimas convocatorias de las fuentes de datos dadas"
REQUIREMENTS    = ['rpaframework','playwright','selenium','bs4']
ID              = ProcessID.EXTRACT_CONVOCATORIA.value
        

class ProcessExtractConvocatoria(ProcessCommand):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, REQUIREMENTS, DESCRIPTION, id_schedule, id_log,id_robot, priority, log_file_path, parameters)    
    
    def execute(self):
        """
        Ejecución del subproceso búsqueda de convocatorias BDNS, CAIXA y Europa H2020.
        """
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        self.log.start_log(time.time())
        emails = self.parameters['receivers']
        self.update_log("El proceso de extracción de convocatorias ha empezado", True)
        self.log.completed = 0 

        body = {}
        resources = []
        librerias = []
        adapter_bdns = Adaptador_BDNS()
        librerias.append(adapter_bdns)
        adapter_caixa = Adaptador_Caixa()
        librerias.append(adapter_caixa)
        adapter_europa = Adaptador_Europa()
        librerias.append(adapter_europa)
        if 'bdns' in self.parameters.keys():
            self.update_log("Detectamos que el proceso quiere buscar directamente una BDNS. Comprobamos primero si está en BBDD.", True)
            bbdd_url ="http://10.208.99.12:5000/api/orchestrator/register/convocatoria?url=https://www.pap.hacienda.gob.es/bdnstrans/GE/es/convocatoria/" + self.parameters['bdns']
            response = requests.get(bbdd_url)
            if response.ok:
                self.update_log("La convocatoria está en nuestra base de datos", True)
            #Esta parte es competencia del subproceso extraer concesiones
            self.update_log("Extraemos la información ampliada de la convocatoria con número: " + self.parameters['bdns'] + ' y descargamos sus recursos (pdf).', True)
            try:
                self.update_log(str(adapter_bdns.ampliar_info(self.parameters['bdns'])))
                resources = adapter_bdns.buscar_recursos(self.parameters['bdns'])
            except:
                self.update_log("Error al obtener los datos de la convocatoria con BDNS número: " + self.parameters['bdns'])
        else:  
            for item in librerias:
                if 'search' in self.parameters.keys():
                    try:
                        if 'start_date' in self.parameters.keys() and 'end_date' in self.parameters.keys():
                            self.update_log("Buscamos la convocatoria por las fechas indicadas: desde " + self.parameters['start_date'] + " hasta " + self.parameters['end_date'] + " con las palabras claves = " + self.parameters['search'] + ". ", True)
                            item.buscar_fecha(self.parameters['start_date'], self.parameters['end_date'], self.parameters['search'])
                        else:
                            self.update_log("Buscamos la convocatoria diaria", True)
                            item.buscar(self.parameters['search'])
                        if type(item).__name__ == "Adaptador_Europa":
                            body = item.notify()
                        else:
                            self.update_log(item.notify(),True)
                    except:
                        self.update_log("Error en la ejecución del subproceso " + type(item).__name__ + " ", True)
                else:
                    try:
                        if 'start_date' in self.parameters.keys() and 'end_date' in self.parameters.keys():
                            self.update_log("Buscamos la convocatoria por las fechas indicadas: desde " + self.parameters['start_date'] + " hasta " + self.parameters['end_date'] + ". ", True)
                            item.buscar_fecha(self.parameters['start_date'], self.parameters['end_date'])
                        else:
                            self.update_log("Buscamos la convocatoria diaria", True)
                            item.buscar()
                        if type(item).__name__ == "Adaptador_Europa":
                            body = item.notify()
                        else:
                            self.update_log(item.notify(),True)
                    except:
                        self.update_log("Error en la ejecución del subproceso " + type(item).__name__ + " ", True)
            #Inyectamos los datos en el SGI
            self.inyect_sgi("BDNS")
            self.inyect_sgi("CAIXA")
            message =  "Este mensaje se ha generado automáticamente:\n\n\n" + '\n' + str(body) #+ '\n\n Y estas son las que no han sido notificadas' + str(notificada)
            self.update_log("Mensaje que enviamos por correo" + message, True)
            self.update_log("Fin de la ejecución de la extracción, mandamos por correo los resultados", True)

            params = {}
            params["user"] = "epictesting21@gmail.com"
            params["password"] = "epicrobot"
            params["smtp_server"] = "smtp.gmail.com"
            params["receivers"]= []
            for r in emails:
                user={}
                user["sender"] = "epictesting21@gmail.com"
                user["receiver"]= r['receiver']
                user["subject"]="Convocatorias encontradas. RPA"
                user["body"]= message
                self.update_log(message, True)
                user["attached"]= resources
                params["receivers"].append(user)
            psm = ProcessSendMail(self.log.id_schedule, self.log.id,self.id_robot, "1", None, params)
            psm.add_data_listener(self)
            psm.execute()
            if psm.log.state == "ERROR":
                self.update_log("Login error", True)
                self.update_log("No se han enviado las convocatorias europeas al email correspondiente. ", True)
                self.log.state = "ERROR"
                self.log.completed = 100
                self.log.end_log(time.time())
                return
            if psm.log.state == "OK":
                adapter_europa.cambio_notificadas()
        
        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED

    def inyect_sgi(self, grupo: str) -> None:
        """
        Método para la inyección de convocatorias en el sistema SGI que no estén marcadas como inyectadas en la base de datos interna.

        :param grupo str: Cadena de caracteres que especifica qué tipo de convocatorias se quieren inyectar en el sistema SGI: BDNS (Base de datos nacional de subvenciones), CAIXA (Fundación la Caixa).
        :return None: Esta función no devuelve nada.
        """
        sgi = SGI()
        url = "http://10.208.99.12:5000/api/orchestrator/register/convocatorias?notificada=false&_from=" + grupo
        response = requests.get(url)
        if response.ok:
            self.update_log("Encontramos que hay una colección de la " + grupo + " para inyectar en el SGI.", True)
            for item in json.loads(response.text):
                insert = {}
                if item['unidad_gestion'] == "OTRI":
                    insert['unidadGestionRef'] = 1
                else:
                    insert['unidadGestionRef'] = 3
                insert['titulo'] = "ROBOT " + item['titulo']
                insert['formularioSolicitud'] = 'PROYECTO'
                if item['modelo_ejecucion'] == Modelo_Ejecucion.FACTURACION.value:
                    insert['modeloEjecucion'] = { "id":2 }
                elif item['modelo_ejecucion'] == Modelo_Ejecucion.PRESTAMO.value:
                    insert['modeloEjecucion'] = { "id":4 }
                else:
                    insert['modeloEjecucion'] = { "id":1 }
                insert['fechaProvisional'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                insert['observaciones'] = item['entidad_convocante'] + ' ' + item['entidad_gestora']
                try:
                    res = sgi.post_convocatoria(json.dumps(insert))
                    self.update_log("Inyectamos convocatoria en el SGI", True)
                except Exception as e:
                    self.update_log("No se ha podido inyectar en el SGI la convocatoria del " + grupo + " con título: " + item['titulo'])
                if res:
                    headers = {'Content-Type': 'application/json'}
                    url_update = "http://10.208.99.12:5000/api/orchestrator/register/convocatoria/" + str(item['id'])
                    requests.patch(url_update, headers=headers, data='{"notificada":true, "id_sgi":' + str(json.loads(res.text)['id']) + '}')
                    self.update_log("Actualizamos nuestra base de datos con la notificación", True)
                    res_entidad_convocante = sgi.get_empresas("nombre=ik=\"" + item['entidad_gestora'] + "\"")
                    if res_entidad_convocante != "":
                        try:
                            body = {"convocatoriaId": json.loads(res)['id'],"entidadRef": str(json.loads(res_entidad_convocante)[0]['id'])}
                            sgi.post_entidadconvocante_convocatoria(json.dumps(body))
                            sgi.post_entidadfinanciadora_convocatoria(json.dumps(body))
                            self.update_log("Insertamos entidad convocante y financiadora en la convocatoria del SGI", True)
                        except Exception as e:
                            self.update_log("No se ha podido establecer las entidades convocantes/financiadoras en el SGI de la convocatoria, se adjuntarán en el campo de observaciones: " + json.loads(res)['titulo'] + ". Error: " + str(e) + "\n -- RESPONSE POST CONVOCATORIA: " + str(res) + "\n -- ENTRADA BASE DE DATOS: " + str(item), True)
            self.update_log("Finalización de las insercciones de " + grupo, True)
        else:
            self.update_log("No hay una colección de " + grupo + " que insertar en el SGI", True)

    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass
