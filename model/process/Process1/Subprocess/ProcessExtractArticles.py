import time
from rpa_robot.ControllerSettings import ControllerSettings
from model.process.Process1.Entities.Article import Article
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus

NAME = "Extract Articles"
DESCRIPTION = "Proceso que extrae artículos científicos."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_ARTICLES_TRANSFER_REPORT.value
cs = ControllerSettings()

class ProcessExtractArticles(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None, 
    ip_api=None, port_api=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, 
                                parameters, ip_api, port_api)
    
    def process_results(self, df):
        """
        Método encargado del tratamiento de los datos obtenidos
        :param df dataframe con los datos obtenidos
        :return list lista de artículos obtenidos
        """
        articles = []
        names = []
        article: Article = None
        for index, elem in df.iterrows():
            doc = elem['nombreDoc.value']
            if doc not in names:
                    names.append(doc)
                    article = Article(doc=doc)
                    article.set_properties(elem)
                    articles.append(article)
            else:
                    article.add_author(elem)                
        return articles

    def execute(self):
        """
        Método encargado de la ejecución del proceso
        """
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0
        articles = []
        
        start_date = self.parameters['start_date']
        date1 = start_date.replace('-','')
        end_date = self.parameters['end_date']
        date2 = end_date.replace('-','')
        self.notify_update(
            "El proceso de extracción de artículos científicos ha comenzado.")

        edma = cs.get_edma(self.ip_api, self.port_api)
        if edma:
            df = edma.get_all_articles(date1, date2)
            self.log.completed = 25
            try:
                if not df.empty:
                    self.notify_update(
                                    "Extracción de artículos: Comienza el tratamiento de los datos obtenidos.")
                    articles = self.process_results(df)
                    self.log.completed = 50
                else:
                    self.notify_update(
                                    'No se ha obtenido ningún artículo en el rango de fechas indicado.')
            except Exception as e:
                self.notify_update(
                        'Error al obtener los artículos con el rango de fechas indicado.')
                self.notify_update(str(e))        
                self.log.state = "ERROR"
        else:
            self.notify_update('ERROR al obtener parámetros de Hércules-EDMA')
            self.log.state = "ERROR"
                
        self.log.completed = 100
        self.notify_update(
            "El proceso de extracción de artículos científicos ha finalizado.")
        self.result = articles
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED

    def kill(self):
        pass

    def resume(self):
        pass

    def pause(self):
        pass
