from abc import ABC, abstractmethod


class Adaptador_Convocatoria(ABC):
    """
    Clase abstracta de la que tienen que implementar las librerías.
    """
    @abstractmethod
    def buscar(self, *args):
        """
        Método para buscar una convocatoria.
        """
        pass

    @abstractmethod
    def buscar_fecha(self, fecha_desde, fecha_hasta, *args):
        """
        Método para buscar una convocatoria por fecha.
        """
        pass

    @abstractmethod
    def notify(self):
        """
        Método para notificar sobre el proceso de una convocatoria.
        """
        pass