from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio
from model.process.Proceso2.Entities.Evaluador import Evaluador
from abc import abstractmethod

"""
Evaluador encargado de baremar la presentación de sexenios
"""
class Comite(Evaluador):
    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    @abstractmethod
    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        pass