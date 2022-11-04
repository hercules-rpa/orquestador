from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation

class CriterionEvaluationQuimica():
    """
    Criterio de evaluación de la acreditación de la comisión de Física:

    min_publications: Número mínimo de publicaciones.
    t1_publications: el número de artículos mínimo que deben estar en el primer tercil.
    t1_ap_publications: el número de artículos mínimo como primer autor.
    max_year: el número de años mínimos para seleccionar los autores.
    """
    def __init__(self, min_publications:int, t1_publications:int, t1_ap_publications:int,
    max_year:int):
        self.min_publications = min_publications
        self.t1_publications = t1_publications
        self.t1_ap_publications = t1_ap_publications
        self.max_year = max_year

class AccreditationEvaluationQuimica(AccreditationEvaluation):
    """
    Resultado de la comisión de Química para una solicitud de acreditación.
    """
    def __init__(self, scientific_production: list = [], positive: bool = False, 
    accreditation: Accreditation = None, observation: str = '', 
    assessment: str = '', arts_t1: list = [], arts_first_author: list = [], 
    criterion: CriterionEvaluationQuimica = None):
        super().__init__(scientific_production=scientific_production, positive=positive, accreditation=accreditation, observation=observation, assessment=assessment)
        self.art_t1 = arts_t1
        self.art_first_author = arts_first_author
        self.criterion = criterion

    def get_publications_t1(self):
        """
        Método para conseguir los artículos del tercil uno necesarios para la producción principal.
        :return list lista de publicaciones que pertenecen al primer tercil 
        """
        results = []
        if self.art_t1:
            for publication in self.art_t1:
                results.append(publication)
                if len(results) == self.criterion.t1_publications:
                    return results
        return results

    def get_publications_first_author(self):
        """
        Método para conseguir las publicaciones en las que eres primer autor para la producción principal.
        :return list lista de publicaciones en las que el investigador es el primer autor
        """
        results = []
        if self.art_first_author:
            for publication in self.art_first_author:
                results.append(publication)
                if len(results) == self.criterion.t1_ap_publications:
                    return results
        return results

    def get_substitute_production(self):
        """
        Método que prepara las publicaciones de producción sustitutoria.
        :return list lista de producción sustitutoria
        """
        results = []
        p1 = self.art_t1
        p_primero = self.art_first_author
        if p1 or p_primero:
            for publication in self.scientific_production:
                if publication not in p1 and publication not in p_primero:
                    results.append(publication)
        return results
