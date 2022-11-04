from abc import ABC

class Evaluator(ABC):
    """
    Un evaluador es el encargado de realizar la evaluación de una solicitud de sexenio o acreditación,
    basándose en los criterios de la ANECA
    """
    def __init__(self, id, configuration, is_commission:bool=False) -> None:
        self.id = id
        self.configuration = configuration
        self.is_commission:bool = is_commission
        if configuration:
            self.name = configuration['name']
            self.authorship_order:bool = configuration['autoria_orden']
            self.authorship_str = configuration['autoria_str']
            self.authors_alert = configuration['alerta_autores']
            self.books_caps:bool = configuration['libros']
            self.conferences:bool = configuration['congresos']
            if 'patentes' in configuration:
                self.patents:bool = configuration['patentes']
            else:
                self.patents:bool = False
            
        if self.name:
            print('****** evaluador: ' + self.name)

    def get_criterion(self, children:str=''):
        """
        Método que obtiene el criterio del archivo de configuración del organismo 
        evaluador. El criterio define los parámetros que son configurables por el usuario
        y que utiliza el evaluador (comité o comisión) para analizar la solicitud.
        :param hijo nombre que se utiliza para buscar un subapartado dentro del criterio.
        :return devuelve el criterio obtenido
        """
        if self.configuration and 'criterio' in self.configuration:
            criterio = self.configuration['criterio']
            if children and children in criterio:
                criterio = criterio[children]
            return criterio
        return None