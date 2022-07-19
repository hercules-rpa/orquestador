from abc import abstractmethod
from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.Evaluacion import Evaluacion

"""
Evaluación resultante de analizar una solicitud de acreditación.
"""
class EvaluacionAcreditacion(Evaluacion):
    def __init__(self, produccion_cientifica:list = [], positiva:bool=False, acreditacion:Acreditacion=None, 
        observacion:str='', valoracion_alcanzada:str=''):
        super().__init__(produccion_cientifica=produccion_cientifica, observacion=observacion)
        self.positiva = positiva
        self.acreditacion = acreditacion
        self.valoracion_alcanzada = valoracion_alcanzada

    @abstractmethod
    def get_produccion_sustitutoria(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        """
        pass