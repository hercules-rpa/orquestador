import time
from datetime import datetime
import json
from rpa_robot.ControllerSettings import ControllerSettings
from model.SGI import SGI
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID, Pstatus

NAME = "Extract Thesis"
DESCRIPTION = "Proceso que extrae las tesis utilizando SGI."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_THESIS_TRANSFER_REPORT.value
cs = ControllerSettings()
"""
Proceso encargado de extraer tesis utilizando SGI.
"""
class ProcessExtractThesis(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None, ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

    def get_inventors(self, id, sgi:SGI):
        """
        Método que sirve para obtener los inventores
        :param id identificador de la tesis
        :param sgi instancia con la información relacionada con Hércules-SGI
        :return str cadena formateada con los inventores obtenidos
        """
        result: str = ''
        response = sgi.get_inventors_invention(id)
        if response:
            num_inventores = 0
            inventores = json.loads(response)
            for inventor in inventores:
                response = sgi.get_person(inventor['inventorRef'])
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
        :param key información obtenida de la tesis
        :param cont número asignado a la tesis en el mensaje
        :param response_director respuesta de la consulta del director de la tesis
        :param response_codirector respuesta de la consulta del codirector de la tesis
        :return str mensaje con la información de la tesis
        """
        msg: str = ''
        try:
            msg = '<b>TESIS DOCTORAL ' + str(cont) + ': </b><br>'
            msg += 'Título: ' + key['tituloTrabajo'] + '<br>'

            if 'resumen' in key and key['resumen']:
                if len(key['resumen']) > 400:
                    msg += 'Resumen: ' + key['resumen'][0:400] + '<br>'
                else:
                    msg += 'Resumen: ' + key['resumen'] + '<br>'
            
            if response_director:
                json_dir = json.loads(response_director)
                if json_dir:
                    msg += 'Director: ' + json_dir['nombre'] + ' ' + json_dir['apellidos'] + '<br>'
            
            if response_codirector:
                json_codir = json.loads(response_codirector)
                if json_codir:
                    msg += 'Co-Director: ' + json_codir['nombre'] + ' ' + json_codir['apellidos'] + '<br>'
            
            if 'fechaDefensa' in key and key['fechaDefensa']:
                msg += 'Fecha de la defensa: ' + key['fechaDefensa'] + '<br>'

            if 'areaCientifica' in key and key['areaCientifica'] and \
                'nombre' in key['areaCientifica'] and key['areaCientifica']['nombre']:
                    msg += 'Área científica: ' + key['areaCientifica']['nombre'] + '<br>'

            if 'url' in key and key['url']:
                msg += 'Url: <a href="' + key['url'] + '" target="_blank">' + key['url'] + '</a><br>'

        except Exception as e:
            print(e)
            self.notify_update(
                'Error en la obtención de datos del elemento con identificador: ' + str(key['id']))
            msg = None

        return msg

    def is_valid(self, element, start_date: datetime, end_date: datetime) -> bool:
        """
        Método que valida si el elemento está dentro de un rango de fechas
        :param element elemento a validar
        :param start_date fecha inicio
        :param end_date fecha fin
        :return bool True si es válido
        """
        try:
            if element['tipoProyecto'] and element['tipoProyecto']['id'] == "067" and element['fechaDefensa']:
                defense_date = datetime.strptime(
                    element['fechaDefensa'], "%Y-%m-%d")
                if defense_date >= start_date and defense_date <= end_date:
                    return True
        except Exception as e:
            print(e)
            self.notify_update(
                'ERROR al obtener la fecha de defensa de la tesis.')
        return False

    def process_results(self, elements, start_date: datetime, end_date: datetime, consult:bool=False, sgi:SGI=None):
        """
        Método que procesa los elementos obtenidos
        :param elements elementos a procesar
        :param start_date fecha inicio
        :param end_date fecha fin
        :param consult define si se deben realizar consultas adicionales
        :param sgi instancia con la información relacionada con Hércules-SGI
        :return tuple tupla donde el primer elemento es el número de elementos válidos y el segundo el mensaje final.
        """
        num: int = 1
        msg: str = ''

        if elements:
            for element in elements:
                if self.is_valid(element, start_date, end_date) == True:
                    response_director=None
                    if consult and sgi and 'personaRef' in element and element['personaRef']:
                        response_director = sgi.get_person(element['personaRef'])
                    
                    response_codirector=None
                    if consult and sgi and 'coDirectorTesisRef' in element and element['coDirectorTesisRef']:
                        response_codirector = sgi.get_person(element['coDirectorTesisRef'])
                    
                    msg_element = self.msg_thesis(element, num, response_director, response_codirector)
                    if msg_element:
                        num += 1
                        msg += msg_element
        num -= 1
        if num > 0:
            if num > 1:
                msg = '<b>TESIS: Se han obtenido ' + \
                    str(num) + ' tesis.</b><br>' + msg
            else:
                msg = '<b> TESIS: Se ha obtenido 1 tesis.</b><br>' + msg
        else:
            msg = '<b>TESIS: No se ha obtenido ningún elemento.</b><br>'
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
            "El proceso de obtención de tesis ha comenzado.")
        
        start_date:datetime = self.parameters['start_date']
        end_date:datetime = self.parameters['end_date']

        elements = None
        sgi = cs.get_sgi(self.ip_api, self.port_api)
        if sgi:
            if start_date.year == end_date.year:
                response = sgi.get_thesis('anioDefensa='+str(start_date.year))
                if response:
                    elements = json.loads(response)
                
            else:
                response = sgi.get_thesis(
                    'anioDefensa='+str(start_date.year))
                if response:
                    elements = json.loads(response)

                response = sgi.get_thesis(
                    'anioDefensa='+str(end_date.year))
                if response:
                    elements += json.loads(response)

        self.log.completed = 50
        self.notify_update(
            'Comienza el tratamiento de la información obtenida.')
        self.result = self.process_results(elements, start_date, end_date, True, sgi)

        self.notify_update('Se han obtenido ' + str(self.result[0]) + ' tesis.')
        self.notify_update(
            'Finaliza el tratamiento de la información obtenida.')

        self.log.completed = 100
        self.notify_update(
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
