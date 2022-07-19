from model.process.Proceso2.Entities.RO import RO
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio
from model.process.Proceso2.Entities.Comites.Comite import Comite


class ComiteFilosofiaFilologiaYLinguistica(Comite):
    """
    Comité que evalúa las solicitudes de sexenios del área Filosofía, Filología y Lingüistica. (11)
    """
    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    def get_puntuacion_articulo(self, element:RO, puntuaciones:dict) -> int:
        """
        Método que obtiene la puntuación de un artículo.
        :param RO elemento a analizar para obtener su puntuación
        :param puntuaciones diccionario con las puntuaciones
        :return puntuación obtenida
        """
        puntuacion = 0
        if element.cuartil:
            if element.get_cuartil() == 4:
                puntuacion = puntuaciones['puntuacion_q4_publicaciones']
            else:
                puntuacion = puntuaciones['puntuacion_q1q2q3_publicaciones']
        return puntuacion

    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        eval = EvaluacionSexenio(produccion_cientifica=produccion_cientifica,
        parametros=self.get_criterio())
        
        if len(produccion_cientifica) >= eval.parametros['min_publicaciones']:
            eval.produccion_principal = produccion_cientifica[0:eval.parametros['min_publicaciones']]
        else: 
            eval.produccion_principal = produccion_cientifica[0:]

        eval.observaciones = 'En los requisitos que se han evaluado no se indican el número de artículos mínimo, por esto, se ha indicado como producción científica ' + \
            'principal los primeros artículos obtenidos. \n'

        if eval.produccion_principal:
            puntuaciones = eval.parametros['puntuaciones']
            for elem in eval.produccion_principal:
                eval.puntuacion += self.get_puntuacion_articulo(elem, puntuaciones)
        return eval