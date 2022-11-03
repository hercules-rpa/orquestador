from model.process.Process2.Entities.RO import RO
from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation, ClassificationInfo
from model.process.Process2.Entities.Committee.Committee import Committee


class CommitteeIngenierias(Committee):
    """
    Comité que evalúa las solicitudes de sexenios de las áreas de Ingenierías de la comunicación, computación y electrónica. (6.2)
    """
    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] scientific_production: listado de artículos de un investigador.
        :return SexenioEvaluation evaluación del sexenio.        
        """
        eval = SexenioEvaluation(scientific_production=scientific_production, 
        parameters=self.get_criterion())
        clasification = eval.get_classification_production()

        tupl = self.criterion1(clasification, eval.parameters)
        if tupl and tupl[0] > 0:
            eval.punctuation = tupl[0]
            eval.main_production = tupl[1]
        else:
            tupl = self.criterion2(clasification, eval.parameters)
            if tupl and tupl[0] > 0:
                eval.punctuation = tupl[0]
                eval.main_production = tupl[1]
        return eval

    def get_punctuation(self, elements, punctuations: dict) -> int:
        """
        Método que calcula la puntuación total de una colección de artículos.
        :param [] lista de artículos
        :param dict puntuaciones
        :result int puntuación obtenida
        """
        punctuation = 0
        if elements:
            for elem in elements:
                punctuation += self.get_punctuation_article(elem, punctuations)
        return punctuation

    def get_punctuation_article(self, element: RO, punctuations: dict) -> int:
        """
        Método que calcula la puntuación que tiene un artículo en base al cuartil al que pertenece y al número de autores que tiene.
        :param RO artículo que se evaluará
        :param dict puntuaciones
        :result int puntuación obtenida
        """
        punctuation = 0
        if element.get_quartile() == 1:
            punctuation = punctuations['puntuacion_q1']
        if element.get_quartile() == 2:
            punctuation = punctuations['puntuacion_q2']
        elif element.get_quartile() == 3:
            punctuation = punctuations['puntuacion_q3']
        elif element.get_quartile() == 4:
            punctuation = punctuations['puntuacion_q4']

        punctuation -= self.get_subtract_punctuation(element)
        return punctuation

    def get_subtract_punctuation(self, element: RO) -> int:
        """
        Método que calcula lo que hay que descontar de la puntuación siguiendo los siguientes criterios basados en la cantidad de firmantes:
        - Si firman hasta 6 personas no se descontará nada
        - De 7 al 10: salvo casos justificados, por cada firma más, se descontará 0,5 puntos.
        - De 11 en adelante: salvo casos justificados, por cada firma más, se descontará 0,25 puntos.

        :param RO elemento que se analizará
        :return int puntuación que se debe descontar
        """
        result = 0
        if element.authors_number >= 7 and element.authors_number <= 10:
            result = (element.authors_number-6)*0.5
        elif element.authors_number >= 11:
            result = (element.authors_number-11)*0.25
        return result

    def criterion1(self, clasification: ClassificationInfo, parameters: dict) -> tuple([int, list]):
        """
        Método que evalúa el siguiente criterio:
        - Dos aportaciones de alta relevancia y una de relevancia media.
        :param ClassificationInfo clasificación de la producción científica del investigador.
        :param dict diccionario de parámetros
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal
        """
        results = []
        punctuation = 0
        criterion = parameters['criterio1']
        if clasification and len(clasification.publications_q1) >= criterion['num_relevancia_alta'] and \
            len(clasification.publications_q2) >= criterion['num_relevancia_media']:
            
            results = clasification.publications_q1[0:criterion['num_relevancia_alta']]
            results += clasification.publications_q2[0:criterion['num_relevancia_media']]
            punctuation = self.get_punctuation(results, parameters['puntuaciones'])

        return (punctuation, results)

    def criterion2(self, clasification: ClassificationInfo, parameters:dict) -> tuple([int, list]):
        """
        Método que evalúa el siguiente criterio:
        - Una aportación de alta relevancia y tres de relevancia media
        :param ClassificationInfo clasificación de la producción científica del investigador.
        :param dict diccionario de parámetros
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal
        """
        results = []
        punctuation = 0
        criterion = parameters['criterio2']
        if clasification and len(clasification.publications_q1) >= criterion['num_relevancia_alta'] and \
            len(clasification.publications_q2) >= criterion['num_relevancia_media']:
            
            results = clasification.publications_q1[0:criterion['num_relevancia_alta']]
            results += clasification.publications_q2[0:criterion['num_relevancia_media']]
            punctuation = self.get_punctuation(results, parameters['puntuaciones'])
        
        return (punctuation, results)
