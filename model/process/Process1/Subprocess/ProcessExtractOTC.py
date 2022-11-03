import time
from rpa_robot.ControllerSettings import ControllerSettings
from model.process.Process1.Entities.TecnologyOffer import TecnologyOffer
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus

NAME = "Extracción oferta tecnológica"
DESCRIPTION = "Proceso que extrae oferta tecnológica."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_OTC_TRANSFER_REPORT.value
cs = ControllerSettings()

class ProcessExtractOTC(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

    
    def process_results(self, df) -> list:
        """
        Método encargado del tratamiento de los datos
        :param df dataframe con los datos obtenidos
        :return list lista de elementoss
        """
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
                self.notify_update('ERROR en la obtención de información de la oferta tecnológica con título: ' + title)
                          
        return otcs

    def execute(self):
        """
        Método encargado de la ejecución del proceso
        """
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0
        otcs = []

        start_date = self.parameters['start_date']
        end_date = self.parameters['end_date']
        
        self.notify_update(
            "El proceso de extracción de oferta tecnológica ha comenzado.")

        edma = cs.get_edma(self.ip_api, self.port_api)
        if edma:
            df = edma.get_tecnology_offers(start_date, end_date)
            self.log.completed = 25

            try:
                if not df.empty:
                    self.notify_update(
                                    "Extracción de oferta tecnológica: Comienza el tratamiento de los datos obtenidos.")
                    otcs = self.process_results(df)
                    self.log.completed = 50
                else:
                    self.notify_update(
                                    'No se ha obtenido ningún elemento en el rango de fechas indicado.')
            except Exception as e:
                    self.notify_update(
                        'Error al obtener la oferta tecnológica con el rango de fechas indicado.')
                    self.notify_update(str(e))
                    self.log.state = "ERROR"            
        else:
            self.log.state = "ERROR"  
            self.notify_update("ERROR en la inicialización de la información de Hércules-EDMA")          

        self.log.completed = 100
        self.notify_update(
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
