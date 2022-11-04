from model.process.Process2.Entities.RO import RO
from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.Committee.Committee import Committee


class CommitteeCienciasBiomedicas(Committee):
    """
    Comité que se encarga de la evaluación de la solicitud de sexenios del área de 
    Ciencias Biomédicas - id (5)'.
    """

    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    def criterion1(self, high_relevance, medium_relevance, parameters: dict) -> tuple([int, list]):
        """
        Método que comprueba la primera combinación para la solicitud de un sexenio.
        2Q1 + 3Q2

        :param [] high_relevance: artículos que pertenecen al Q1.
        :param [] medium_relevance: artículos que pertenecen al Q2.
        :param dict parameters diccionario de parámetros del criterio.
        :return tuple [int, list] que devuelve la puntuación total y la lista de artículos seleccionados.

        """
        punctuation = 0
        articles = []
        criterion = parameters['criterio1']
        if len(high_relevance) >= criterion['num_relevancia_alta']:
            articles = high_relevance[0:criterion['num_relevancia_alta']]
            if len(medium_relevance) >= criterion['num_relevancia_media']:
                articles += medium_relevance[0:criterion['num_relevancia_media']]
                punctuation = self.get_punctuation_total(
                    articles, parameters['puntuaciones'])
        return (punctuation, articles)

    def criterion2(self, high_relevance, medium_relevance, low_relevance, parameters: dict) -> tuple([int, list]):
        """
        Método que comprueba 3Q1 + 1Q2 + 1Q3
        :param [] high_relevance: artículos que pertenecen al Q1.
        :param [] medium_relevance: artículos que pertenecen al Q2.
        :param [] low_relevance: artículos que pertenecen al Q3-Q4.
        :param dict diccionario de parámetros del criterio.
        :return tupla [int, list] que devuelve la puntuación total y la lista de artículos seleccionados.    
        """
        punctuation = 0
        articles = []
        criterion = parameters['criterio2']
        if len(high_relevance) >= criterion['num_relevancia_alta']:
            articles = high_relevance[0:criterion['num_relevancia_alta']]
            if len(medium_relevance) >= criterion['num_relevancia_media']:
                articles += medium_relevance[0:criterion['num_relevancia_media']]
                if len(low_relevance) >= criterion['num_relevancia_baja']:
                    articles += low_relevance[0:criterion['num_relevancia_baja']]

                    punctuation = self.get_punctuation_total(
                        articles, parameters['puntuaciones'])
        return (punctuation, articles)

    def criterion3(self, high_relevance, low_relevance, parameters) -> tuple([int, list]):
        """
        Método que comprueba la primera combinación para la solicitud de un sexenio.
        4Q1 + 1Q3
        :param [] high_relevance: artículos que pertenecen al Q1.
        :param [] low_relevance: artículos que pertenecen al Q3-Q4.
        :param dict diccionario de parámetros del criterio
        :return tupla [int, list] que devuelve la puntuación total y la lista de artículos seleccionados.
        """
        punctuation = 0
        articles: list = []
        criterion = parameters['criterio3']
        if len(high_relevance) >= criterion['num_relevancia_alta']:
            articles = high_relevance[0:criterion['num_relevancia_alta']]
            if len(low_relevance) >= criterion['num_relevancia_baja']:
                articles += low_relevance[0:criterion['num_relevancia_baja']]
                punctuation = self.get_punctuation_total(
                    articles, parameters['puntuaciones'])

        return (punctuation, articles)

    def get_punctuation_total(self, elements: list, punctuations: dict) -> int:
        """
        Método que obtiene la puntuación total de una lista de elementos.
        :param list lista de elementos
        :param dict puntuaciones
        """
        punctuation = 0
        if elements:
            for element in elements:
                punctuation += self.get_punctuation(element, punctuations)
        return punctuation

    def get_punctuation(self, element: RO, punctuations: dict) -> int:
        """
        Método que obtiene la puntuación del elemento
        :param RO elemento a analizar
        :param dict puntuaciones
        :result int puntuación obtenida
        """
        punctuation = 0
        quartile = element.get_quartile()
        if quartile == 1:
            punctuation = punctuations['puntuacion_q1']
        elif quartile == 2:
            punctuation = punctuations['puntuacion_q2']
        elif quartile == 3:
            punctuation = punctuations['puntuacion_q3']
        elif quartile == 4:
            punctuation = punctuations['puntuacion_q4']
        return punctuation

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] scientific_production: listado de artículos de un investigador.
        :return SexenioEvaluation evaluación del sexenio.        
        """
        evaluation = SexenioEvaluation(scientific_production=scientific_production,
                                       parameters=self.get_criterion())

        if scientific_production:
            high_relevance = []
            medium_relevance = []
            low_relevance = []

            for art in scientific_production:
                quartile = art.get_quartile()
                if quartile == 1:
                    high_relevance.append(art)
                elif quartile == 2:
                    medium_relevance.append(art)
                else:
                    low_relevance.append(art)

            result = self.criterion1(
                high_relevance, medium_relevance, evaluation.parameters)
            if result and result[0] > 0:
                evaluation.punctuation = result[0]
                evaluation.main_production = result[1]
            else:
                result = self.criterion2(
                    high_relevance, medium_relevance, low_relevance, evaluation.parameters)
                if result[0] > 0:
                    evaluation.punctuation = result[0]
                    evaluation.main_production = result[1]
                else:
                    result = self.criterion3(
                        high_relevance, low_relevance, evaluation.parameters)
                    if result[0] > 0:
                        evaluation.punctuation = result[0]
                        evaluation.main_production = result[1]

        return evaluation
