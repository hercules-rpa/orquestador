from model.process.Proceso2.Entities.Comites.Comite import Comite
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio


class ComiteArquitecturaIngenieriaCivilYUrbanismo(Comite):
    """
    Comité que evalúa las solicitudes de sexenios del área Arquitectura, Ingeniería Civil y Urbanismo. (6.3)
    """
    def __init__(self, id, evaluador, es_comision: bool = False, 
        perfil_tecnologico:bool = False):
        super().__init__(id, evaluador, es_comision)
        self.perfil_tecnologico = perfil_tecnologico

    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        eval = EvaluacionSexenio(produccion_cientifica=produccion_cientifica, 
            observacion='En esta evaluación no ha sido posible obtener la puntuación ya que el comité no la especifica en sus requisitos.')

        if self.perfil_tecnologico:
            eval.parametros = self.get_criterio('perfil_tecnologico')
        else:
            eval.parametros = self.get_criterio('perfil_no_tecnologico')

        if produccion_cientifica:
            min_aportaciones = eval.parametros['min_aportaciones']
            if len(produccion_cientifica) >= min_aportaciones:
                eval.produccion_principal  = produccion_cientifica[0:min_aportaciones]

        return eval