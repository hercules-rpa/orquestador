import time
import json
from rpa_robot.ControllerSettings import ControllerSettings
from model.SGI import SGI
from model.process.ProcessCommand import ProcessCommand, Pstatus
from model.process.ProcessCommand import ProcessID

NAME = "Extract Invenciones"
DESCRIPTION = "Proceso que extrae las invenciones utilizando SGI."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_INVENTIONS_TRANSFER_REPORT.value
cs = ControllerSettings()
"""
Proceso encargado de extraer elementos de tipo propiedad industrial e intelectual 
utilizando Hércules-SGI.
"""
class ProcessExtractInventions(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

    def get_inventors(self, id, sgi:SGI):
        """
        Método que obtiene los inventores de una invención
        :param id identificador de una invención
        :param sgi instancia con la información relacionada con Hércules-SGI
        :return str cadena formateada con los inventores 
        """
        result: str = ''
        response = sgi.get_inventors_invention(id)
        if response:
            num_inventors = 0
            inventors = json.loads(response)
            for inventor in inventors:
                response = sgi.get_person(inventor['inventorRef'])
                if response:
                    info = json.loads(response)
                    if info:
                        if num_inventors >= 1:
                            result += ', '
                        result += info['nombre'] + \
                            ' ' + info['apellidos']
                        num_inventors += 1

            if result:
                result = 'Inventores: ' + result + '<br>'

        return result

    def get_incumbent(self, id, sgi:SGI):
        """
        Método que obtiene los titulares de una invención
        :param id identificador de una invención
        :param sgi instancia con la información relacionada con Hércules-SGI
        :return str cadena formateada con los titulares 
        """
        result: str = ''
        response = sgi.get_imcumbent_invention(id)
        if response:
            num = 0
            elements = json.loads(response)
            for elem in elements:
                response = sgi.get_company(elem['titularRef'])
                if response:
                    info = json.loads(response)
                    if num >= 1:
                        result += ', '
                    if info['razonSocial']:
                        result += info['razonSocial']
                    else:
                        result += info['nombre']
                    num += 1

            if result:
                result = 'Titulares: ' + result + '<br>'

        return result

    def msg_requests(self, element, num):
        """
        Método que genera el mensaje de una solicitud con los datos proporcionados
        :param element datos de una solicitud
        :param num número asignado a la solicitud
        :return str mensaje con los datos de la solicitud
        """
        result = 'SOLICITUD ' + str(num) + ': <br>'
        result += 'Título: ' + element['titulo'] + '<br>'
        result += 'Número solicitud: ' + element['numeroSolicitud'] + '<br>'

        if element['numeroRegistro']:
            result += 'Número registro' + element['numeroRegistro'] + '<br>'
        if element['fechaPrioridadSolicitud']:
            result += 'Fecha prioridad: ' + \
                self.format_date(
                    element['fechaPrioridadSolicitud'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")+'<br>'
        if element['fechaFinPriorPresFasNacRec']:
            fecha_str = self.format_date(
                    element['fechaFinPriorPresFasNacRec'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")
            if fecha_str:
                result += 'Fecha fin prioridad: ' + fecha_str +'<br>'

        if element['fechaPublicacion']:
            fecha_str = self.format_date(
                    element['fechaPublicacion'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")
            if fecha_str:
                result += 'Fecha publicación: ' + fecha_str +'<br>'

        return result

    def get_requests(self, id, sgi:SGI):
        """
        Método encargado de la obtención de las solicitudes de una invención
        :param id identificador de la invención        
        :param sgi instancia con la información relacionada con Hércules-SGI

        :return str mensaje con todas las solicitudes obtenidas
        """
        result: str = ''
        response = sgi.get_request_invention(id, 'activo==true')
        if response:
            sol_dict = json.loads(response)
            num = 1
            for sol in sol_dict:
                result += self.msg_requests(sol, num)
                num += 1

            if result:
                result = 'SOLICITUDES: <br>' + result

        return result

    def msg_element(self, inv, num, type, consult_information, sgi:SGI):
        """
        Método que genera un mensaje con la informacion de una invención
        :param inv datos de una invención
        :param num número asignado a la invención
        :param type tipo de invención        
        :param consult_information True si es necesario solicitar información a Hércules-SGI
        :param sgi instancia con la información relacionada con Hércules-SGI
        :return str mensaje con la información de una invención
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

        if consult_information:
            inventors = self.get_inventors(id, sgi)
            if inventors:
                msg += inventors

            incumbent = self.get_incumbent(id,sgi)
            if incumbent:
                msg += incumbent

            requests = self.get_requests(id,sgi)
            if requests:
                msg += requests
        if sgi:
            url = sgi.host + '/pii/invencion/' + str(id) + '/datos-generales'
            msg += 'Url: <a href="' + url + '" target="_blank">elemento-'+(str(id))+'/datos-generales</a><br>'

        return msg

    def process_results(self, response, consult_sgi:bool, sgi:SGI=None):
        """
        Método encargado de procesar la información de las invenciones obtenidas
        :param response datos obtenidos de Hércules-SGI
        :param consult_sgi True si es necesario realizar consultas a Hércules-SGI
        :param sgi instancia con la información relacionada con Hércules-SGI
        :return str mensaje con los datos obtenidos
        """
        msg_pintelect: str = ''
        msg_pindust: str = ''
        num_pindust = 0
        num_pintelect = 0
        
        if response:
            try:
                elements = json.loads(response)
                self.notify_update(
                    'Se han obtenido ' + str(len(elements)) + ' elementos.')
                self.notify_update(
                    'Comienza el tratamiento de la información obtenida.')

                for inv in elements:
                    protected_type = inv['tipoProteccion']['id']
                    if protected_type == 8 or protected_type == 9:
                        num_pintelect += 1
                        msg_pintelect += self.msg_element(
                            inv, num_pintelect, "PROPIEDAD INTELECTUAL", consult_sgi, sgi)
                    else:
                        num_pindust += 1
                        msg_pindust += self.msg_element(inv,
                                                        num_pindust, "PROPIEDAD INDUSTRIAL", consult_sgi, sgi)

                self.notify_update(
                    'Finaliza el tratamiento de la información obtenida.')

            except Exception as e:
                print(repr(e))
                self.notify_update(
                    "Error al obtener invenciones desde SGI.")
                self.log.state = "ERROR"
        else:
            self.notify_update(
                'No se han obtenido invenciones en el rango de fechas indicado.')

        return self.process_msg(
            msg_pintelect, msg_pindust, num_pintelect, num_pindust)

    def process_msg(self, msg_pintelect, msg_pindust, num_pintelect, num_pindust):
        """
        Método para generar el mensaje con la información de las invenciones procesada 
        :param msg_pintelect mensaje de la sección propiedad intelectual
        :param msg_indust mensaje de la sección de propiedad industrial
        :param num_pintelect número de elementos obtenidos de la sección de propiedad intelectual
        :param num_pindustr número de elementos obtenidos de la sección de propiedad industrial
        :return tuple primer elemento contiene una tupla con el nº de elementos y el mensaje de propiedad intelectual,
        el segundo elemento lo mismo pero para la propiedad industrial
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

        self.notify_update(
            "El proceso de obtención de invenciones ha comenzado.")

        self.notify_update('Consultando si existen invenciones en SGI con el rango de fechas indicado.')
        sgi = cs.get_sgi(self.ip_api, self.port_api)
        if sgi:
            response = sgi.get_inventions(
                'fechaComunicacion=ge=' + self.parameters['start_date'] + ';fechaComunicacion=le=' + self.parameters['end_date'])

            self.log.completed = 50

            self.notify_update('Comienza el tratamiento de los datos obtenidos.')
            self.result = self.process_results(response, True, sgi)
            self.notify_update('Finaliza el tratamiento de los datos obtenidos.')
            
        else:
            self.notify_update('ERROR al obtener información de Hércules-SGI')
            self.log.state='ERROR'
        
        self.log.completed = 100
        self.notify_update(
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
