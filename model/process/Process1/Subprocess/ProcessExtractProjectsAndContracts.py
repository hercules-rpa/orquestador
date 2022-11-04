import time
import json
from rpa_robot.ControllerSettings import ControllerSettings
from model.SGI import SGI
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus

NAME = "Extract Projects and Contracts"
DESCRIPTION = "Proceso que extrae proyectos y contratos utilizando SGI."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_PROJECTS_AND_CONTRACTS_TRANSFER_REPORT.value
cs = ControllerSettings()
"""Proceso que como resultado devuelve dos listas, una de proyectos y otra de contratos."""


class ProcessExtractProjectsAndContracts(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

    def get_budget(self, key, sgi:SGI):
        """
        Método que sirve para obtener el presupuesto
        :param key información del proyecto/contrato
        :param sgi instancia con la información relacionada con Hércules-SGI
        :return str cadena con los datos del presupuesto
        """
        msg: str = ''
        prep_dict = None
        id = key['id']
        try:
            if key['totalImportePresupuesto']:
                msg += 'Importe total presupuesto: ' + \
                    str(key['totalImportePresupuesto']) + '€ <br>'
            else:
                if sgi:
                    response = sgi.get_project_budget(key['id'])
                    if response:
                        prep_dict = json.loads(response)
                        if prep_dict and prep_dict['importeTotalPresupuesto']:
                            msg += 'Importe total presupuesto: ' + \
                                str(prep_dict['importeTotalPresupuesto']) + '€ <br>'

            if key['totalImporteConcedido']:
                msg += 'Importe total concedido: ' + \
                    str(key['totalImporteConcedido']) + '€ <br>'
            else:
                if not prep_dict and sgi:
                    response = sgi.get_project_budget(key['id'])
                    if response:
                        prep_dict = json.loads(response)

                if prep_dict and prep_dict['importeTotalConcedido']:
                    msg += 'Importe total concedido: ' + \
                        str(prep_dict['importeTotalConcedido']) + '€ <br>'
        except Exception as e:
            print(e)
            self.notify_update('ERROR al obtener el presupuesto del proyecto/contrato con id: ' + str(id))

        return msg

    def get_researchers(self, id_element, sgi:SGI):
        """
        Método encargado de obtener y realizar el tratamiento de datos de los
        investigadores miembros del equipo de un proyecto/contrato
        :param id_element identificador del proyecto/contrato
        :param sgi instancia con la información relacionada con Hércules-SGI
        :return str cadena formateada con los investigadores obtenidos
        """
        result: str = ''
        try:
            if sgi:
                response = sgi.get_project_team(id_element)
                if response:
                    json_members = json.loads(response)
                    cont = 0
                    for key in json_members:
                        persona_ref = key['personaRef']
                        if persona_ref:
                            response=sgi.get_person(persona_ref)
                            if response:
                                json_member = json.loads(response)
                                if json_member:
                                    if cont >= 1:
                                        result += ', '
                                    result += json_member['nombre'] + \
                                        ' ' + json_member['apellidos']

                                    cont += 1
                    if result:
                        result = 'Investigadores: ' + result + '<br>'
        except Exception as e:
            print(e)
            self.notify_update('ERROR al obtener los investigadores del elemento con id: ' + str(id_element))

        return result

    def get_conveners(self, id_element, sgi:SGI):
        """
        Método encargado de obtener y realizar el tratamiento de datos de las
        entidades convocantes de un proyecto/contrato
        :param id_element identificador del proyecto/contrato
        :param sgi instancia con la información relacionada con Hércules-SGI
        :return str cadena formateada con las entidades convocantes obtenidas
        """
        result: str = ''
        try:
            if sgi:
                response = sgi.get_conveners_project(id_element)
                if response:
                    json_convoners = json.loads(response)
                    cont = 0
                    for key in json_convoners:
                        entity_ref = key['entidadRef']
                        if entity_ref:
                            entity = sgi.get_company(entity_ref)
                            if entity:
                                json_convoner = json.loads(entity)
                                if json_convoner:
                                    if cont >= 1:
                                        result += ', '
                                    if json_convoner['razonSocial']:
                                        result += json_convoner['razonSocial']
                                    else:
                                        result += json_convoner['nombre']

                                    cont += 1

                    if result:
                        result = 'Entidades convocantes: ' + result + '<br>'
        except Exception as e:
            print(e)
            self.notify_update('ERROR al obtener las entidades convocantes del elemento con id: ' + str(id_element))

        return result

    def msg_element(self, key: dict, is_project: bool, consult_information:bool,sgi:SGI=None) -> str:
        """
        Método para generar un mensaje con la informacion de un proyecto
        :param key diccionario con la información obtenida
        :param is_project True si el elemento a tratar es un proyecto
        :param consult_information True si es necesario consultar información adicional 
        :param sgi instancia con la información relacionada con Hércules-SGI
        :return str mensaje con la información del elemento tratado
        """
        msg: str = ''
        id_element: int = 0
        try:
            if key:
                id_element = key['id']
                if key['acronimo']:
                    msg += 'Acrónimo: ' + key['acronimo'] + '<br>'
                msg += 'Título: ' + key['titulo'] + '<br>'
                if key['fechaInicio']:
                    fecha_str = self.format_date(
                            key['fechaInicio'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")
                    if fecha_str:
                        msg += 'Fecha inicio: ' + fecha_str + '<br>'
                if key['fechaFin']:
                    fecha_str = self.format_date(
                            key['fechaFin'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")
                    if fecha_str:
                        msg += 'Fecha fin: ' + fecha_str + '<br>'
                if key['fechaFinDefinitiva']:
                    fecha_str = self.format_date(
                            key['fechaFinDefinitiva'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y")
                    if fecha_str:
                        msg += 'Fecha definitiva: ' + fecha_str + '<br>'

                if is_project:
                    if 'convocatoriaId' in key and consult_information:
                        id_conv =  key['convocatoriaId']
                        if id_conv and id_conv >0 and sgi:
                            conv = sgi.get_call(key['convocatoriaId'])
                            if conv:
                                conv_dict = json.loads(conv)
                                msg += 'Convocatoria: ' + \
                                    conv_dict['titulo'] + '<br>'

                    if key['convocatoriaExterna']:
                        msg += 'Convocatoria Externa: ' + \
                            str(key['convocatoriaExterna']) + '<br>'

                    if consult_information:
                        msg += self.get_conveners(id_element, sgi)

                if consult_information:
                    msg += self.get_researchers(id_element,sgi)
                
                if consult_information:
                    msg += self.get_budget(key, sgi)
                if sgi:
                    url = sgi.host + '/csp/proyectos/' + \
                        str(id_element) + '/ficha-general'
                    msg += 'Url: <a href="' + url + '" target="_blank">' + 'elemento-'+(str(id_element))+'/ficha-general</a><br>'
        except Exception as e:
            print(e)
            self.notify_update(
                'ERROR al realizar el tratamiento del elemento con identificador:  ' + str(id_element))


        return msg

    def process_results(self, response, sgi:SGI=None,consult_information:bool=True):
        """
            Método encargado del tratamiento de los datos.
            :param response respuesta obtenida tras la petición a Hércules-SGI
            :param sgi instancia con la información relacionada con Hércules-SGI
            :param consult_information True si es necesario consultar información adicional
            :return tuple tupla donde el primer elemento es una lista de proyectos y el segundo
            una lista de contratos.
         """
        projects: str = ''
        contracts: str = ''
        num_projects = 0
        num_contracts = 0
        if response:
            json_dicti = json.loads(response)
            for key in json_dicti:
                    modelo_ejecucion = key['modeloEjecucion']
                    if modelo_ejecucion['contrato']:
                        num_contracts += 1
                        contracts += '<b>CONTRATO ' + \
                            str(num_contracts) + ': </b><br>' + \
                            self.msg_element(key, False, consult_information, sgi)
                    else:
                        num_projects += 1
                        projects += '<b>PROYECTO ' + \
                            str(num_projects) + ': </b><br> ' + \
                            self.msg_element(key, True, consult_information, sgi)
                
        if num_projects > 0:
            if num_projects == 1:
                projects = '<b>PROYECTOS: Se ha obtenido 1 proyecto. </b><br>' + projects
            else:
                projects = '<b>PROYECTOS: Se han obtenido ' + \
                    str(num_projects) + ' proyectos. </b><br>' + projects
        else:
            projects = '<b>PROYECTOS: No se han obtenido proyectos. </b><br>'

        if num_contracts > 0:
            if num_contracts == 1:
                contracts = '<b>CONTRATOS: Se ha obtenido 1 contrato. </b><br>' + contracts
            else:
                contracts = '<b>CONTRATOS: Se han obtenido ' + \
                    str(num_contracts) + ' contratos </b><br>' + contracts
        else:
            contracts = '<b>CONTRATOS: No se han obtenido contratos. </b><br>'

        return [(projects, num_projects), (contracts, num_contracts)]

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
            "El proceso de extracción de proyectos y contratos ha comenzado.")
        sgi = cs.get_sgi(self.ip_api, self.port_api)
        response = None 
        if sgi:
            response = sgi.get_projects('activo==true;fechaInicio=ge=' + self.parameters['start_date'] +
                                        ';fechaFin=le=' + self.parameters['end_date'])
        else: 
            self.log.state= "ERROR"
            self.notify_update("ERROR al obtener la configuración de Hércules-SGI")

        self.log.completed = 50

        self.notify_update(
            'Extracción de proyectos y contratos: Comienza el tratamiento de los datos obtenidos.')
        self.result = self.process_results(response, sgi, True)
    
        self.log.completed = 100
        self.notify_update(
            "El proceso de extracción de proyectos y contratos ha finalizado.")
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED

    def kill(self):
        pass

    def resume(self):
        pass

    def pause(self):
        pass
