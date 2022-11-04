from model.process.Process2.Entities.Committee.Committee import Committee
from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation


class CommitteeArquitecturaIngenieriaCivilYUrbanismo(Committee):
    """
    Comité que evalúa las solicitudes de sexenios del área Arquitectura, Ingeniería Civil y Urbanismo. (6.3)
    """
    def __init__(self, id, evaluator, is_commission: bool = False, 
        is_tecnology:bool = False):
        super().__init__(id, evaluator, is_commission)
        self.is_tecnology = is_tecnology

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        eval = SexenioEvaluation(scientific_production=scientific_production, 
            observation='En esta evaluación no ha sido posible obtener la puntuación ya que el comité no la especifica en sus requisitos.')

        if self.is_tecnology:
            eval.parameters = self.get_criterion('perfil_tecnologico')
        else:
            eval.parameters = self.get_criterion('perfil_no_tecnologico')

        if scientific_production:
            min_articles = eval.parameters['min_aportaciones']
            if len(scientific_production) >= min_articles:
                eval.main_production  = scientific_production[0:min_articles]

        return eval