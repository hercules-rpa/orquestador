from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation

class CriterionEvaluationCienciasComportamiento():
    """
    Criterio de evaluación de la acreditación de la comisión de Ciencias del Comportamiento:

    num_art: número de artículos necesarios que tiene que tener el investigador.
    min_art: mínimo de artículos que tiene que tener el investigador.
    num_t1_t2: el número de artículos que deben estar en el primer y segundo tercil.
    min_t1_t2: el número de artículos mínimo que deben estar en el primer y segundo tercil.
    num_authorship: el número de autorías que tiene que tener el investigador.
    min_authorship: el número mínimo de autorías que tiene que tener un investigador.
    min_percent: número mínimo de porcentaje que tiene que tener para cumplir el criterio.
    """
    def __init__(self, num_art: int, min_art: int, num_t1_t2: int, min_t1_t2: int, 
    num_authorship: int, min_authorship: int, min_percent: int):
        self.num_art = num_art
        self.min_art = min_art
        self.num_t1_t2 = num_t1_t2
        self.min_t1_t2 = min_t1_t2
        self.num_authorship = num_authorship
        self.min_authorship = min_authorship
        self.min_percent = min_percent

class AccreditationEvaluationCienciasComportamiento(AccreditationEvaluation):
    """
    Resultado de la evaluación de la comisión de Ciencias del Comportamiento de una solicitud de acreditación
    """
    def __init__(self, scientific_production:list = [], positive:bool=False, 
    accreditation:Accreditation=None, observation:str='', publications_authorship:list=[], 
    publications_t1_t2:list=[], criterion: CriterionEvaluationCienciasComportamiento=None):
        super().__init__(scientific_production=scientific_production, positive = positive, accreditation=accreditation, observation=observation)
        self.publications_authorship = publications_authorship
        self.publications_t1_t2 = publications_t1_t2
        self.criterion = criterion

    def get_publications_t1_t2(self):
        """
        Método para obtener las publicaciones del tercil primero y segundo para la producción principal.
        :return list lista de publicaciones en el tercil 1 y 2
        """
        p_t1_t2 = []
        if self.publications_t1_t2:
            for publication in self.publications_t1_t2:
                if publication.get_tertile() == 1 or publication.get_tertile() == 2:
                    p_t1_t2.append(publication)
                    if len(p_t1_t2) == self.criterion.min_t1_t2:
                        return p_t1_t2
        return p_t1_t2

    def get_publications_authorship(self):
        """
        Método para obtener las publicaciones que cumplan el criterio de autoría.
        :return list lista de publicaciones 
        """
        p_authorship = []
        if self.publications_authorship:
            for publication in self.publications_authorship:
                p_authorship.append(publication)
                if publication == self.criterion.num_authorship:
                    return p_authorship
        return p_authorship

    def get_substitute_production(self):
        """
        Método para obtener la producción sustitutoria.
        :return list lista de producción sustitutoria
        """
        p_substitute = []
        p_t1_t2 = self.get_publications_t1_t2()
        p_authorship = self.get_publications_authorship()
        if self.scientific_production:
            for publication in self.scientific_production:
                if publication not in p_t1_t2 and publication not in p_authorship:
                    p_substitute.append(publication)
        return p_substitute