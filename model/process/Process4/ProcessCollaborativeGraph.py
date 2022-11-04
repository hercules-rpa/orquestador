import json
import time
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from rpa_robot.ControllerSettings import ControllerSettings

NAME = "Grafo Colaborativo"
DESCRIPTION = "Proceso que toma el grafo de colaboración de EDMA para ver las relaciones con otros investigadores"
REQUIREMENTS = ['']
ID = ProcessID.COLLABORATIVE_GRAPH.value
cs = ControllerSettings()

class ProcessCollaborativeGraph(ProcessCommand):
    """
    Proceso que toma datos de edma dado un investigador y devuelve investigadores que han colaborado con el
    """

    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None, ip_api = None, port_api = None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

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
        ed = cs.get_edma(self.ip_api, self.port_api)
        for investigador in investigadores:
            df = ed.get_grafo_colaboracion(investigador.email)
            if len(df) > 0:
                df = df.dropna()
                inv_col_10 = df.head(10)
                for email in inv_col_10['email.value']:
                    # Si el correo aparece dentro de la lista de investigadores, significa que no ha hecho la solicitud, por tanto no nos interesa y nos ahorramos procesamiento
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
        ed = cs.get_edma(self.ip_api, self.port_api)
        r = ed.get_personaref(email)
        return r

    def get_solicitudes_convocatoria(self, idref, idconvocatoria):
        sgi = cs.get_sgi(self.ip_api, self.port_api)
        solicitudes = sgi.get_forms(
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
