import time
import json
from model.SGI import SGI
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus

NAME = "Extract Projects and Contracts"
DESCRIPTION = "Proceso que extrae proyectos y contratos utilizando SGI."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_PROJECTS_AND_CONTRACTS.value

"""Proceso que como resultado devuelve dos listas, una de proyectos y otra de contratos."""


class ProcessExtractProjectsAndContracts(ProcessCommand):
    SGI = SGI()

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def get_presupuesto(self, key):
        """
        Método que sirve para obtener el presupuesto
        """
        print('get_presupuesto')
        msg: str = ''
        prep_dict = None

        if key['totalImportePresupuesto']:
            msg += 'Importe total presupuesto: ' + \
                str(key['totalImportePresupuesto']) + '€ <br>'
        else:
            response = self.SGI.get_presupuesto_proyecto(key['id'])
            if response:
                prep_dict = json.loads(response)
                if prep_dict and prep_dict['importeTotalPresupuesto']:
                    msg += 'Importe total presupuesto: ' + \
                        str(prep_dict['importeTotalPresupuesto']) + '€ <br>'

        if key['totalImporteConcedido']:
            msg += 'Importe total concedido: ' + \
                str(key['totalImporteConcedido']) + '€ <br>'
        else:
            if not prep_dict:
                response = self.SGI.get_presupuesto_proyecto(key['id'])
                if response:
                    prep_dict = json.loads(response)

            if prep_dict and prep_dict['importeTotalConcedido']:
                msg += 'Importe total concedido: ' + \
                    str(prep_dict['importeTotalConcedido']) + '€ <br>'

        return msg

    def get_researchers(self, id_element):
        """
        Método encargado de obtener y realizar el tratamiento de datos de los
        investigadores miembros del equipo de un proyecto/contrato
        """
        result: str = ''
        try:
            response = self.SGI.get_equipo_proyecto(id_element)
            if response:
                json_members = json.loads(response)
                cont = 0
                for key in json_members:
                    persona_ref = key['personaRef']
                    if persona_ref:
                        response=self.SGI.get_persona(persona_ref)
                        if response:
                            json_member = json.loads()
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
            self.notificar_actualizacion('ERROR al obtener los investigadores del elemento con id: ' + id_element)

        return result

    def get_conveners(self, id_element):
        """
        Método encargado de obtener y realizar el tratamiento de datos de las
        entidades convocantes de un proyecto/contrato
        """
        result: str = ''
        try:
            response = self.SGI.get_entidades_convocantes_proyecto(id_element)
            if response:
                json_convoners = json.loads(response)
                cont = 0
                for key in json_convoners:
                    entidad_ref = key['entidadRef']
                    if entidad_ref:
                        entidad = self.SGI.get_empresa(entidad_ref)
                        if entidad:
                            json_convoner = json.loads(entidad)
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
            self.notificar_actualizacion('ERROR al obtener las entidades convocantes del elemento con id: ' + id_element)

        return result

    def msg_element(self, key: dict, is_project: bool, consult_information:bool ):
        """
        Método para generar un mensaje con la informacion de un proyecto
        """
        msg: str = ''
        id_element: int = 0
        if key:
            id_element = key['id']
            if key['acronimo']:
                msg += 'Acrónimo: ' + key['acronimo'] + '<br>'
            msg += 'Titulo: ' + key['titulo'] + '<br>'
            if key['fechaInicio']:
                msg += 'Fecha inicio: ' + \
                    self.format_date(
                        key['fechaInicio'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y") + '<br>'
            if key['fechaFin']:
                msg += 'Fecha fin: ' + \
                    self.format_date(
                        key['fechaFin'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y") + '<br>'
            if key['fechaFinDefinitiva']:
                msg += 'Fecha definitiva: ' + \
                    self.format_date(
                        key['fechaFinDefinitiva'], "%Y-%m-%dT%H:%M:%SZ", "%d/%m/%Y") + '<br>'

                # org. convocante
            if is_project:
                if 'convocatoriaId' in key and key['convocatoriaId'] > 0 and consult_information:
                    conv = self.SGI.get_convocatoria(key['convocatoriaId'])
                    if conv:
                        conv_dict = json.loads(conv)
                        msg += 'Convocatoria: ' + \
                            conv_dict['titulo'] + '<br>'

                if key['convocatoriaExterna']:
                    msg += 'Convocatoria Externa: ' + \
                        key['convocatoriaExterna'] + '<br>'

                if consult_information:
                    msg += self.get_conveners(id_element)

            # equipo
            if consult_information:
                msg += self.get_researchers(id_element)
            # presupuesto
            if consult_information:
                msg += self.get_presupuesto(key)

            url = SGI.host + '/csp/proyectos/' + \
                str(id_element) + '/ficha-general'
            msg += 'Url: <a href="' + url + '" target="_blank">' + url + '</a><br>'

        return msg

    def process_results(self, response, consult_information:bool):
        """
            Función encargada del tratamiento de los datos.
            Devuelve una tupla donde el primer elemento es una lista de proyectos y el segundo
            una lista de contratos.
         """
        projects: str = ''
        contracts: str = ''
        num_projects = 0
        num_contracts = 0
        if response:
            json_dicti = json.loads(response)
            id:int = 0
            for key in json_dicti:
                try:
                    id = key['id']
                    modelo_ejecucion = key['modeloEjecucion']
                    if modelo_ejecucion['contrato']:
                        num_contracts += 1
                        contracts += '<b>CONTRATO ' + \
                            str(num_contracts) + ': </b><br>' + \
                            self.msg_element(key, False, consult_information)
                    else:
                        num_projects += 1
                        projects += '<b>PROYECTO ' + \
                            str(num_projects) + ': </b><br> ' + \
                            self.msg_element(key, True, consult_information)
                except Exception as e:
                    print(e)
                    self.notificar_actualizacion(
                        'ERROR al realizar el tratamiento del elemento con identificador:  ' + str(id))

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
        """Función encargada de la ejecución del proceso"""
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0

        # obtención de proyectos accediendo a SGI
        self.notificar_actualizacion(
            "El proceso de extracción de proyectos y contratos ha comenzado.")
        response = self.SGI.get_proyectos('activo==true;fechaInicio=ge=' + self.parameters['start_date'] +
                                          ';fechaFin=le=' + self.parameters['end_date'])
        self.log.completed = 50

        # tratto. de la respuesta
        self.notificar_actualizacion(
            'Extracción de proyectos y contratos: Comienza el tratamiento de los datos obtenidos.')
        self.result = self.process_results(response, True)
    
        self.log.completed = 100
        self.notificar_actualizacion(
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
