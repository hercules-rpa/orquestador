from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.Committee.CommitteeEstudiosGenero import CommitteeEstudiosGenero
from model.process.Process2.Entities.RO import RO

class CommitteeCienciasComportamiento(CommitteeEstudiosGenero):
    """
    Comité que evalúa el área de Ciencias del Comportamiento dentro del comité 7.1.
    """
    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] scientific_production: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        return super().get_evaluation_sexenio(scientific_production)

    def get_penalty_punctuation(self, element: RO, punctuation: int, penalties:dict):
        """
        Método que calcula la penalización sobre la puntuación basandose en el nº de autores
        y en el nº de firmante del investigador.
            -1-6 indiferente: no se resta
            -7 o más autores, en 1ª, 2ª o última posición: no se resta
            -7 o más autores, entre la 3ª y la última: se resta un 25%
        :param RO elemento a analizar
        :param int punctuation para calcular la penalización
        :return int penalties obtenida.
        """
        penalty = 0
        if element.authors_number >= 7:
            if element.author_position >= 3:
                penalty = punctuation * penalties['n_autores_max_7']
        return penalty
