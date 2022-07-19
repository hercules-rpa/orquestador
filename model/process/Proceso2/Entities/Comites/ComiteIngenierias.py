from model.process.Proceso2.Entities.RO import RO
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio, InfoClasificacion
from model.process.Proceso2.Entities.Comites.Comite import Comite


class ComiteIngenierias(Comite):
    """
    Comité que evalúa las solicitudes de sexenios de las áreas de Ingenierías de la comunicación, computación y electrónica. (6.2)
    """

    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        eval = EvaluacionSexenio(produccion_cientifica=produccion_cientifica, 
        parametros=self.get_criterio())
        clasificacion = eval.get_clasificacion_produccion()

        tupla = self.criterio1(clasificacion, eval.parametros)
        if tupla and tupla[0] > 0:
            eval.puntuacion = tupla[0]
            eval.produccion_principal = tupla[1]
        else:
            tupla = self.criterio2(clasificacion, eval.parametros)
            if tupla and tupla[0] > 0:
                eval.puntuacion = tupla[0]
                eval.produccion_principal = tupla[1]
        return eval

    def get_puntuacion_total_articulos(self, elements, puntuaciones: dict) -> int:
        """
        Método que calcula la puntuación total de una colección de artículos.
        :param [] lista de artículos
        :param dict puntuaciones
        :result int puntuación obtenida
        """
        puntuacion = 0
        if elements:
            for elem in elements:
                puntuacion += self.get_puntuacion_articulo(elem, puntuaciones)
        return puntuacion

    def get_puntuacion_articulo(self, element: RO, puntuaciones: dict) -> int:
        """
        Método que calcula la puntuación que tiene un artículo en base al cuartil al que pertenece y al número de autores que tiene.
        :param RO artículo que se evaluará
        :param dict puntuaciones
        :result int puntuación obtenida
        """
        puntuacion = 0
        if element.get_cuartil() == 1:
            puntuacion = puntuaciones['puntuacion_q1']
        if element.get_cuartil() == 2:
            puntuacion = puntuaciones['puntuacion_q2']
        elif element.get_cuartil() == 3:
            puntuacion = puntuaciones['puntuacion_q3']
        elif element.get_cuartil() == 4:
            puntuacion = puntuaciones['puntuacion_q4']

        puntuacion -= self.get_descontar_puntuacion(element)
        return puntuacion

    def get_descontar_puntuacion(self, element: RO) -> int:
        """
        Método que calcula lo que hay que descontar de la puntuación siguiendo los siguientes criterios basados en la cantidad de firmantes:
        - Si firman hasta 6 personas no se descontará nada
        - De 7 al 10: salvo casos justificados, por cada firma más, se descontará 0,5 puntos.
        - De 11 en adelante: salvo casos justificados, por cada firma más, se descontará 0,25 puntos.

        :param RO elemento que se analizará
        :return int puntuación que se debe descontar
        """
        result = 0
        if element.nautores >= 7 and element.nautores <= 10:
            result = (element.nautores-6)*0.5
        elif element.nautores >= 11:
            result = (element.nautores-11)*0.25
        return result

    def criterio1(self, clasificacion: InfoClasificacion, parametros: dict) -> tuple([int, list]):
        """
        Método que evalúa el siguiente criterio:
        - Dos aportaciones de alta relevancia y una de relevancia media.
        :param InfoClasificacion clasificación de la producción científica del investigador.
        :param dict diccionario de parámetros
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal
        """
        results = []
        puntuacion = 0
        criterio = parametros['criterio1']
        if clasificacion and len(clasificacion.publicaciones_q1) >= criterio['num_relevancia_alta'] and \
            len(clasificacion.publicaciones_q2) >= criterio['num_relevancia_media']:
            
            results = clasificacion.publicaciones_q1[0:criterio['num_relevancia_alta']]
            results += clasificacion.publicaciones_q2[0:criterio['num_relevancia_media']]
            puntuacion = self.get_puntuacion_total_articulos(results, parametros['puntuaciones'])

        return (puntuacion, results)

    def criterio2(self, clasificacion: InfoClasificacion, parametros:dict) -> tuple([int, list]):
        """
        Método que evalúa el siguiente criterio:
        - Una aportación de alta relevancia y tres de relevancia media
        :param InfoClasificacion clasificación de la producción científica del investigador.
        :param dict diccionario de parámetros
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal
        """
        results = []
        puntuacion = 0
        criterio = parametros['criterio2']
        if clasificacion and len(clasificacion.publicaciones_q1) >= criterio['num_relevancia_alta'] and \
            len(clasificacion.publicaciones_q2) >= criterio['num_relevancia_media']:
            
            results = clasificacion.publicaciones_q1[0:criterio['num_relevancia_alta']]
            results += clasificacion.publicaciones_q2[0:criterio['num_relevancia_media']]
            puntuacion = self.get_puntuacion_total_articulos(results, parametros['puntuaciones'])
        
        return (puntuacion, results)
