
from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation
"""
El criterio de relevancia define el número de artículos que se necesita de cada tipo
para que una evaluación sea positiva.
"""
class CriterionEvaluationRelevance():
    def __init__(self, num_relevant:int, num_m_relevant:int):
        self.num_relevant = num_relevant
        self.num_m_relevant = num_m_relevant
        
"""
Evaluación resultante de analizar una solicitud de acreditación de las comisiones que tienen como criterio las relevancias de las publicaciones.
"""
class AccreditationEvaluationRelevance(AccreditationEvaluation):
    def __init__(self, scientific_production:list = [], positive:bool=False, 
    accreditation:Accreditation=None, observation:str='', assessment:str='', 
    arts_relevant:list=[], arts_m_relevant:list=[], criterion:CriterionEvaluationRelevance = None):
        
        super().__init__(scientific_production=scientific_production, positive = positive, 
        accreditation = accreditation, observation=observation)
        self.assessment = assessment
        self.arts_relevant = arts_relevant
        self.arts_m_relevant = arts_m_relevant
        self.criterio = criterion

    def get_articles_relevant(self):
        """
        Método para obtener los articulos relevantes.
        :return list lista de artículos relevantes
        """
        if self.arts_relevant:
            if len(self.arts_relevant) >= self.criterio.num_relevant:
                return self.arts_relevant[0:self.criterio.num_relevant]
            return self.arts_relevant[0:]
        return None    

    def get_articles_m_relevant(self):
        """
        Método para obtener los articulos muy relevantes.
        :return list lista de artículos muy relevantes
        """
        if self.arts_m_relevant:
            if len(self.arts_m_relevant) >= self.criterio.num_m_relevant:
                return self.arts_m_relevant[0:self.criterio.num_m_relevant]
            return self.arts_m_relevant[0:]
        return None
    
    def get_substitute_production(self):
        """
        Método para obtener la producción sustitutoria.
        :return list lista de producción sustitutoria
        """
        result = self.scientific_production
        if result:
            articles = self.get_articles_relevant()
            m_relevant = self.get_articles_m_relevant()
            if m_relevant:
                articles += m_relevant
            
            if articles:
                for art in articles:
                    result.remove(art)
        return result
            