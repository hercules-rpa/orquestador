import time
import json
from rpa_robot.ControllerSettings import ControllerSettings
from model.SGI import SGI
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus

NAME = "Extract Calls"
DESCRIPTION = "Proceso que extrae convocatorias utilizando SGI."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_CALLS_TRANSFER_REPORT.value
cs = ControllerSettings()
"""
Proceso encargado de extraer convocatorias de Hércules-SGI.
Este proceso devolverá como resultando una lista de convocatorias.
"""
class ProcessExtractCalls(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters,ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)
    
    def process_conveners(self, response, sgi:SGI):
        """
        Método encargado de procesar el tratamiento de datos de las entidades convocantes de una convocatoria
        :param response respuesta obtenida tras la consulta a Hércules-SGI
        :param SGI clase que contiene la información de Hércules-SGI
        :return str cadena formateada de las entidades convocantes de una convocatoria
        """
        result: str = ''        
        if response and sgi:
            json_convoners = json.loads(response)
            cont = 0
            for key in json_convoners:
                entity_ref = key['entidadRef']
                if entity_ref:
                    json_convoner = json.loads(
                        sgi.get_company(entity_ref))
                    if json_convoner:
                        if cont > 1:
                            result += ', '
                        if json_convoner['razonSocial']:
                            result += json_convoner['razonSocial']
                        else:
                            result += json_convoner['nombre']

                        cont += 1
        return result

    def process_results(self, elements, consult_sgi:bool, sgi:SGI=None):
        """
        Método encargado de procesar el resultado de las convocatorias
        :param elements lista de elementos obtenidos
        :param consult_sgi consultar o no información adicional a Hércules-SGI        
        :param sgi clase con la información de Hércules-SGI
        :return str mensaje de la sección de convocatorias a incluir en el correo electrónico final
        """
        msg = '<b> CONVOCATORIAS: '
        num = 0
        if elements:
            num = len(elements)
            if num > 1:
                msg += 'Se han obtenido ' + \
                    str(num) + ' convocatorias. </b><br>'
            else:
                msg += 'Se ha obtenido 1 convocatoria. </b><br>'

            self.notify_update('Se han obtenido ' + str(num) + ' convocatorias.')
            id_conv = 0
            cont = 1
            for key in elements:
                try:
                    id_conv = key['id']
                    msg += '<b>CONVOCATORIA ' + str(cont) + ': </b><br>'
                    if key['codigo']:
                        msg += 'Código: ' + key['codigo'] + '<br>'
                    msg += 'Título: ' + key['titulo'] + '<br>'

                    if id_conv > 0 and consult_sgi and sgi:
                        response = sgi.get_conveners_call(id_conv)
                        conveners = self.process_conveners(response, sgi)
                        if conveners:
                            msg += 'Entidades convocantes: ' + conveners + '<br>'

                    if key['fechaPublicacion']:
                        date_str=self.format_date(
                                key['fechaPublicacion'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")
                        if date_str:
                            msg += 'Fecha publicación: ' + date_str+ '<br>'
                    if key['fechaProvisional']:
                        date_str = self.format_date(
                                key['fechaProvisional'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")
                        if date_str:
                             msg += 'Fecha provisional: ' + date_str + '<br>'
                    if key['fechaConcesion']:
                        date_str = self.format_date(
                                key['fechaConcesion'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")
                        if date_str:
                            msg += 'Fecha concesión: ' + date_str + '<br>'
                    
                    if sgi:
                        url = sgi.host + '/csp/convocatoria/' + str(id_conv) + '/datos-generales'
                        msg += 'Url: <a href="' + url + '" target="_blank">elemento-'+(str(id_conv))+'/datos-generales</a><br>'
                        
                    cont += 1
                except Exception as e:
                    print(e)
                    cont += 1
                    self.notify_update('ERROR al obtener los parámetros de la convocatoria con id: ' + str(id_conv))
        else:
            msg += "No se han obtenido convocatorias. </b> <br>"
            self.notify_update('No se han obtenido convocatorias.')
        return (num, msg)

    def execute(self):
        """
        Método encargado de la ejecución del proceso
        """
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0

        self.notify_update(
            "El proceso de extracción de convocatorias ha comenzado.")

        sgi = cs.get_sgi(self.ip_api, self.port_api)
        if sgi:
            response = sgi.get_calls('activo==true;fechaProvisional=ge=' + self.parameters['start_date'] +
                                                ';fechaProvisional=le=' + self.parameters['end_date'])

            self.log.completed = 50
            if response:
                json_dict = json.loads(response)
                self.notify_update(
                    "Extracción de convocatorias: Comienza el tratamiento de los datos obtenidos.")
                self.result = self.process_results(json_dict, True, sgi)

            self.log.completed = 100
            self.notify_update(
                "El proceso de extracción de convocatorias ha finalizado.")

            if not self.result:
                self.result = (0,'<b> CONVOCATORIAS: No se han obtenido convocatorias. </b> <br>')
        else:
            self.notify_update('ERROR al obtener parámetros de Hércules-SGI')
            self.log.state = "ERROR"

        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
