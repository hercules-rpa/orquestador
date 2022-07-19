from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio
from model.process.Proceso2.Entities.Comites.Comite import Comite


class ComiteCienciasEducacion(Comite):
    """
    Comité encargado de la evaluación de solicitud de sexenios para la comisión de Ciencias de la Educacion. (7.2)
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
        min_publicaciones = eval.parametros['min_publicaciones']
        if len(produccion_cientifica) >= min_publicaciones:
            eval.produccion_principal = eval.produccion_cientifica[0:min_publicaciones]
            puntuaciones = eval.parametros['puntuaciones']
            eval.puntuacion = 2*puntuaciones['puntuacion_jcr_publicaciones']
        return eval
                