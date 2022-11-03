from abc import ABC, abstractmethod

"""
Evaluación resultante de analizar una solicitud de acreditación o de sexenio.
"""
class Evaluation(ABC):
    def __init__(self, scientific_production: list = [], observation: str = ''):
        self.scientific_production = scientific_production
        self.observation = observation

    @abstractmethod
    def get_substitute_production(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        :return list lista de producción sustitutoria
        """
        pass