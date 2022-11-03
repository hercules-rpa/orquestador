from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation

class CriterionEvaluationFilologiaLinguistica():
    """
    Criterio de evaluación de la acreditación de la comisión de Filología Lingüística

    num_arts: número de artículos que tiene que tener el investigador.
    num_t1: número de artículos mínimo que deben estar en el primer tercil.
    num_porcentaje: porcentaje mínimo
    """

    def __init__(self, num_arts: int, num_t1: int, min_percent: int):
        self.num_arts = num_arts
        self.num_t1 = num_t1
        self.min_percent = min_percent


class AccreditationEvaluationFilologiaLinguistica(AccreditationEvaluation):
    """
    Resultado de la comisión de Filología y Lingüistica para una solicitud de acreditación.
    """
    def __init__(self, scientific_production: list = [], positive: bool = False, 
    accreditation: Accreditation = None, observation: str = '', publications_n1: list = [],
    criterion: CriterionEvaluationFilologiaLinguistica=None):
        super().__init__(scientific_production=scientific_production, positive=positive, accreditation=accreditation, observation=observation)
        self.publications_n1 = publications_n1
        self.criterion = criterion

    def get_publications_n1(self):
        """
        Obtiene los artículos que forman parte de las publicaciones de nivel 1 que deben estar en la prucción principal
        :return list lista de publicaciones en el nivel 1
        """
        num = self.criterion.num_t1
        if self.publications_n1:
            if len(self.publications_n1) >= num:
                return self.publications_n1[0:num]
            return self.publications_n1[0:]
        return None

    def get_substitute_production(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        :return list lista de producción sustitutoria
        """
        result = []
        if self.publications_n1:
            p_n1 = self.get_publications_n1()
            for publication in self.scientific_production:
                if publication not in p_n1:
                    result.append(publication)
        return result
        