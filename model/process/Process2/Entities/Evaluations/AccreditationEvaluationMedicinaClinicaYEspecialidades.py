from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation

"""
Criterio de evaluación de la acreditación de la comisión de Medicina Clinica y Especialidades Clinicas,
refleja:
min_arts: mínimo de artículos que tiene que tener
num_t1: el número de artículos mínimo que deben estar en el primer tercil.
num_authorship: el número de artículos mínimo con autoría preferente.
num_authorship_t1: el número de artículos mínimo con autoría prefente en el primer tercil.
"""
class CriterionEvaluationMedicinaClinicaYespecialidades():
    def __init__(self, min_arts:int, num_t1:int, num_authorship:int, num_authorship_t1:int):
        
        self.min_arts = min_arts
        self.num_t1 = num_t1
        self.num_authorship = num_authorship
        self.num_authorship_t1 = num_authorship_t1
"""
Resultado de la comisión de Medicina clínica y Especialidades clínicas para una solicitud de acreditación.
"""

class AccreditationEvaluationMedicinaClinicaYEspecialidades(AccreditationEvaluation):
    def __init__(self, scientific_production: list = [], positive: bool = False, 
                accreditation: Accreditation = None, observation: str = '', 
                assessment: str = '', arts_t1: list = [], arts_t2: list = [], 
                arts_authorship: list = [], arts_authorship_t1: list = [],
                criterion:CriterionEvaluationMedicinaClinicaYespecialidades=None):
        super().__init__(scientific_production=scientific_production, positive=positive, 
                                        accreditation=accreditation, observation=observation, assessment=assessment)
        self.arts_t1 = arts_t1
        self.arts_t2 = arts_t2
        self.arts_authorship = arts_authorship
        self.arts_authorship_t1 = arts_authorship_t1
        self.criterion = criterion

    def get_publications_t1(self):
        """
        Método que obtiene las publicaciones en el primer tercil que deb estar en 
        la producción principal del informe
        :return lista de publicaciones en el primer tercil
        """
        num = self.criterion.num_t1
        if self.arts_t1:
            if len(self.arts_t1) >= num:
                return self.arts_t1[0:num]
            return self.arts_t1[0:]
        return None
    
    def get_publications_authorship(self):
        """
        Método que obtiene las publicaciones con autoria preferente que deben estar en 
        la producción científica del informe
        :return lista de publicaciones con autoría preferente
        """
        num = self.criterion.num_authorship
        result = []
        articles_authorship_t1 = self.get_publications_authorship_t1()

        if len(self.arts_authorship) >= (num - len(articles_authorship_t1)):
            result = self.arts_authorship
            for art in self.arts_authorship_t1:
                if art in result:
                    result.remove(art)     
            if len(result) > num:
                result = result[0:num]  
        else:
            result = self.arts_authorship[0:]       

        return result

    def get_publications_authorship_t1(self):
        """
        Método que obtiene las publicaciones con autoria preferente en el tercil 1 que deben
        estar en la producción científica del informe
        :return list lista de publicaciones que pertenecen al primer tercil y tienen autoría preferente
        """
        num = self.criterion.num_authorship_t1
        if self.arts_authorship_t1:
            if len(self.arts_authorship_t1) >= num:
                return self.arts_authorship_t1[0:num]
            return self.arts_authorship_t1[0:]
        return None

    def get_substitute_production(self):
        """
        Método que obtiene las publicaciones en el tercer y cuarto cuartil que deben estar
        en la producción del informe
        :return list lista de producción sustitoria
        """
        result = self.scientific_production
        if result:
            authorship_t1 = self.get_publications_t1()
            authorship = self.get_publications_authorship()

            for art in authorship_t1:
                if art in result: 
                    result.remove(art)

            for art in authorship:
                if art in result:
                    result.remove(art)           
                               
        return result