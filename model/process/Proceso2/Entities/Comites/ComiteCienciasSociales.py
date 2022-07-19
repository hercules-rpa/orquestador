from model.process.Proceso2.Entities.Comites.Comite import Comite
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio
from model.process.Proceso2.Entities.RO import RO

class ComiteCienciasSociales(Comite):
    """
    Comité que evalúa el área de Ciencias Sociales, Políticas y Comunicación dentro del comité 7.1.
    """
    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        evaluacion = EvaluacionSexenio(produccion_cientifica=produccion_cientifica, parametros=self.get_criterio('cienciassociales'))

        if len(produccion_cientifica) >= 5:
            evaluacion.produccion_principal = produccion_cientifica[0:5]

            for art in evaluacion.produccion_principal:
                evaluacion.puntuacion += self.get_puntuacion_articulo(art, evaluacion.parametros)  
        return evaluacion
        
    def get_penalizacion_puntuacion(self, element:RO, puntuacion:int, penalizaciones:dict): 
        """
        Método que calcula la penalización sobre la puntuación basandose en el nº de autores
        y en el nº de firmante del investigador.
            -hasta 3: no se resta
            -de 4 a 6, 1,2, y 3: no se resta
            -de 4 a 6, posiciones 4,5, y 6: se resta un 25%
            -de 7 en adelante: se resta un 50 %
        :param RO elemento a analizar
        :param int puntuación para calcular la penalización
        :return int penalización obtenida.
        """
        penalizacion = 0
        if element.nautores > 4 and element.nautores <= 6: 
            if element.posicion_autor >= 4:
                penalizacion = puntuacion * penalizaciones['n_autores_4_6']
        elif element.nautores >= 7:
            if element.posicion_autor >= 4:
                penalizacion = puntuacion * penalizaciones['n_autores_4_6']
            elif element.posicion_autor >= 7:
                penalizacion = puntuacion * penalizaciones['n_autores_max_7']
        return penalizacion

    def get_puntuacion_articulo(self, element:RO, parametros):
        """
        Método que obtiene la puntuación de un artículo.
        """
        if element and parametros and 'puntuaciones' in parametros:
            puntuaciones = parametros['puntuaciones']
            cuartil = element.get_cuartil()
            puntuacion = 0
            if cuartil == 1:
                puntuacion = puntuaciones['puntuacion_q1']
            elif cuartil == 2:
                puntuacion = puntuaciones['puntuacion_q2']
            elif cuartil == 3:
                puntuacion = puntuaciones['puntuacion_q3']
            elif cuartil == 4:
                puntuacion = puntuaciones['puntuacion_q4']        

        puntuacion -= self.get_penalizacion_puntuacion(element, puntuacion, parametros['penalizaciones'])        
        return puntuacion