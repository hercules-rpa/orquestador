
from model.process.Proceso2.Entities.RO import RO
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio
from model.process.Proceso2.Entities.Comites.Comite import Comite


class ComiteCienciasBiomedicas(Comite):
    """
    Comité que se encarga de la evaluación de la solicitud de sexenios del área de 
    Ciencias Biomédicas - id (5)'.
    """
    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    def criterio1(self, alta_relevancia, media_relevancia, parametros:dict) -> tuple([int, list]):
        """
        Método que comprueba la primera combinación para la solicitud de un sexenio.
        2Q1 + 3Q2

        :param [] alta_relevancia: artículos que pertenecen al Q1.
        :param [] media_relevancia: artículos que pertenecen al Q2.
        :param dict diccionario de parámetros del criterio.
        :return tupla [int, list] que devuelve la puntuación total y la lista de artículos seleccionados.
       
        """
        puntuacion = 0
        articulos = []
        criterio=parametros['criterio1']
        if len(alta_relevancia) >= criterio['num_relevancia_alta']:
            articulos = alta_relevancia[0:criterio['num_relevancia_alta']]
            if len(media_relevancia) >= criterio['num_relevancia_media']:
                articulos += media_relevancia[0:criterio['num_relevancia_media']]                
                puntuacion = self.get_puntuacion_total(articulos, parametros['puntuaciones'])       
        return (puntuacion,articulos)
    
    def criterio2(self, alta_relevancia, media_relevancia, baja_relevancia, parametros:dict) -> tuple([int, list]):
        """
        Método que comprueba 3Q1 + 1Q2 + 1Q3
        :param [] alta_relevancia: artículos que pertenecen al Q1.
        :param [] media_relevancia: artículos que pertenecen al Q2.
        :param [] baja_relevancia: artículos que pertenecen al Q3-Q4.
        :param dict diccionario de parámetros del criterio.
        :return tupla [int, list] que devuelve la puntuación total y la lista de artículos seleccionados.    
        """
        puntuacion = 0
        articulos = []
        criterio = parametros['criterio2']
        if len(alta_relevancia) >= criterio['num_relevancia_alta']:
            articulos = alta_relevancia[0:criterio['num_relevancia_alta']]
            if len(media_relevancia) >= criterio['num_relevancia_media']:
                articulos += media_relevancia[0:criterio['num_relevancia_media']]  
                if len(baja_relevancia) >= criterio['num_relevancia_baja']:
                    articulos += baja_relevancia[0:criterio['num_relevancia_baja']]  

                    puntuacion = self.get_puntuacion_total(articulos, parametros['puntuaciones'])   
        return (puntuacion,articulos)

    def criterio3(self, alta_relevancia, baja_relevancia, parametros) -> tuple([int, list]):
        """
        Método que comprueba la primera combinación para la solicitud de un sexenio.
        4Q1 + 1Q3
        :param [] alta_relevancia: artículos que pertenecen al Q1.
        :param [] baja_relevancia: artículos que pertenecen al Q3-Q4.
        :param dict diccionario de parámetros del criterio
        :return tupla [int, list] que devuelve la puntuación total y la lista de artículos seleccionados.
        """
        puntuacion = 0
        articulos:list = []
        criterio = parametros['criterio3']
        if len(alta_relevancia) >= criterio['num_relevancia_alta']:
            articulos = alta_relevancia[0:criterio['num_relevancia_alta']]
            if len(baja_relevancia) >= criterio['num_relevancia_baja']:
                articulos += baja_relevancia[0:criterio['num_relevancia_baja']]
                puntuacion = self.get_puntuacion_total(articulos, parametros['puntuaciones'])
                     
        return (puntuacion,articulos)

    def get_puntuacion_total(self, elements:list, puntuaciones:dict) -> int:
        """
        Método que obtiene la puntuación total de una lista de elementos.
        :param list lista de elementos
        :param dict puntuaciones
        """
        puntuacion =0
        if elements:
            for element in elements:
                puntuacion += self.get_puntuacion(element, puntuaciones)
        return puntuacion

    def get_puntuacion(self, element:RO, puntuaciones:dict) -> int:
        """
        Método que obtiene la puntuación del elemento
        :param RO elemento a analizar
        :param dict puntuaciones
        :result int puntuación obtenida
        """
        puntuacion = 0
        cuartil = element.get_cuartil()
        if cuartil == 1:
            puntuacion = puntuaciones['puntuacion_q1']
        elif cuartil == 2:
            puntuacion = puntuaciones['puntuacion_q2']
        elif cuartil == 3:
            puntuacion = puntuaciones['puntuacion_q3']
        elif cuartil == 4:
            puntuacion = puntuaciones['puntuacion_q4']
        return puntuacion
    
    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        evaluacion = EvaluacionSexenio(produccion_cientifica=produccion_cientifica, 
        parametros=self.get_criterio())
        
        if produccion_cientifica:
            alta_relevancia = []
            media_relevancia = []
            baja_relevancia = []

            for articulo in produccion_cientifica:
                if articulo.get_cuartil() == 1:
                    alta_relevancia.append(articulo)
                elif articulo.get_cuartil() == 2:
                    media_relevancia.append(articulo)
                else:
                    baja_relevancia.append(articulo)
                       
            result = self.criterio1(alta_relevancia, media_relevancia, evaluacion.parametros)
            if result and result[0] > 0:
                evaluacion.puntuacion = result[0]
                evaluacion.produccion_principal = result[1]
            else:
                result = self.criterio2(alta_relevancia, media_relevancia, baja_relevancia, evaluacion.parametros)
                if result[0] > 0:
                    evaluacion.puntuacion = result[0]
                    evaluacion.produccion_principal = result[1]
                else:
                    result = self.criterio3(alta_relevancia, baja_relevancia, evaluacion.parametros)
                    if result[0] > 0:
                        evaluacion.puntuacion = result[0]
                        evaluacion.produccion_principal = result[1]
                        
        return evaluacion
