from model.process.Proceso3.Adaptador_BDNS import Adaptador_BDNS
from model.process.Proceso3.Adaptador_Caixa import Adaptador_Caixa
from model.process.Proceso3.Adaptador_Europa import Adaptador_Europa
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.ProcessSendMail import ProcessSendMail

import time
import requests
import json

NAME            = "Extract Convocatorias"
DESCRIPTION     = "Proceso que extrae las últimas convocatorias de las fuentes de datos dadas"
REQUIREMENTS    = ['rpaframework','playwright','selenium','bs4']
ID              = ProcessID.EXTRACT_CONVOCATORIA.value
        

class ProcessExtractConvocatoria(ProcessCommand):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log,id_robot, priority, log_file_path, parameters)    
    
    def execute(self):
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        self.log.start_log(time.time())
        emails = self.parameters['receivers']
        self.update_log("El proceso de extracción de convocatorias ha empezado", True)
        self.log.completed = 0 

        body = {}
        notificada_europa = {}
        resources = []
        librerias = []
        bbdd_url = "http://10.208.99.12:5000/api/orchestrator/register/convocatorias?notificada=false&_from=EUROPA2020"
        response = requests.get(bbdd_url)
        if response.ok:
            notificada_europa = json.loads(response.content)
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
            else:
                #Esta parte es competencia del subproceso extraer concesiones
                self.update_log("Extraemos la información ampliada de la convocatoria con número: " + self.parameters['bdns'] + ' y descargamos sus recursos (pdf).', True)
                self.update_log(adapter_bdns.ampliar_info(self.parameters['bdns']))
                resources = adapter_bdns.buscar_recursos(self.parameters['bdns'])
        else:  
            for item in librerias:
                if 'busqueda' in self.parameters.keys():
                    try:
                        if 'fecha-desde' in self.parameters.keys() and 'fecha-hasta' in self.parameters.keys():
                            self.update_log("Buscamos la convocatoria por las fechas indicadas: desde " + self.parameters['fecha-desde'] + " hasta " + self.parameters['fecha-hasta'] + " con las palabras claves = " + self.parameters['busqueda'] + ". ", True)
                            item.buscar_fecha(self.parameters['fecha-desde'], self.parameters['fecha-hasta'], self.parameters['busqueda'])
                        else:
                            self.update_log("Buscamos la convocatoria diaria", True)
                            item.buscar()
                        if type(item).__name__ == "Adaptador_Europa":
                            aux = item.notify()
                            body = aux.split("Número")[1]
                            for item in notificada_europa:
                                if item['url'] not in body:
                                    print(item)
                                    body += "\n\nConvocatoria con nombre: " + item['titulo'] + "\n\t URL: " + item['url'] + ". \n\t Fecha de publicación: " + time.strftime('%d/%m/%Y', time.localtime(item['fecha_publicacion'])) + ". \n\t Fecha Fin: " + time.strftime('%d/%m/%Y', time.localtime(item['fecha_creacion']))
                            self.update_log("Convocatorias Europa: " + aux.split("Número")[0], True)
                        else:
                            self.update_log(item.notify(),True)
                    except:
                        self.update_log("Error en la ejecución del subproceso " + type(item).__name__ + " ", True)
                else:
                    try:
                        if 'fecha-desde' in self.parameters.keys() and 'fecha-hasta' in self.parameters.keys():
                            self.update_log("Buscamos la convocatoria por las fechas indicadas: desde " + self.parameters['fecha-desde'] + " hasta " + self.parameters['fecha-hasta'] + ". ", True)
                            item.buscar_fecha(self.parameters['fecha-desde'], self.parameters['fecha-hasta'])
                        else:
                            self.update_log("Buscamos la convocatoria diaria", True)
                            item.buscar()
                        if type(item).__name__ == "Adaptador_Europa":
                            aux = item.notify()
                            body = aux.split("Número")[1]                            
                            for item in notificada_europa:
                                if item['url'] not in body:
                                    print(item)
                                    body += "\n\nConvocatoria con nombre: " + item['titulo'] + "\n\t URL: " + item['url'] + ". \n\t Fecha de publicación: " + time.strftime('%d/%m/%Y', time.localtime(item['fecha_publicacion'])) + ". \n\t Fecha Fin: " + time.strftime('%d/%m/%Y', time.localtime(item['fecha_creacion']))
                            self.update_log("Convocatorias Europa: " + aux.split("Número")[0],True)
                        else:
                            self.update_log(item.notify(),True)
                    except:
                        self.update_log("Error en la ejecución del subproceso " + type(item).__name__ + " ", True)
                
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


    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass

