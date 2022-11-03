from model.process.Process2.Entities.Evaluations.AccreditationEvaluationRelevance import AccreditationEvaluationRelevance, CriterionEvaluationRelevance
from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType

class CommissionInformatica(Commission):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
    
    def get_accreditation_evaluation(self, scientific_production, 
    accreditation:Accreditation):
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return objeto AccreditationEvaluationRelevance con los resultados del criterio de la comisión de las Commissions que tienen como criterio las relevancias de las publicaciones.
        """
        eval:AccreditationEvaluationRelevance = AccreditationEvaluationRelevance(scientific_production=scientific_production, 
        accreditation=accreditation)
        if accreditation.type == AccreditationType.CATEDRA:
            return self.get_catedra(eval)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            return self.get_titularidad(eval)  

    def create_observation(self, eval:AccreditationEvaluationRelevance, assessment: str) -> str:
        """
        Método que construye el mensaje que se mostrará si no se cumplen los criterios para
        la valoración indicada como parámetro
        :param AccreditationEvaluationRelevance eval: Evaluación con los resultados obtenidos.
        :param str valoracion: Cadena de texto con la valoracion no alcanzada para generar el mensaje
        :return str: Mensaje generado con los parametros indicados.
        """
        observation = 'La valoración  ' + assessment + ' podría resultar ' + ('positiva' if eval.positive else 'negativa') + ' obteniéndose los siguientes resultados:\nNúmero de publicaciones relevantes necesarias: ' + str(eval.criterio.num_relevant)
        if eval.arts_relevant:
            observation += ' obtenidas: ' + str(len(eval.arts_relevant)) + '.\n' 
        else:
            observation += ' obtenidas: 0. \n'
        observation +='Número de publicaciones muy relevantes necesarias: ' + str(eval.criterio.num_m_relevant)
        if eval.arts_m_relevant:
            observation += ' obtenidas: ' + str(len(eval.arts_m_relevant)) + '.\n\n'
        else:
            observation += ' obtenidas: 0. \n\n'        
        return observation  
    
    def get_evaluacion(self, eval:AccreditationEvaluationRelevance, assessment:str='') -> AccreditationEvaluationRelevance:
        """
        Método para la evaluacion de los criterios

        :param AccreditationEvaluationRelevance eval: evaluacion sobre la que se hidratará el criterio.
        :param str valoracion: Cadena de texto con la valoración objetivo de la evaluación.
        :return AccreditationEvaluationRelevance eval: Evalucacion con el resultado de la evaluación.
        """
        if len(eval.scientific_production) >= eval.criterio.num_relevant:
            arts_relevant = []
            arts_m_relevant = []
            for pc in eval.scientific_production:
                if pc.get_decile() == 1:
                    arts_m_relevant.append(pc)
                else: 
                    arts_relevant.append(pc)
            
            eval.arts_m_relevant = arts_m_relevant
            eval.arts_relevant = arts_relevant

            if len(eval.arts_m_relevant) >= eval.criterio.num_m_relevant:
                eval.positive = True
                eval.assessment = assessment
        else:
            eval.arts_relevant = eval.scientific_production
     
        eval.observation += self.create_observation(eval, assessment)

        return eval

    def get_titularidad(self, evaluation:AccreditationEvaluationRelevance=None):
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param [] evaluación: objeto evaluación que contiene el criterio y la producción científica.
        :return objeto AccreditationEvaluationRelevance con los resultados del criterio de la comisión de las Commissions que tienen como criterio las relevancias de las publicaciones.
        """
        evaluation = self.get_titularidad_A(evaluation)
        if not evaluation.positive:
            evaluation = self.get_titularidad_B(evaluation)
        return evaluation
    
    def get_catedra(self, evaluation:AccreditationEvaluationRelevance=None) -> AccreditationEvaluationRelevance:
        """
        Metodo para la evaluación de la catedra de un investigador

        :param [] evaluación: objeto evaluación que contiene el criterio y la producción científica.
        :return objeto AccreditationEvaluationRelevance con los resultados del criterio de la comisión de las Commissions que tienen como criterio las relevancias de las publicaciones.
        """
        # suponiendo que prod cientif solo son artículos
        evaluation=self.get_catedra_A(evaluation)
        if not evaluation.positive:
            evaluation = self.get_catedra_B(evaluation)
        return evaluation

    def set_criterion(self, evaluation:AccreditationEvaluationRelevance, assessment:str='') -> AccreditationEvaluationRelevance:
        """
        Método que hidrata el criterio a la propiedad criterio de la evaluación.        :param evaluación sobre la que se hidratará el criterio
        :param valoración valoración que se utilizará para obtener los parámetros 
        """
        if evaluation:
            conf = self.get_configuration_criterion(evaluation.accreditation.type, assessment)
            if conf:
                evaluation.criterio = CriterionEvaluationRelevance(conf['n_relevantes'],conf['n_muy_relevantes'])
        return evaluation

    def get_titularidad_A(self, evaluation:AccreditationEvaluationRelevance) -> AccreditationEvaluationRelevance:
        """
        Metodo para la evaluacion con valoracion A de la titularidad de un investigador
        
        :param evaluación sobre la que se hidratará el criterio
        :return objeto AccreditationEvaluationRelevance con los resultados del criterio de la comisión de las Commissions que tienen como criterio las relevancias de las publicaciones.
        """
        evaluation = self.set_criterion(evaluation, 'A')
        return self.get_evaluacion(evaluation, "A")

    def get_titularidad_B(self, evaluation:AccreditationEvaluationRelevance) -> AccreditationEvaluationRelevance:
        """
        Metodo para la evaluacion con valoracion B de la titularidad de un investigador
        
        :param evaluación sobre la que se hidratará el criterio
        :return objeto AccreditationEvaluationRelevance con los resultados del criterio de la comisión de las Commissions que tienen como criterio las relevancias de las publicaciones.
        """
        evaluation = self.set_criterion(evaluation, 'B')
        return self.get_evaluacion(evaluation, "B")

    def get_catedra_A(self, evaluation:AccreditationEvaluationRelevance) -> AccreditationEvaluationRelevance:
        """
        Metodo para la evaluacion con valoracion A de la catedra de un investigador
        
        :param evaluación sobre la que se hidratará el criterio
        :return objeto AccreditationEvaluationRelevance con los resultados del criterio de la comisión de las Commissions que tienen como criterio las relevancias de las publicaciones.
        """
        evaluation =self.set_criterion(evaluation, 'A')
        return self.get_evaluacion(evaluation,"A")

    def get_catedra_B(self, evaluation:AccreditationEvaluationRelevance) -> AccreditationEvaluationRelevance:
        """
        Metodo para la evaluacion con valoracion B de la catedra de un investigador
        
        :param evaluación sobre la que se hidratará el criterio
        :return objeto AccreditationEvaluationRelevance con los resultados del criterio de la comisión de las Commissions que tienen como criterio las relevancias de las publicaciones.
        """
        evaluation = self.set_criterion(evaluation, 'B')
        return self.get_evaluacion(evaluation, "B")

   
        
    

        
