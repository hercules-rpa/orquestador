from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.Committee.CommitteeCienciasComportamiento import CommitteeCienciasComportamiento

class CommitteeBiblioteconomiaYDocumentacion(CommitteeCienciasComportamiento):
    """
    Comité que evalúa el área de Biblioteconomía y Documentación dentro del comité 7.1.
    """
    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        return super().get_evaluation_sexenio(scientific_production)