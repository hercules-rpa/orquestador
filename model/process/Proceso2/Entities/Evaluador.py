from abc import ABC

class Evaluador(ABC):
    def __init__(self, id, configuracion, es_comision:bool=False) -> None:
        self.id = id
        self.configuracion = configuracion
        if configuracion:
            self.nombre = configuracion['name']
            self.comision:bool = es_comision
            self.autoria_orden:bool = configuracion['autoria_orden']
            self.autoria_str = configuracion['autoria_str']
            self.alerta_autores = configuracion['alerta_autores']
            self.libros_caps:bool = configuracion['libros']
            self.congresos:bool = configuracion['congresos']
            self.patentes:bool = configuracion['patentes']
            
            print('****** evaluador: ' + self.nombre)

    def get_criterio(self, hijo:str=''):
        """
        Método que obtiene el criterio del archivo de configuración del organismo 
        evaluador. El criterio define los parámetros que son configurables por el usuario
        y que utiliza el evaluador (comité o comisión) para analizar la solicitud.
        """
        if self.configuracion and 'criterio' in self.configuracion:
            criterio = self.configuracion['criterio']
            if hijo and hijo in criterio:
                criterio = criterio[hijo]
            return criterio
        return None