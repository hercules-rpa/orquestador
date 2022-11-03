from model.process.Process2.Entities.Evaluations.AccreditationEvaluationRelevance import CriterionEvaluationRelevance
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationRelevance import AccreditationEvaluationRelevance
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType
from model.process.Process2.Entities.Commissions.CommissionInformatica import CommissionInformatica

"""
Comisión encargada de la evaluación de las solicitudes de acreditación del área de 
Ingeniería Eléctrica. (11)
"""
class CommissionIngElectrica(CommissionInformatica):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_accreditation_evaluation(self, scientific_production, 
    accreditation:Accreditation) -> AccreditationEvaluationRelevance:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] scientific_production: listado de artículos de un investigador.
        :param Accreditation accreditation: tipo de acreditación que se está solicitando.
        :return objeto AccreditationEvaluationRelevance con los resultados del criterio de la comisión de las Commissions que tienen como criterio las relevancias de las publicaciones.
        """
        eval:AccreditationEvaluationRelevance = AccreditationEvaluationRelevance(scientific_production=scientific_production, accreditation=accreditation)
        self.set_criterion(eval)
        if accreditation.type == AccreditationType.CATEDRA:
            return self.get_catedra(eval)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            return self.get_titularidad(eval)

    def get_titularidad(self, eval:AccreditationEvaluationRelevance) -> AccreditationEvaluationRelevance:
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param AccreditationEvaluationRelevance eval: evaluacion sobre la que se hidratará el criterio.
        :return objeto AccreditationEvaluationRelevance con los resultados del criterio de la comisión de las Commissions que tienen como criterio las relevancias de las publicaciones.
        """
        return self.get_evaluacion(eval=eval)

    def get_catedra(self, eval:AccreditationEvaluationRelevance) -> AccreditationEvaluationRelevance:
        """
        Metodo para la evaluación de la catedra de un investigador

        :param AccreditationEvaluationRelevance eval: evaluacion sobre la que se hidratará el criterio.
        :return objeto AccreditationEvaluationRelevance con los resultados del criterio de la comisión de las Commissions que tienen como criterio las relevancias de las publicaciones.
        """
        return self.get_evaluacion(eval=eval)
