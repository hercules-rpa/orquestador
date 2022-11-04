from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.Committee.Committee import Committee


class CommitteeQuimica(Committee):
    """
    Comité encargado de la evaluación de solicitud de sexenios para la comisión de Química(2).
    En este comité se han tenido en cuenta los artículos del Q1, no se tienen en cuenta los artículos en Q2 
    en límite con Q1. 
    """

    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método que realiza la evaluación del sexenio, hidratará la colección "producción 
        principal" si el investigador tiene 5 artículos en Q1.
        :param list producción científica del investigador.
        :return SexenioEvaluation evaluación realizada según los criterios del comité.
        """
        eval = SexenioEvaluation(scientific_production=scientific_production,
        parameters=self.get_criterion())
        clasificacion = eval.get_classification_production()

        if clasificacion and len(clasificacion.publications_q1) >= eval.parameters['min_publicaciones']:
            eval.main_production = clasificacion.publications_q1[0:eval.parameters['min_publicaciones']]
            punctuation = eval.parameters['puntuaciones']
            eval.punctuation = 5*punctuation['puntuacion_q1']
            
            eval.observation = '\n\nEn este comité se han tenido en cuenta los artículos pertenecientes al primer cuartil (Q1), ' +\
                ' no se tienen en cuenta los artículos pertenecientes al cuartil dos (Q2) en límite con Q1. \n'

        return eval