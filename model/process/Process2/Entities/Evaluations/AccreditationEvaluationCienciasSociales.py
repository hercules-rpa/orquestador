from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation

class CriterionEvaluationCienciasSociales():
    """
    Criterio de evaluación de la acreditación de la comisión de Ciencias Sociales:
    num_art_A: número de artículos que tiene que tener el investigador para la valoración A.
    num_art_BC: número de artículos que tiene que tener el investigador para la valoración BC.
    num_t1_t2: el número de artículos que deben estar en el primer y segundo tercil.
    min_t1_t2: el número de artículos mínimo que deben estar en el primer y segundo tercil.
    min_percent: el número mínimo de porcentaje que tiene que considerar el criterio.
    """
    def __init__(self, num_art_A: int, num_art_BC: int, num_t1_t2_A: int, 
    num_t1_BC: int, num_t2_BC: int, min_percent: int):
        self.num_art_A = num_art_A
        self.num_art_BC = num_art_BC
        self.num_t1_t2_A = num_t1_t2_A
        self.num_t1_BC = num_t1_BC
        self.num_t2_BC = num_t2_BC
        self.min_percent = min_percent
        

class AccreditationEvaluationCienciasSociales(AccreditationEvaluation):
    """
    Resultado de la comisión de Ciencias Sociales para una solicitud de acreditación.
    """
    def __init__(self, scientific_production: list = [], positive: bool = False, 
    accreditation: Accreditation = None, observation: str = '', assessment: str = '', 
    publications_n1: list = [], publications_n2: list = [], criterion: CriterionEvaluationCienciasSociales=None):
        super().__init__(scientific_production=scientific_production, positive=positive, 
        accreditation=accreditation, observation=observation)
        self.publications_n1 = publications_n1
        self.publications_n2 = publications_n2
        self.assessment = assessment
        self.criterion = criterion

    def get_publications_n1_n2(self):
        """
        Método para obtener las publicaciones del tercil primero y segundo en la producción principal.
        :return list lista de publicaciones
        """
        p_n1_n2 = []
        if self.publications_n1 or self.publications_n2:
            for article in self.publications_n1:
                p_n1_n2.append(article)
                if len(p_n1_n2) == self.criterion.num_t1_t2_A:
                    return p_n1_n2
            for article in self.publications_n2:
                p_n1_n2.append(article)
                if len(p_n1_n2) == self.criterion.num_t1_t2_A:
                    return p_n1_n2
        return p_n1_n2

    def get_substitute_production(self):
        """
        Método para obtener la producción científica sustitutoria para esta comisión de Ciencias Sociales.
        :return list lista de producción sustitutoria
        """
        result = []
        if self.scientific_production:
            p_n1_n2 = self.get_publications_n1_n2()
            for article in self.scientific_production:
                if article not in p_n1_n2:
                    result.append(article)
        return result
