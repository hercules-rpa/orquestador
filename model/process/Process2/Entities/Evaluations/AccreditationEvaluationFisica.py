from model.process.Process2.Entities.Evaluations.AccreditationEvaluationRelevance import AccreditationEvaluationRelevance
from model.process.Process2.Entities.Accreditation import Accreditation

class CriterionEvaluationFisica():
    """
    Criterio de evaluación de la acreditación de la comisión de Física:

    min_arts: mínimo de artículos que tiene que tener
    num_t1: el número de artículos mínimo que deben estar en el primer tercil.
    num_t1_t2: el número de artículos mínimo que deben estar en el primer y segundo tercil.
    min_t1: número mínimo de artículos en el primer tercil
    """
    def __init__(self, min_arts:int, num_t1:int, num_t1_t2:int, min_t1:int):
        self.min_arts = min_arts
        self.num_t1 = num_t1
        self.num_t1_t2 = num_t1_t2
        self.min_t1 = min_t1

class AccreditationEvaluationFisica(AccreditationEvaluationRelevance):
    """
    Resultado de la comisión de Física para una solicitud de acreditación.
    """
    def __init__(self, scientific_production: list = [], positive: bool = False,
    accreditation: Accreditation = None, observation: str = '',assessment: str = '', 
    arts_t1: list = [], arts_t2: list = [], criterion: CriterionEvaluationFisica = None):
        super().__init__(scientific_production=scientific_production, positive=positive, accreditation=accreditation, observation=observation, assessment=assessment)
        self.arts_t1 = arts_t1
        self.arts_t2 = arts_t2
        self.criterion = criterion

    def get_publications_t1(self):
        """
        Obtiene los artículos que forman parte de las publicaciones en t1 que deben estar en la producción principal.
        :return lista de publicaciones en el primer tercil
        """
        results = []
        if self.arts_t1:
            for publication in self.arts_t1:
                results.append(publication)
                if len(results) == self.criterion.num_t1:
                    return results
        return results

    def get_publications_t1_t2(self):
        """
        Obtiene los artículos que forman parte de las publicaciones en t1 y t2 que deben estar en la producción principal.
        :return list lista de publicaciones en el primer y segundo tercil
        """
        results = []
        if self.scientific_production:
            if self.arts_t1:
                for publication in self.arts_t1:
                    results.append(publication)
                    if len(results) == self.criterion.num_t1_t2:
                        return results
            if self.arts_t2:
                for publication in self.arts_t2:
                    results.append(publication)
                    if len(results) == self.criterion.num_t1_t2:
                        return results                
        return results

    def get_substitute_production(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        :return lista de producción sustitutoria
        """
        results = []
        if self.arts_t1 or self.arts_t2:
            p1 = self.get_publications_t1()
            p1_p2 = self.get_publications_t1_t2()
            for publication in self.scientific_production:
                if publication not in p1 and publication not in p1_p2:
                    results.append(publication)
        return results
        