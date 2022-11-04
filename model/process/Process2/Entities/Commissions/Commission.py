from model.process.Process2.Entities.Evaluations.Evaluation import Evaluation
from model.process.Process2.Entities.Evaluator import Evaluator
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationBiologCelularMolecular import AccreditationEvaluationBiologCelularMolecular,CriterionEvaluationBiologiaCelularMolecular
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType

from abc import abstractmethod

"""
Una comisión es el organismo encargado de evaluar las solicitudes de acreditaciones
de los investigadores
"""
class Commission(Evaluator):
    def __init__(self, id, evaluator, is_commission: bool = True):
        super().__init__(id, evaluator, is_commission)

    @abstractmethod
    def get_accreditation_evaluation(self, scientific_production, tipo:Accreditation) -> Evaluation:
        pass

    def get_configuration_criterion(self, accreditation_type:AccreditationType, assessment:str=None):
        """
        Método que obtiene los parámetros a utilizar en la evaluación de un tipo de
        acreditación, utilizando si es necesario el tipo de valoración que se va a comprobar.
        :param accreditation_type Enumerado que define el tipo de acreditación
        :param assessment letra de la valoración que se evaluará (A,B,C...)

        :return si lo encuentra devuelve los parámetros que se deben utilizar, en caso contrario
        no devolverá nada.
        """
        criterion = self.get_criterion()
        if criterion:
            type_node = ''
            if accreditation_type == AccreditationType.CATEDRA:
                type_node = 'catedra'
            elif accreditation_type == AccreditationType.TITULARIDAD:
                type_node = 'titularidad'

            if type_node:
                result = criterion[type_node]
                if result and assessment and assessment in result:
                    result = result[assessment]                        
                return result
        return None
                
    






    