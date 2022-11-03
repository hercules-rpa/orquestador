from abc import ABC, abstractmethod


class Adapter_Call(ABC):
    """
    Clase abstracta de la que tienen que implementar las librerías.
    """
    @abstractmethod
    def search(self, *args):
        """
        Método para buscar una convocatoria.
        """
        pass

    @abstractmethod
    def search_date(self, start_date, end_date, *args):
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