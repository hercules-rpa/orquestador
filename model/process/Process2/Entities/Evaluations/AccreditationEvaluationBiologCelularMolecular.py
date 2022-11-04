from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation

"""
Criterio de evaluación de la acreditación de la comisión de Biología Celular y Molecular,
refleja:
minimo_articulos: mínimo de artículos que tiene que tener
num_t1: el número de artículos mínimo que deben estar en el primer tercil.
num_autoria: el número de artículos mínimo con autoría preferente.
"""
class CriterionEvaluationBiologiaCelularMolecular():
    def __init__(self, min_art_100:int, num_t1_100:int, num_authorship_100:int,
        min_art_75:int, num_t1_75:int, num_authorship_75:int):
        self.min_art_100 =min_art_100 
        self.num_t1_100 = num_t1_100
        self.num_authorship_100 = num_authorship_100
        self.min_art_75 =min_art_75
        self.num_t1_75 = num_t1_75
        self.num_authorship_75 = num_authorship_75

"""
Resultado de la evaluación de la comisión de Biología Celular y Molecular de una solicitud de acreditación
"""
class AccreditationEvaluationBiologCelularMolecular(AccreditationEvaluation):
    def __init__(self, scientific_production:list = [], positive:bool=False, 
        accreditation:Accreditation=None, observation:str='', assessment:str='',
        publications_t1:list=[], publications_authorship:list=[], 
        criterion:CriterionEvaluationBiologiaCelularMolecular=None):
        super().__init__(scientific_production, positive, accreditation, observation)
        self.publications_t1 = publications_t1
        self.publications_authorship = publications_authorship
        self.assessment = assessment
        self.criterion = criterion

    def get_publications_t1(self):
        """
        Método que obtiene las publicaciones en el primer tercil que deben estar en 
        la producción principal del informe.
        :return list lista de publicaciones en el tercil 1
        """
        num = self.criterion.num_t1_100
        if self.publications_t1:
            if len(self.publications_t1) < num: 
                num = self.criterion.num_t1_75

            if len(self.publications_t1) >= num:             
                return self.publications_t1[0:num]
            return self.publications_t1[0:]
        return None
    
    def get_publications_authorship(self):
        """
        Método que obtiene las publicaciones con autoria preferente que deben estar en 
        la producción científica del informe.
        :return list lista de publicaciones con autoria preferente
        """
        num = self.criterion.num_authorship_100
        if self.publications_authorship:
            if len(self.publications_authorship) < num: 
                num = self.criterion.num_authorship_75

            if len(self.publications_authorship) >= num:             
                return self.publications_authorship[0:num]
            return self.publications_authorship[0:]
        return None


    def get_substitute_production(self):
        """
        Método para obtener la producción sustitutoria.
        :return list lista de producción sustitutoria
        """
        result = self.scientific_production
        if result:
            elements = self.get_publications_t1()
            authorship = self.get_publications_authorship()
            for art in authorship:
                if art not in elements:
                    elements.append(art)
            
            if elements:
                for elem in elements:
                    result.remove(elem)
        
        return result
