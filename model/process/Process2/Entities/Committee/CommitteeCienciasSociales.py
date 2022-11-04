from model.process.Process2.Entities.Committee.Committee import Committee
from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.RO import RO

class CommitteeCienciasSociales(Committee):
    """
    Comité que evalúa el área de Ciencias Sociales, Políticas y Comunicación dentro del comité 7.1.
    """
    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] scientific_production: listado de artículos de un investigador.
        :return SexenioEvaluation evaluación del sexenio.        
        """
        evaluation = SexenioEvaluation(scientific_production=scientific_production, parameters=self.get_criterion('cienciassociales'))

        if len(scientific_production) >= 5:
            evaluation.main_production = scientific_production[0:5]

            for art in evaluation.main_production:
                evaluation.punctuation += self.get_punctuation_article(art, evaluation.parameters)  
        return evaluation
        
    def get_penalty_punctuation(self, element:RO, punctuation:int, penalties:dict): 
        """
        Método que calcula la penalización sobre la puntuación basandose en el nº de autores
        y en el nº de firmante del investigador.
            -hasta 3: no se resta
            -de 4 a 6, 1,2, y 3: no se resta
            -de 4 a 6, posiciones 4,5, y 6: se resta un 25%
            -de 7 en adelante: se resta un 50 %
        :param RO elemento a analizar
        :param int puntuación para calcular la penalización
        :return int penalización obtenida.
        """
        penalty = 0
        if element.authors_number > 4 and element.authors_number <= 6: 
            if element.author_position >= 4:
                penalty = punctuation * penalties['n_autores_4_6']
        elif element.authors_number >= 7:
            if element.author_position >= 4:
                penalty = punctuation * penalties['n_autores_4_6']
            elif element.author_position >= 7:
                penalty = punctuation * penalties['n_autores_max_7']
        return penalty

    def get_punctuation_article(self, element:RO, parameters):
        """
        Método que obtiene la puntuación de un artículo.
        :param RO artículo
        :param dict parámetros
        :return int puntuación obtenida por el artículo
        """
        if element and parameters and 'puntuaciones' in parameters:
            punctuations = parameters['puntuaciones']
            quartile = element.get_quartile()
            puntuacion = 0
            if quartile == 1:
                puntuacion = punctuations['puntuacion_q1']
            elif quartile == 2:
                puntuacion = punctuations['puntuacion_q2']
            elif quartile == 3:
                puntuacion = punctuations['puntuacion_q3']
            elif quartile == 4:
                puntuacion = punctuations['puntuacion_q4']        

        puntuacion -= self.get_penalty_punctuation(element, puntuacion, parameters['penalizaciones'])        
        return puntuacion