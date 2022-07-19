import time
from datetime import datetime
import json
from model.SGI import SGI
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID, Pstatus

NAME = "Extract Thesis"
DESCRIPTION = "Proceso que extrae las tesis utilizando SGI."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_THESIS.value

"""
Proceso encargado de extraer tesis utilizando SGI.
"""

class ProcessExtractThesis(ProcessCommand):
    SGI = SGI()

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
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

    def msg_thesis(self, key, cont, response_director, response_codirector):
        """
        Método que genera el mensaje basado en la información de una tesis
        """
        msg: str = ''
        try:
            msg = '<b>TESIS DOCTORAL ' + str(cont) + ': </b><br>'
            msg += 'Título: ' + key['tituloTrabajo'] + '<br>'
            
            if response_director:
                json_dir = json.loads(response_director)
                if json_dir:
                    msg += 'Director: ' + json_dir['nombre'] + ' ' + json_dir['apellidos'] + '<br>'
            
            if response_codirector:
                json_codir = json.loads(response_codirector)
                if json_codir:
                    msg += 'Co-Director: ' + json_codir['nombre'] + ' ' + json_codir['apellidos'] + '<br>'
            
            if key['fechaDefensa']:
                msg += 'Fecha de la defensa: ' + key['fechaDefensa'] + '<br>'

            # url = SGI.host + '/sgp/direccion-tesis' + \
           # str(id_element) + '/ficha-general'
            #msg += 'Url: <a href="' + url + '" target="_blank">' + url + '</a><br>'

        except Exception as e:
            print(e)
            self.notificar_actualizacion(
                'Error en la obtención de datos del elemento con identificador: ' + str(key['id']))
            msg = None

        return msg

    def is_valid(self, element, start_date: datetime, end_date: datetime) -> bool:
        """
        Método que valida si el elemento está dentro de un rango de fechas
        """
        try:
            if element['tipoProyecto'] and element['tipoProyecto']['id'] == "067" and element['fechaDefensa']:
                fechaDefensa = datetime.strptime(
                    element['fechaDefensa'], "%Y-%m-%d")
                if fechaDefensa >= start_date and fechaDefensa <= end_date:
                    return True
        except Exception as e:
            print(e)
            self.notificar_actualizacion(
                'ERROR al obtener la fecha de defensa de la tesis.')
        return False

    def process_results(self, elements, start_date: datetime, end_date: datetime):
        """
        Método que procesa los elementos obtenidos y devuelve una tupla donde
        el primer elemento es el número de elementos válidos y el segundo el mensaje final.
        """
        num_validos: int = 1
        msg: str = ''

        if elements:
            for element in elements:
                if self.is_valid(element, start_date, end_date) == True:
                    response_director = SGI.get_persona(element['personaRef'])
                    response_codirector = SGI.get_persona(element['coDirectorTesisRef'])
                    msg_element = self.msg_thesis(element, num_validos, response_director, response_codirector)
                    if msg_element:
                        num_validos += 1
                        msg += msg_element

        num_validos -= 1
        if num_validos > 0:
            if num_validos > 1:
                msg = '<b>TESIS: Se han obtenido ' + \
                    str(num_validos) + ' tesis.</b><br>' + msg
            else:
                msg = '<b> TESIS: Se ha obtenido 1 tesis.</b><br>' + msg
        else:
            msg = '<b>TESIS: No se ha obtenido ningún elemento.</b><br>'

        return (num_validos, msg)

    def execute(self):
        """
        Función encargada de la ejecución del proceso
        """
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0

        self.notificar_actualizacion(
            "El proceso de obtención de tesis ha comenzado.")
        
        start_date:datetime = self.parameters['start_date']
        end_date:datetime = self.parameters['end_date']

        elements = None
        if start_date.year != end_date.year:
            response = self.SGI.get_tesis(
                'anioDefensa='+str(start_date.year))
            if response:
                elements = json.loads(response)

            response = self.SGI.get_tesis(
                'anioDefensa='+str(end_date.year))
            if response:
                elements += json.loads(response)

        else:
            response = self.SGI.get_tesis(
                'anioDefensa='+str(start_date.year))
            if response:
                elements = json.loads(response)

        self.log.completed = 50
        self.notificar_actualizacion(
            'Comienza el tratamiento de la información obtenida.')
        self.result = self.process_results(elements, start_date, end_date)

        self.notificar_actualizacion('Se han obtenido ' + str(self.result[0]) + ' tesis.')
        self.notificar_actualizacion(
            'Finaliza el tratamiento de la información obtenida.')

        self.log.completed = 100
        self.notificar_actualizacion(
            "El proceso de obtención de tesis ha finalizado.")
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED

    def pause(self):
        pass

    def resume(self):
        pass

    def kill(self):
        pass
