import time
from model.process.Proceso1.Entidades.Article import Article
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus
from model.EDMA import EDMA


NAME = "Extract Articles"
DESCRIPTION = "Proceso que extrae artículos científicos."
REQUIREMENTS = []
ID = ProcessID.EXTRACT_ARTICLES.value


class ProcessExtractArticles(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    
    def process_results(self, df):
        """Función encargada del tratamiento de los datos"""
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
        """Función encargada de la ejecución del proceso"""
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.log.completed = 0
        articles = []
        # obtención parametros
        start_date = self.parameters['start_date']
        print('start_date: ' + start_date)
        date1 = start_date.replace('-','')
        end_date = self.parameters['end_date']
        date2 = end_date.replace('-','')
        # obtención de artículos accediendo a ED
        self.notificar_actualizacion(
            "El proceso de extracción de artículos científicos ha comenzado.")

        edma = EDMA()
        if self.ping(edma.IP):
            print('inicio: ' + date1 + ' final: ' + date2)
            df = edma.get_all_articles(date1, date2)
            self.log.completed = 25
            # tratto. de la respuesta
            try:
                if not df.empty:
                    self.notificar_actualizacion(
                                "Extracción de artículos: Comienza el tratamiento de los datos obtenidos.")
                    articles = self.process_results(df)
                    self.log.completed = 50
                else:
                    self.notificar_actualizacion(
                                'No se ha obtenido ningún artículo en el rango de fechas indicado.')
            except Exception as e:
                self.notificar_actualizacion(
                    'Error al obtener los artículos con el rango de fechas indicado.')
                self.notificar_actualizacion(str(e))
        else:
            self.notificar_actualizacion('ERROR: el proceso no dispone de conexión con ED.')
            self.log.state = "ERROR"
        self.log.completed = 100
        self.notificar_actualizacion(
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
