import time
import json
from model.SGI import SGI
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus

NAME = "Extract Announcements"
DESCRIPTION = "Proceso que extrae convocatorias utilizando SGI."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_ANNOUNCEMENTS.value

"""
Proceso encargado de extraer convocatorias de SGI.
Este proceso devolverá como resultando una lista de convocatorias.
"""


class ProcessExtractAnnouncements(ProcessCommand):
    SGI = SGI()

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)


    """
    Método encargado de procesar el tratamiento de datos de las entidades convocantes 
    de una convocatoria
    """
    def process_conveners(self, response):
        result: str = ''        
        if response:
            json_convoners = json.loads(response)
            cont = 0
            for key in json_convoners:
                entidad_ref = key['entidadRef']
                if entidad_ref:
                    json_convoner = json.loads(
                        self.SGI.get_empresa(entidad_ref))
                    if json_convoner:
                        if cont > 1:
                            result += ', '
                        if json_convoner['razonSocial']:
                            result += json_convoner['razonSocial']
                        else:
                            result += json_convoner['nombre']

                        cont += 1
        return result

    def process_results(self, convocatorias, consult_sgi:bool):
        """
        Método encargado de procesar el resultado de las convocatorias
        """
        msg = '<b> CONVOCATORIAS: '
        num = 0
        if convocatorias:
            num = len(convocatorias)
            if num > 1:
                msg += 'Se han obtenido ' + \
                    str(num) + ' convocatorias. </b><br>'
            else:
                msg += 'Se ha obtenido 1 convocatoria. </b><br>'

            self.notificar_actualizacion('Se han obtenido ' + str(num) + ' convocatorias.')
            id_conv = 0
            cont = 1
            for key in convocatorias:
                try:
                    id_conv = key['id']
                    msg += '<b>CONVOCATORIA ' + str(cont) + ': </b><br>'
                    if key['codigo']:
                        msg += 'Código: ' + key['codigo'] + '<br>'
                    msg += 'Título: ' + key['titulo'] + '<br>'

                    if id_conv > 0 and consult_sgi:
                        response = self.SGI.get_entidades_convocantes_convocatoria(id_conv)
                        conveners = self.process_conveners(response)
                        if conveners:
                            msg += 'Entidades convocantes: ' + conveners + '<br>'

                    if key['fechaPublicacion']:
                        msg += 'Fecha publicación: ' + \
                            self.format_date(
                                key['fechaPublicacion'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y") + '<br>'
                    if key['fechaProvisional']:
                        msg += 'Fecha provisional: ' + \
                            self.format_date(
                                key['fechaProvisional'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y") + '<br>'
                    if key['fechaConcesion']:
                        msg += 'Fecha concesión: ' + \
                            self.format_date(
                                key['fechaConcesion'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y") + '<br>'
                    
                    url = SGI.host + '/csp/convocatoria/' + str(id_conv) + '/datos-generales'
                    msg += 'Url: <a href="' + url + '" target="_blank">' + url + '</a><br>'
                    
                    cont += 1
                except Exception as e:
                    print(e)
                    cont += 1
                    self.notificar_actualizacion('ERROR al obtener los parámetros de la convocatoria con id: ' + str(id_conv))
        else:
            msg += "No se han obtenido convocatorias. </b> <br>"
            self.notificar_actualizacion('No se han obtenido convocatorias.')
        return (num, msg)

    def execute(self):
        """Función encargada de la ejecución del proceso"""
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0

        # obtención de convocatorias accediendo a SGI
        self.notificar_actualizacion(
            "El proceso de extracción de convocatorias ha comenzado.")

        response = self.SGI.get_convocatorias('activo==true;fechaProvisional=ge=' + self.parameters['start_date'] +
                                              ';fechaProvisional=le=' + self.parameters['end_date'])

        self.log.completed = 50
        # tratto. de la respuesta
        if response:
            json_dict = json.loads(response)
            self.notificar_actualizacion(
                "Extracción de convocatorias: Comienza el tratamiento de los datos obtenidos.")
            self.result = self.process_results(json_dict, True)

        self.log.completed = 100
        self.notificar_actualizacion(
            "El proceso de extracción de convocatorias ha finalizado.")

        if not self.result:
            self.result = '<b> CONVOCATORIAS: No se han obtenido convocatorias. </b> <br>'

        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
