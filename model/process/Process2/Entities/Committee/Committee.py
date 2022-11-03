from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.Evaluator import Evaluator
from abc import abstractmethod

"""
Evaluador encargado de baremar la presentación de sexenios
"""
class Committee(Evaluator):
    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    @abstractmethod
    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        pass