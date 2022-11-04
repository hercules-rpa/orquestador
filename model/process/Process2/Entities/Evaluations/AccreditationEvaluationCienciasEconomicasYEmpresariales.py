from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation

class CriterionEvaluationCienciasEconomicasYEmpresariales():
    """
    Criterio de evaluación de la acreditación de la comisión de Ciencias del Comportamiento:

    num_Q1_Q2: número de artículos que están en el primer y segundo cuartil.   
    num_Q3_Q4: número de artículos que están en el tercer y cuarto cuartil.
    num_D1: número de artículos que están en el primer decil.
    """
    def __init__(self, num_Q1_Q2 : int,  num_Q3_Q4: int,  num_D1: int):
        self.num_Q1_Q2 = num_Q1_Q2
        self.num_Q3_Q4 = num_Q3_Q4
        self.num_D1 = num_D1

class AccreditationEvaluationCienciasEconomicasYEmpresariales(AccreditationEvaluation):
    """
    Resultado de la evaluación de la comisión de Ciencias Económicas y Empresariales
    """
    def __init__(self, scientific_production: list = [], positive: bool = False, 
        accreditation: Accreditation = None, observation: str = '', 
        assessment: str = '', art_Q1_Q2: list = [], 
        art_Q3_Q4 :list = [],art_D1: list = [],
        criterion: CriterionEvaluationCienciasEconomicasYEmpresariales = None ):
        super().__init__(scientific_production=scientific_production, positive=positive, 
                        accreditation=accreditation, observation=observation, assessment=assessment)
        self.art_Q1_Q2 = art_Q1_Q2
        self.art_Q3_Q4 = art_Q3_Q4
        self.art_D1 = art_D1
        self.criterion = criterion

    def get_publications_D1(self) -> list:
        """
        Método que obtiene las publicaciones en el primer decil que deben estar
        en la producción del informe.
        :return list lista de elementos que se encuentran en el primer decil
        """
        num = self.criterion.num_D1
        if self.art_D1:
            if len(self.art_D1) >= num:
                return self.art_D1[0:num]
            return self.art_D1[0:]
        return None        

    def get_publications_Q1_Q2(self) -> list:
        """
        Métodop que obtiene las publicaciones en el primer y segundo cuartil que deben estar
        en la producción del informe.
        :return list lista de elementos que se encuentran en el cuartil uno y dos.
        """
        num = self.criterion.num_Q1_Q2
        if self.art_Q1_Q2:
            if len(self.art_Q1_Q2) >= num:
                return self.art_Q1_Q2[0:num]
            return self.articulos_Q1_Q2s_Q1[0:]
        return None

    def get_publications_Q3_Q4(self) -> list:
        """
        Método que obtiene las publicaciones en el tercer y cuarto cuartil que deben estar
        en la producción del informe
        :return list lista de elementos que se encuentran en el tercer y cuarto cuartil.
        """
        num = self.criterion.num_Q3_Q4
        if self.art_Q3_Q4:
            if len(self.art_Q3_Q4) >= num:
                return self.art_Q3_Q4[0:num]
            return self.art_Q3_Q4[0:]
        return None
        
    def get_substitute_production(self):
        """
        Método que obtiene las publicaciones en el tercer y cuarto cuartil que deben estar
        en la producción del informe
        :return list lista de producción sustitutoria
        """
        result = []
        if self.scientific_production:
            arts_q1q2 = self.get_publications_Q1_Q2()
            arts_q3q4 = self.get_publications_Q3_Q4()
            arts_d1 = self.get_publications_D1()
            for article in self.scientific_production:
                if article not in arts_q1q2 or article not in arts_q3q4 or article not in arts_d1:
                    result.append(article)
        return result
