from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import json
import model.SGI as SGI
import time
import model.EDMA as EDMA
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID

NAME = "Grafo Colaborativo"
DESCRIPTION = "Proceso que toma el grafo de colaboración de EDMA para ver las relaciones con otros investigadores"
REQUIREMENTS = ['pandas', 'numpy']
ID = ProcessID.GRAFO_COLABORACION.value


class ProcessGrafoColaboracion(ProcessCommand):
    '''
    Proceso que toma datos de edma dado un investigador y devuelve investigadores que han colaborado con el
    '''

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def execute(self):
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.update_log(
            "Proceso Grafo Colaborativo ha empezado", True)
        self.log.completed = 5
        self.result = None
        investigadores = self.parameters['investigadores']
        convocatoria = self.parameters['convocatoria']
        investigadores_resultado = {}
        ed = EDMA.EDMA()
        for investigador in investigadores:
            df = ed.get_grafo_colaboracion(investigador.email)
            if len(df) > 0:
                df = df.dropna()
                inv_col_10 = df.head(10)
                for email in inv_col_10['email.value']:
                    # Si el correo aparece dentro de los investigadores, significa que no ha hecho la solicitud, por tanto no nos interesa y nos ahorramos procesamiento
                    if not any(x.email == email for x in investigadores):
                        idref = self.get_investigador_sgi(email)
                        if idref and self.get_solicitudes_convocatoria(idref, convocatoria.id):
                            investigadores_resultado[investigador.id] = 1
            if not investigador.id in investigadores_resultado:
                investigadores_resultado[investigador.id] = 0
        self.result = investigadores_resultado
        self.update_log(
            "Result "+str(self.result), True)
        self.update_log(
            "Proceso Grafo Colaborativo ha finalizado correctamente", True)
        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED

    def get_investigador_sgi(self, email):
        ed = EDMA.EDMA()
        r = ed.get_personaref(email)
        return r

    def get_solicitudes_convocatoria(self, idref, idconvocatoria):
        sgi = SGI.SGI()
        solicitudes = sgi.get_solicitudes(
            "solicitanteRef=="+str(idref)+"&convocatoriaId=="+str(idconvocatoria))
        if solicitudes and len(solicitudes) > 0:
            solicitudes = json.loads(solicitudes)
            if len(solicitudes) > 0:
                return True
        return False

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
