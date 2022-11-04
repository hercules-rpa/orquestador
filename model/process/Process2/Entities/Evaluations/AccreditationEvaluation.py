from abc import abstractmethod
from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.Evaluation import Evaluation

"""
Evaluación resultante de analizar una solicitud de acreditación.
"""
class AccreditationEvaluation(Evaluation):
    def __init__(self, scientific_production:list = [], positive:bool=False, accreditation:Accreditation=None, 
        observation:str='', assessment:str=''):
        super().__init__(scientific_production=scientific_production, observation=observation)
        self.positive = positive
        self.accreditation = accreditation
        self.assessment = assessment

    @abstractmethod
    def get_substitute_production(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        :return list lista de producción sustitutoria
        """
        pass
