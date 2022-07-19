import time
from model.process.Proceso1.Entidades.TecnologyOffer import TecnologyOffer
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus
from model.EDMA import EDMA


NAME = "Extracción oferta tecnológica"
DESCRIPTION = "Proceso que extrae oferta tecnológica."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_OTC.value


class ProcessExtractOTC(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    
    def process_results(self, df) -> list:
        """Función encargada del tratamiento de los datos"""
        otcs = []
        names = []
        otc: TecnologyOffer = None
        title:str = ''
        for index, elem in df.iterrows():
            title = elem['titulo.value']
            try:
                if title not in names:
                    names.append(title)
                    otc = TecnologyOffer(title=title)
                    otc.set_properties(elem)
                    otcs.append(otc)
                else:
                    otc.add_researcher(elem)  
            except Exception as e:
                print(e)
                self.notificar_actualizacion('ERROR en la obtención de información de la oferta tecnológica con título: ' + title)
                          
        return otcs

    def execute(self):
        """Función encargada de la ejecución del proceso"""
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0
        otcs = []
        # obtención parametros
        start_date = self.parameters['start_date']
        end_date = self.parameters['end_date']
        # obtención de oferta tecnológica accediendo a ED
        self.notificar_actualizacion(
            "El proceso de extracción de oferta tecnológica ha comenzado.")

        edma = EDMA()
        if self.ping(edma.IP):
            df = edma.get_oferta_tecnologica(start_date, end_date)
            self.log.completed = 25

            try:
                if not df.empty:
                    self.notificar_actualizacion(
                                "Extracción de oferta tecnológica: Comienza el tratamiento de los datos obtenidos.")
                    otcs = self.process_results(df)
                    self.log.completed = 50
                else:
                    self.notificar_actualizacion(
                                'No se ha obtenido ningún elemento en el rango de fechas indicado.')
            except Exception as e:
                self.notificar_actualizacion(
                    'Error al obtener la oferta tecnológica con el rango de fechas indicado.')
                self.notificar_actualizacion(str(e))
        else:
            self.notificar_actualizacion('ERROR: el proceso no dispone de conexión con ED.')
            self.log.state = "ERROR"
       
        self.log.completed = 100
        self.notificar_actualizacion(
            "El proceso de extracción de oferta tecnológica ha finalizado.")
        self.result = otcs
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED

    def kill(self):
        pass

    def resume(self):
        pass

    def pause(self):
        pass
