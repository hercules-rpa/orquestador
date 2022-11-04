from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.Committee.Committee import Committee


class CommitteeCienciasEducacion(Committee):
    """
    Comité encargado de la evaluación de solicitud de sexenios para la comisión de Ciencias de la Educacion. (7.2)
    """
    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] scientific_production: listado de artículos de un investigador.
        :return SexenioEvaluation evaluación del sexenio.        
        """
        eval = SexenioEvaluation(scientific_production=scientific_production, 
        parameters=self.get_criterion())
        min_publications = eval.parameters['min_publicaciones']
        if len(scientific_production) >= min_publications:
            eval.main_production = eval.scientific_production[0:min_publications]
            punctuations = eval.parameters['puntuaciones']
            eval.punctuation = 2*punctuations['puntuacion_jcr_publicaciones']
        return eval
                