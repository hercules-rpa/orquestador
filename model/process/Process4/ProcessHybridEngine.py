from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
import time

NAME = "Motor híbrido"
DESCRIPTION = "Dado el resultado de los distintos sistemas de recomendación, aplica los pesos correspondientes para devolver el resultado que corresponda"
REQUIREMENTS = ['pandas', 'numpy']
ID = ProcessID.HYBRID_ENGINE.value


class ProcessHybridEngine(ProcessCommand):
    """
    Proceso que toma los datos de los distintos sistemas de recomendación y saca un verecdito, como entrada recibe un array de diccionarios. Con la siguiente estructura: 
        [{'SistemaRecomendacion':nombre, 'peso':peso, 'data':{inv: puntuacion},{'SRContenido':peso, 'data':{inv: puntuacion}]
    """

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None, ip_api = None, port_api = None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

    def execute(self):
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.update_log(
            "Proceso de Motor Híbrido ha comenzado", True)
        self.log.completed = 5
        investigadores = {}

        for dict in self.parameters:
            self.update_log(
                "Sistema de recomendacion: "+dict['SistemaRecomendacion']+", peso: "+str(dict['peso']), True)
            peso = dict['peso']
            self.update_log(
                str(dict['data']), True)
            for key, value in dict['data'].items():
                if not key in investigadores:
                    investigadores[key] = 0
                investigadores[key] += float(value)*float(peso)
        self.result = investigadores
        self.update_log("Resultado:", True)
        self.update_log(str(self.result), True)
        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
