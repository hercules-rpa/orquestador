from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionRelevancia import CriterioRelevancia
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionRelevancia import EvaluacionAcreditacionRelevancia
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion
from model.process.Proceso2.Entities.Comisiones.ComisionInformatica import ComisionInformatica

"""
Comisión encargada de la evaluación de las solicitudes de acreditación del área de 
Ingeniería Eléctrica. (11)
"""
class ComisionIngElectrica(ComisionInformatica):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_evaluacion_acreditacion(self, produccion_cientifica, acreditacion:Acreditacion) -> EvaluacionAcreditacionRelevancia:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return objeto EvaluacionAcreditacionRelevancia con los resultados del criterio de la comisión de las comisiones que tienen como criterio las relevancias de las publicaciones.
        """
        eval:EvaluacionAcreditacionRelevancia = EvaluacionAcreditacionRelevancia(articulos=produccion_cientifica, acreditacion=acreditacion)
        self.set_criterio_evaluacion(eval)
        if acreditacion.tipo == TipoAcreditacion.CATEDRA:
            return self.get_evaluacion_catedra(eval)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            return self.get_evaluacion_titularidad(eval)

    def get_evaluacion_titularidad(self, eval:EvaluacionAcreditacionRelevancia) -> EvaluacionAcreditacionRelevancia:
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param EvaluacionAcreditacionRelevancia eval: evaluacion sobre la que se hidratará el criterio.
        :return objeto EvaluacionAcreditacionRelevancia con los resultados del criterio de la comisión de las comisiones que tienen como criterio las relevancias de las publicaciones.
        """
        return self.get_evaluacion(eval=eval)

    def get_evaluacion_catedra(self, eval:EvaluacionAcreditacionRelevancia) -> EvaluacionAcreditacionRelevancia:
        """
        Metodo para la evaluación de la catedra de un investigador

        :param EvaluacionAcreditacionRelevancia eval: evaluacion sobre la que se hidratará el criterio.
        :return objeto EvaluacionAcreditacionRelevancia con los resultados del criterio de la comisión de las comisiones que tienen como criterio las relevancias de las publicaciones.
        """
        return self.get_evaluacion(eval=eval)
