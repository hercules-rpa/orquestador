from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio
from model.process.Proceso2.Entities.Comites.Comite import Comite


class ComiteQuimica(Comite):
    """
    Comité encargado de la evaluación de solicitud de sexenios para la comisión de Química(2).
    En este comité se han tenido en cuenta los artículos del Q1, no se tienen en cuenta los artículos en Q2 
    en límite con Q1. 
    """

    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        """
        Método que realiza la evaluación del sexenio, hidratará la colección "producción 
        principal" si el investigador tiene 5 artículos en Q1.
        :param list producción científica del investigador.
        :return EvaluacionSexenio evaluación realizada según los criterios del comité.
        """
        eval = EvaluacionSexenio(produccion_cientifica=produccion_cientifica,
        parametros=self.get_criterio())
        clasificacion = eval.get_clasificacion_produccion()

        if clasificacion and len(clasificacion.publicaciones_q1) >= eval.parametros['min_publicaciones']:
            eval.produccion_principal = clasificacion.publicaciones_q1[0:eval.parametros['min_publicaciones']]
            puntuaciones = eval.parametros['puntuaciones']
            eval.puntuacion = 5*puntuaciones['puntuacion_q1']
            
            eval.observaciones = '\n\nEn este comité se han tenido en cuenta los artículos pertenecientes al primer cuartil (Q1), ' +\
                ' no se tienen en cuenta los artículos pertenecientes al cuartil dos (Q2) en límite con Q1. \n'

        return eval