from abc import ABC, abstractmethod

"""
Evaluación resultante de analizar una solicitud de acreditación o de sexenio.
"""
class Evaluacion(ABC):
    def __init__(self, produccion_cientifica: list = [], observacion: str = ''):
        self.produccion_cientifica = produccion_cientifica
        self.observaciones = observacion

    @abstractmethod
    def get_produccion_sustitutoria(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        """
        pass