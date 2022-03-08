from abc import ABC, abstractmethod


class Adaptador_Convocatoria(ABC):

    @abstractmethod
    def buscar(self, *args):
        pass

    @abstractmethod
    def buscar_fecha(self, fecha_desde, fecha_hasta, *args):
        pass

    @abstractmethod
    def notify(self):
        pass