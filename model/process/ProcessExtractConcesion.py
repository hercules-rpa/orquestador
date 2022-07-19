from model.process.Proceso3.Adaptador_BDNS import Adaptador_BDNS
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.ProcessExtractInfoPDF import ProcessExtractInfoPDF
from model.process.ProcessSendMail       import ProcessSendMail
from model.SGI import SGI

import time
import requests
import json

NAME            = "Extract Convocatorias"
DESCRIPTION     = "Proceso que extrae las últimas convocatorias de las fuentes de datos dadas"
REQUIREMENTS    = ['rpaframework','playwright','selenium','bs4']
ID              = ProcessID.EXTRACT_CONVOCATORIA.value
SERVIDOR        = "10.208.99.12"

class ProcessExtractConcesion(ProcessCommand):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, REQUIREMENTS, DESCRIPTION, id_schedule, id_log,id_robot, priority, log_file_path, parameters)    
    
    def execute(self):
        """
        Ejecución del subproceso de extracción de una concesión.
        """
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        self.log.start_log(time.time())
        self.update_log("El proceso de extracción de concesiones ha empezado", True)
        self.log.completed = 0


        list_concesiones = {}
        param_info_pdf = {}
        adaptador_bdns = Adaptador_BDNS()
        sgi = SGI()
        #list_concesiones = [{'createdBy': '00391433', 'creationDate': '2022-05-05T09:02:28.475Z', 'lastModifiedBy': '00391433', 'lastModifiedDate': '2022-05-05T09:04:35.943Z', 'id': 23, 'titulo': '', 'convocatoriaId': 35, 'codigoExterno': '', 'codigoRegistroInterno': 'SGI_SLC2320220505', 'estado': {'createdBy': '00391433', 'creationDate': '2022-05-05T09:04:35.941Z', 'lastModifiedBy': '00391433', 'lastModifiedDate': '2022-05-05T09:04:35.941Z', 'id': 47, 'solicitudId': 23, 'estado': 'SOLICITADA', 'fechaEstado': '2022-05-05T09:02:37.084Z', 'comentario': ''}, 'creadorRef': '00391433', 'solicitanteRef': '28710458', 'observaciones': '', 'convocatoriaExterna': '', 'unidadGestionRef': '3', 'formularioSolicitud': 'PROYECTO', 'tipoSolicitudGrupo': None, 'activo': True},{"createdBy":"00391433","creationDate":"2022-05-09T14:20:32.068Z","lastModifiedBy":"00391433","lastModifiedDate":"2022-05-09T14:20:57.238Z","id":25,"titulo":"","convocatoriaId":35,"codigoExterno":"","codigoRegistroInterno":"SGI_SLC2520220509","estado":{"createdBy":"00391433","creationDate":"2022-05-09T14:20:57.238Z","lastModifiedBy":"00391433","lastModifiedDate":"2022-05-09T14:20:57.238Z","id":52,"solicitudId":25,"estado":"SOLICITADA","fechaEstado":"2022-05-09T14:20:42.496Z","comentario":""},"creadorRef":"00391433","solicitanteRef":"48495234","observaciones":"","convocatoriaExterna":"","unidadGestionRef":"3","formularioSolicitud":"PROYECTO","tipoSolicitudGrupo":None,"activo":True}]
        list_concesiones = self.get_solicitudes_validas(solicitudes=sgi.get_solicitudes("convocatoriaId==35")) #[{'createdBy': '00391433', 'creationDate': '2022-05-09T14:20:32.068Z', 'lastModifiedBy': '00391433', 'lastModifiedDate': '2022-05-09T14:20:57.238Z', 'id': 25, 'titulo': '', 'convocatoriaId': 35, 'codigoExterno': '', 'codigoRegistroInterno': 'SGI_SLC2520220509', 'estado': {'createdBy': '00391433', 'creationDate': '2022-05-09T14:20:57.238Z', 'lastModifiedBy': '00391433', 'lastModifiedDate': '2022-05-09T14:20:57.238Z', 'id': 52, 'solicitudId': 25, 'estado': 'SOLICITADA', 'fechaEstado': '2022-05-09T14:20:42.496Z', 'comentario': ''}, 'creadorRef': '00391433', 'solicitanteRef': '48495234', 'observaciones': '', 'convocatoriaExterna': '', 'unidadGestionRef': '3', 'formularioSolicitud': 'PROYECTO', 'tipoSolicitudGrupo': None, 'activo': True}]
        self.update_log("Lista de concesiones: " + str(list_concesiones), True)
        list_solicitantes = self.get_solicitantes(list_concesiones, sgi)
        self.update_log("Lista de solicitantes: " + str(list_solicitantes), True)
        if len(list_concesiones) > 0:
            for item in list_concesiones:
                self.log.completed += 100/len(list_concesiones)
                BDNS_NUM = self.get_bdns(item['convocatoriaId'])
                self.update_log("Número de la BDNS: " + str(BDNS_NUM), True)
                #Buscamos la solicitudes que hay.
                if BDNS_NUM:
                    self.update_log("Empezamos con la convocatoria BDNS: "+ str(BDNS_NUM), True)
                    param_info_pdf['paths'] = adaptador_bdns.buscar_recursos(BDNS_NUM) #devuelve un array["hercules-rpa/rpa_robot/files/525644_Convocatoria ayudas contratos predoctorales 2020","hercules-rpa/rpa_robot/files/525644_PRE2020_RC_ModificacionRC_CambiosCentros_Firmada","hercules-rpa/rpa_robot/files/525644_PRE2020_SegundaRC_Art20_3_abc_Firmada525644_PRE2020_TerceraRC_Art20_4_Firmada","hercules-rpa/rpa_robot/files/525644_resolucion ampliacion plazo concesion PRE2020","hercules-rpa/rpa_robot/files/525644_Resolucion_Concesion_PREDOC2020_firmada(2)"] 
                    nif_array = []
                    for nif in self.parameters['nif_universidad']:
                        nif_array.append(nif['nif'])
                    param_info_pdf['nif_universidad'] = nif_array
                    param_info_pdf['solicitudes'] = list_solicitantes #{'PID2020-113723RB-C22':'ANTONIO FERNANDO SKARMETA GOMEZ', 'PID2019-105684RB-I00':'SAGER LA GANGA'} item['codigoExterno'] #devolverá un array de solicitudes ['PID-12312','PID-323559'] 
                    pExtractPdf = ProcessExtractInfoPDF(self.log.id_schedule, self.log.id, self.id_robot, "1", None, param_info_pdf)
                    pExtractPdf.add_data_listener(self)
                    pExtractPdf.execute()
                    if pExtractPdf.result:
                        self.update_log("Enviamos la información obtenida de la concesión "+ str(item['codigoRegistroInterno']), True)
                        """state = self.send_mail(str(BDNS_NUM), pExtractPdf.result, self.parameters['emails'])
                        if state =="ERROR":
                            self.log.completed = 100
                            self.state = pstatus.FINISHED
                            self.update_log("Error enviando el correo. Proceso finalizado. ",True)
                            self.log.state = "ERROR"
                            self.log.end_log(time.time())
                            return
                        """
                else:
                    self.update_log("No se ha encontrado ninguna información que el robot haya sido capaz de inferir de la concesión ", True)
        else:
            self.log.update_log("No hay concesiones que tengan un estado distinto a: BORRADOR, CONCEDIDA, DENEGADA, DESISTIDA ó EXCLUIDA", True)

        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED

    def get_solicitudes_validas(self, solicitudes: str) -> list:
        """
        Método para seleccionar de las solicitudes recogidas por el SGI las que cumplan las condiciones de no estar en estado borrador, concedida, denegada, desistida ó excluida.

        :param solicitudes str: Solicitudes en formato JSON a analizar.
        :return list Lista de solicitudes tratadas que cumplen el criterio.
        """
        list_concesiones = []
        if solicitudes:
            for solicitud in json.loads(solicitudes):
                if solicitud['estado']['estado'] != "BORRADOR" and solicitud['estado']['estado'] != "CONCEDIDA" and solicitud['estado']['estado'] != "DENEGADA" and solicitud['estado']['estado'] != "DESISTIDA" and solicitud['estado']['estado'] != "EXCLUIDA":
                    list_concesiones.append(solicitud)
        return list_concesiones

    def get_solicitantes(self, solicitudes: str, sgi: SGI) -> list:
        """
        Método para recuperar los solicitantes de las solicitudes dadas.

        :param solicitudes str: Solicitudes en formato JSON.
        :param sgi SGI: Objeto SGI para consultar los datos en el sistema.
        :return list Lista de solicitantes.
        """
        list_solicitantes =  {}
        if solicitudes:
            for solicitud in solicitudes:
                if solicitud['codigoExterno'] != '':
                    list_solicitantes[solicitud['codigoExterno']] = json.loads(sgi.get_persona(solicitud['solicitanteRef']))['apellidos']
            return list_solicitantes
        return list_solicitantes


    def get_bdns(self, id_sgi_convocatoria: int):
        """
        Método para obtener desde la base de datos interna el código BDNS que tiene asignado.

        :param id_sgi_convocatoria int: Número de id que tiene la convocatoria en el sistema SGI.
        :return int El código de la BDNS que tiene asignado. Sino, 0.
        """
        #titulo_codificado = titulo.split(' ', 1)[1].encode("gb2312").decode('utf_8')
        bbdd_url = "http://" + SERVIDOR + ":5000/api/orchestrator/register/convocatorias?_from=BDNS&id_sgi=" + str(id_sgi_convocatoria) + "&entidad_convocante=AGENCIA ESTATAL DE INVESTIGACIÓN"
        response = requests.get(bbdd_url)
        print(response.text)
        if response.ok:
            return int(json.loads(response.text)[0]['url'].split("/")[-1])    
        return 0


    def send_mail(self, id_bdns: int, message: dict, emails: list) -> str:
        """
        Método para enviar un email. Se llama a la rutina Send Mail.

        :param id_bdns int: Número de la BDNS que hace referencia a una convocatoria.
        :param message dict: Diccionario con el contenido del mensaje.
        :param emails list: Lista de emails a los que hay que enviar mensaje.
        :return str: Estado del proceso Send Mail.
        """
        body = message['content']
        files = message['files'] #array de paths, deberian estar en files dentro de robot
        params = {}
        params["port"] = 25
        params["smtp_server"] = "smtp.um.es"
        params["receivers"] = []
        for r in emails:
            user = {}
            user["sender"] = "noreply@um.es"
            user["receiver"] = r['receiver']
            user["subject"] = "Concesión BDNS "+id_bdns
            user["body"] = body
            user["attached"] = files
            params["receivers"].append(user)
        psm = ProcessSendMail(self.log.id_schedule,
                              self.log.id, self.id_robot, "1", None, params)
        psm.add_data_listener(self)
        psm.execute()
        return psm.log.state


    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass
