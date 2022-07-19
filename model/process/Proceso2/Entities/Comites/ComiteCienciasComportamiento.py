from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio
from model.process.Proceso2.Entities.Comites.ComiteEstudiosGenero import ComiteEstudiosGenero
from model.process.Proceso2.Entities.RO import RO

class ComiteCienciasComportamiento(ComiteEstudiosGenero):
    """
    Comité que evalúa el área de Ciencias del Comportamiento dentro del comité 7.1.
    """
    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        return super().get_evaluacion_sexenio(produccion_cientifica)

    def get_penalizacion_puntuacion(self, element: RO, puntuacion: int, penalizaciones:dict):
        """
        Método que calcula la penalización sobre la puntuación basandose en el nº de autores
        y en el nº de firmante del investigador.
            -1-6 indiferente: no se resta
            -7 o más autores, en 1ª, 2ª o última posición: no se resta
            -7 o más autores, entre la 3ª y la última: se resta un 25%
        :param RO elemento a analizar
        :param int puntuación para calcular la penalización
        :return int penalización obtenida.
        """
        penalizacion = 0
        if element.nautores >= 7:
            if element.posicion_autor >= 3:
                penalizacion = puntuacion * penalizaciones['n_autores_max_7']
        return penalizacion
