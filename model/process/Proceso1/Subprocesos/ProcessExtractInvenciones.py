import time
import json
from model.SGI import SGI
from model.process.ProcessCommand import ProcessCommand, Pstatus
from model.process.ProcessCommand import ProcessID

NAME = "Extract Invenciones"
DESCRIPTION = "Proceso que extrae las invenciones utilizando SGI."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_INVENCIONES.value

"""
Proceso encargado de extraer elementos de tipo propiedad industrial del SGI.
"""


class ProcessExtractInvenciones(ProcessCommand):
    SGI = SGI()

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def get_inventores(self, id):
        """
        Método que sirve para obtener los inventores
        """
        result: str = ''
        response = self.SGI.get_inventores_invencion(id)
        if response:
            num_inventores = 0
            inventores = json.loads(response)
            for inventor in inventores:
                response = self.SGI.get_persona(inventor['inventorRef'])
                if response:
                    info = json.loads(response)
                    if info:
                        if num_inventores >= 1:
                            result += ', '
                        result += info['nombre'] + \
                            ' ' + info['apellidos']
                        num_inventores += 1

            if result:
                result = 'Inventores: ' + result + '<br>'

        return result

    def get_titulares(self, id):
        """
        Método que sirve para obtener los titulares
        """
        result: str = ''
        response = self.SGI.get_titulares_invencion(id)
        if response:
            num_tit = 0
            elements = json.loads(response)
            for elem in elements:
                response = self.SGI.get_empresa(elem['titularRef'])
                if response:
                    info = json.loads(response)
                    if num_tit >= 1:
                        result += ', '
                    if info['razonSocial']:
                        result += info['razonSocial']
                    else:
                        result += info['nombre']
                    num_tit += 1

            if result:
                result = 'Titulares: ' + result + '<br>'

        return result

    def msg_solicitud(self, sol, num):
        """
        Método que genera la solicitud con los datos proporcionados
        """
        result = 'SOLICITUD ' + str(num) + ': <br>'
        result += 'Título: ' + sol['titulo'] + '<br>'
        result += 'Número solicitud: ' + sol['numeroSolicitud'] + '<br>'

        if sol['numeroRegistro']:
            result += 'Número registro' + sol['numeroRegistro'] + '<br>'
        if sol['fechaPrioridadSolicitud']:
            result += 'Fecha prioridad: ' + \
                self.format_date(
                    sol['fechaPrioridadSolicitud'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")+'<br>'
        if sol['fechaFinPriorPresFasNacRec']:
            result += 'Fecha fin prioridad: ' + \
                self.format_date(
                    sol['fechaFinPriorPresFasNacRec'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")+'<br>'

        if sol['fechaPublicacion']:
            result += 'Fecha publicación: ' + \
                self.format_date(
                    sol['fechaPublicacion'], "%Y-%m-%dT%H:%M:%S.Z", "%d/%m/%Y")+'<br>'

        return result

    def get_solicitudes(self, id):
        """
        Método que sirve para obtener las solicitudes sobre una invención
        """
        result: str = ''
        response = self.SGI.get_solicitudes_invencion(id, 'activo==true')
        if response:
            sol_dict = json.loads(response)
            num = 1
            for sol in sol_dict:
                result += self.msg_solicitud(sol, num)
                num += 1

            if result:
                result = 'SOLICITUDES: <br>' + result

        return result

    def msg_element(self, inv, num, type, consult_information):
        """
        Método que genera un mensaje con la informacion de una invención
        """
        msg: str = ''
        id = inv['id']

        msg += '<b>' + type + ' ' + str(num) + ': </b><br>'
        msg += 'Tipo: ' + \
            inv['tipoProteccion']['nombre'] + '. <br>'
        msg += 'Título: ' + inv['titulo'] + '<br>'
        if inv['descripcion']:
            msg += 'Descripción: ' + inv['descripcion'] + '<br>'
        if inv['fechaComunicacion']:
            date = self.format_date(inv['fechaComunicacion'],
                                    "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")
            if date:
                msg += 'Fecha Comunicación: ' + date \
                    + '<br>'

        # inventores
        if consult_information:
            inventores = self.get_inventores(id)
            if inventores:
                msg += inventores

            # titulares
            titulares = self.get_titulares(id)
            if titulares:
                msg += titulares

            # solicitudes
            solicitudes = self.get_solicitudes(id)
            if solicitudes:
                msg += solicitudes

        url = SGI.host + '/pii/invencion/' + str(id) + '/datos-generales'
        msg += 'Url: <a href="' + url + '" target="_blank">' + url + '</a><br>'

        return msg

    def process_results(self, response, consult_sgi:bool):
        """
        Método encargado de procesar la información de las invenciones obtenidas
        """
        msg_pintelect: str = ''
        msg_pindust: str = ''
        num_pindust = 0
        num_pintelect = 0
        
        if response:
            try:
                invenciones = json.loads(response)
                self.notificar_actualizacion(
                    'Se han obtenido ' + str(len(invenciones)) + ' elementos.')
                self.notificar_actualizacion(
                    'Comienza el tratamiento de la información obtenida.')

                for inv in invenciones:
                    protected_type = inv['tipoProteccion']['id']
                    if protected_type == 8 or protected_type == 9:
                        num_pintelect += 1
                        msg_pintelect += self.msg_element(
                            inv, num_pintelect, "PROPIEDAD INTELECTUAL", consult_sgi)
                    else:
                        num_pindust += 1
                        msg_pindust += self.msg_element(inv,
                                                        num_pindust, "PROPIEDAD INDUSTRIAL", consult_sgi)

                self.notificar_actualizacion(
                    'Finaliza el tratamiento de la información obtenida.')

            except Exception as e:
                print(repr(e))
                self.notificar_actualizacion(
                    "Error al obtener invenciones desde SGI.")
                self.log.state = "ERROR"
        else:
            self.notificar_actualizacion(
                'No se han obtenido invenciones en el rango de fechas indicado.')

        return self.process_msg(
            msg_pintelect, msg_pindust, num_pintelect, num_pindust)

    def process_msg(self, msg_pintelect, msg_pindust, num_pintelect, num_pindust):
        """
        Método para generar el mensaje con la información de las invenciones procesada
        """
        if msg_pindust:
            if num_pindust > 1:
                msg_pindust = '<b>PROPIEDAD INDUSTRIAL: Se han obtenido ' + \
                    str(num_pindust) + ' invenciones.</b><br>' + msg_pindust
            else:
                msg_pindust = '<b> PROPIEDAD INDUSTRIAL: Se ha obtenido 1 invención.</b><br>' + msg_pindust
        else:
            msg_pindust = '<b>PROPIEDAD INDUSTRIAL: No se han obtenido invenciones.</b><br>'

        if msg_pintelect:
            if num_pintelect > 1:
                msg_pintelect = '<b> PROPIEDAD INTELECTUAL: Se han obtenido ' + \
                    str(msg_pintelect) + ' invenciones. </b><br>' + msg_pintelect
            else:
                msg_pintelect = '<b> PROPIEDAD INTELECTUAL: Se ha obtenido 1 invención. </b><br>' + msg_pintelect
        else:
            msg_pintelect = '<b> PROPIEDAD INTELECTUAL: No se han obtenido invenciones. </b><br>'

        return ((num_pindust, msg_pindust), (num_pintelect, msg_pintelect))

    def execute(self):
        """
        Método encargado de la ejecución del proceso
        """
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0

        self.notificar_actualizacion(
            "El proceso de obtención de invenciones ha comenzado.")

        self.notificar_actualizacion('Consultando si existen invenciones en SGI con el rango de fechas indicado.')
        response = self.SGI.get_invenciones(
            'fechaComunicacion=ge=' + self.parameters['start_date'] + ';fechaComunicacion=le=' + self.parameters['end_date'])

        self.log.completed = 50

        self.notificar_actualizacion('Comienza el tratamiento de los datos obtenidos.')
        self.result = self.process_results(response, True)
        self.notificar_actualizacion('Finaliza el tratamiento de los datos obtenidos.')
        
        self.log.completed = 100

        self.notificar_actualizacion(
            "El proceso de obtención de invenciones ha finalizado.")
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED

    def pause(self):
        pass

    def resume(self):
        pass

    def kill(self):
        pass
