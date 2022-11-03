from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation

"""
Criterio de evaluación de la acreditación de la comisión de Otras Especialidades Sanitarias,
refleja:
min_arts: el número mínimo de artículos que tiene que tener
num_authorship: el número mínimo de artículos con autoría preferente
num_authorship_t1: el número mínimo de artículos con autoría preferente que deben estar en el primer tercil.
"""
class CriterionEvaluationOtrasEspecialidadesSanitarias():
    def __init__(self, min_arts:int, num_authorship: int, num_authorship_t1: int):

        self.min_arts = min_arts
        self.num_authorship = num_authorship
        self.num_authorship_t1 = num_authorship_t1

class AccreditationEvaluationOtrasEspecialidadesSanitarias(AccreditationEvaluation):
    """
    Esta clase es la encargada de realizar la evaluación del área de Otras especialidades sanitarias.
    """
    def __init__(self, scientific_production: list = [], positive: bool = False, 
                acreditacion: Accreditation = None, observation: str = '', 
                assessment: str = '', articles_authorship: list = [], articles_authorship_t1: list = [],
                criterion: CriterionEvaluationOtrasEspecialidadesSanitarias = None):
        super().__init__(scientific_production=scientific_production, positive=positive, 
                                        accreditation=acreditacion, observation=observation, assessment=assessment)
        self.articles_authorship = articles_authorship
        self.articles_authorship_t1 = articles_authorship_t1
        self.assessment = assessment
        self.criterion = criterion

    def get_publications_authorship_t1(self):
        """
        Método que obtiene las publicaciones con autoria preferente en el tercil 1 que debe estar
        en la producción cientifíca del informe
        :return list lista de publicaciones que pertenecen al primer tercil y tienen autoría preferente
        """
        num = self.criterion.num_authorship_t1
        if self.articles_authorship_t1:            
            if len(self.articles_authorship_t1) >= num:
                return self.articles_authorship_t1[0:num]
            return self.articles_authorship_t1[0:]
        return None

    def get_publications_authorship(self):
        """
        Método que obtiene las publicaciones con autoria preferente que deben estar en 
        la producción científica del informe.
        :return list lista de publicaciones que tienen autoría preferente
        """
        result = []
        articles_authorship_t1 = self.get_publications_authorship_t1()
        num = self.criterion.num_authorship
        if self.articles_authorship and articles_authorship_t1:
            result = self.articles_authorship            

            if len(self.articles_authorship) >= (num - len(articles_authorship_t1)): 
                for art in articles_authorship_t1:
                    if art in result:
                        result.remove(art)
                if len(result) >= num:            
                    result = result[0:num]
            else:
                result = self.articles_authorship[0:]
        return result

    def get_substitute_production(self):
        """
        Método que obtiene las publicaciones en el tercer y cuarto cuartil que deben estar
        en la producción del informe
        :return list lista de producción sustitutoria
        """
        result = self.scientific_production
        if result:
            authorship = self.get_publications_authorship()
            if authorship:
                for art in authorship:
                    result.remove(art)
            authorship = self.get_publications_authorship_t1()
            if authorship:
                for art in authorship:
                    result.remove(art)        
        return result