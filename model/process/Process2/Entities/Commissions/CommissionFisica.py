from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationFisica import CriterionEvaluationFisica, AccreditationEvaluationFisica
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType
# comisión 2

class CommissionFisica(Commission):
    """
    La comisión de Física se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluator, is_commission: bool = True):
        super().__init__(id, evaluator, is_commission)
        
    def get_accreditation_evaluation(self, scientific_production, 
    accreditation: Accreditation) -> AccreditationEvaluationFisica:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return El objeto EvaluacionAcreditación que contiene la evaluación de la acreditación solicitada.
        """
        evaluation = AccreditationEvaluationFisica(scientific_production, accreditation)
        if accreditation.type == AccreditationType.CATEDRA:
            criteria = self.get_configuration_criterion(accreditation.type)
            if criteria:
                evaluation.criterion = CriterionEvaluationFisica(criteria['O1']['min_publicaciones'],criteria['O1']['t1_publicaciones'],criteria['O2']['t1t2_publicaciones'],criteria['O3']['t1_publicaciones'])
            return self.get_catedra(scientific_production, evaluation=evaluation)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            criteria = self.get_configuration_criterion(accreditation.type)
            if criteria:
                evaluation.criterion = CriterionEvaluationFisica(criteria['O1']['min_publicaciones'],criteria['O1']['t1_publicaciones'],criteria['O2']['t1t2_publicaciones'],criteria['O3']['t1_publicaciones'])
            return self.get_titularidad(scientific_production, evaluation=evaluation)

    def get_catedra(self, scientific_production, evaluation:AccreditationEvaluationFisica) -> AccreditationEvaluationFisica:
        """
        Método para la evaluación de la titularidad de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFisica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Física.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Física.
        """

        eval, arts_t1, arts_t2 = self.criterion1_T1(scientific_production, evaluation.criterion.min_arts, evaluation.criterion.num_t1)
        evaluation.observation += self.create_observation_criterion_1(evaluation)
        if eval:
            evaluation.positive = eval
            evaluation.arts_t1 = arts_t1
            evaluation.arts_t2 = arts_t2
            return evaluation
        eval, arts_t1, arts_t2 = self.criterion2_T1_T2(scientific_production, evaluation.criterion.min_arts, evaluation.criterion.num_t1_t2)
        evaluation.observation += self.create_observation_criterion_2(evaluation)
        if eval:
            evaluation.positive = eval
            evaluation.arts_t1 = arts_t1
            evaluation.arts_t2 = arts_t2     
            return evaluation
        eval, arts_t1, arts_t2 = self.criterion3_T1(scientific_production, evaluation.criterion.min_t1, evaluation.criterion.min_t1)
        evaluation.observation = self.create_observation_criterion_3(evaluation)
        if eval:
            evaluation.positive = eval
            evaluation.arts_t1 = arts_t1
            evaluation.arts_t2 = arts_t2         
        return evaluation

    def get_titularidad(self, scientific_production, evaluation:AccreditationEvaluationFisica) -> AccreditationEvaluationFisica:
        """
        Método para la evaluación de la titularidad de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFisica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Física.
        :return objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Física.
        """
        eval, arts_t1, arts_t2 = self.criterion1_T1(scientific_production, evaluation.criterion.min_arts, evaluation.criterion.num_t1)
        evaluation.observation += self.create_observation_criterion_1(evaluation)
        if eval:
            evaluation.positive = eval
            evaluation.arts_t1 = arts_t1
            evaluation.arts_t2 = arts_t2
            return evaluation
        
        eval, arts_t1, arts_t2 = self.criterion2_T1_T2(scientific_production, evaluation.criterion.min_arts, evaluation.criterion.num_t1_t2)
        evaluation.observation += self.create_observation_criterion_1(evaluation)
        if eval:
            evaluation.positive = eval
            evaluation.arts_t1 = arts_t1
            evaluation.arts_t2 = arts_t2            
            return evaluation

        eval, arts_t1, arts_t2 = self.criterion3_T1(scientific_production, evaluation.criterion.min_t1, evaluation.criterion.min_t1)
        evaluation.observation += self.create_observation_criterion_1(evaluation)
        if eval:
            evaluation.positive = eval
            evaluation.arts_t1 = arts_t1
            evaluation.arts_t2 = arts_t2
            return evaluation
        
        return evaluation
    
    def criterion1_T1(self, scientific_production, num_publications, num_t1) -> tuple([bool, [], []]):
        """
        Método para comprobar cuántos artículos pertenecen al T1 y si cumple con el mínimo establecido de artículos.
        
        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param int num_publicaciones: número de publicaciones necesarias para cumplir el criterio.
        :param int num_t1: número de publicaciones necesarias en el tercil 1.
        :return dupla formada por un booleano si se cumple con el criterio y una lista de artículos seleccionados
        """
        articles = []
        result = False
        if len(scientific_production) >= num_publications:
            for article in scientific_production:
                if article.get_tertile() == 1:
                    articles.append(article)

            if articles and len(articles) >= num_t1:
                result = True
                return (result, articles, [])

        return (result, articles, [])

    def criterion2_T1_T2(self, scientific_production, num_publications, num_t1_t2) -> tuple([bool, [], []]):
        """
        Método para comprobar cuántos artículos pertenecen al T1 y T2 y si cumple con el mínimo establecido de artículos.

        :param [] producción_científica: listado de artículos de un investigador.
        :param int num_publicaciones: número de publicaciones necesarias para cumplir el criterio.
        :param int num_t1_t2: número de publicaciones necesarias en los terciles 1 y 2.
        :return dupla formada por un booleano si se cumple con el criterio y una lista de artículos seleccionados.
        """

        arts_t1 = []
        arts_t2 = []
        result = False
        if len(scientific_production) >= num_publications:
            for article in scientific_production:
                if article.get_tertile() == 1:
                    arts_t1.append(article)
                elif article.get_tertile() == 2:
                    arts_t2.append(article)

            if arts_t1 and arts_t2 and (len(arts_t1) + len(arts_t2)) >= num_t1_t2:
                result = True
                return (result, arts_t1, arts_t2)
        
        return (result, arts_t1, arts_t2)

    def criterion3_T1(self, scientific_production, num_publications, num_t1) -> tuple([bool, [], []]):
        """
        Método para comprobar cuantos artículos pertenecen al T1 y si cumple con el mínimo establecido de artículos.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param int num_publicaciones: número de publicaciones necesarias para cumplir el criterio.
        :param int num_t1: número de publicaciones necesarias en el tercil 1.
        :return dupla formada por un booleano si se cumple con el criterio y una lista de artículos seleccionados
        """

        articles = []
        result = False
        if len(scientific_production) >= num_publications:
            for article in scientific_production:
                if article.get_tertile() == 1:
                    articles.append(article)

            if articles and len(articles) >= num_t1:
                result = True
                return (result, articles)

        return (result, articles, [])

    def create_observation_criterion_1(self, evaluation: AccreditationEvaluationFisica) -> str:
        """
        Método para rellenar el campo observaciones con el resultado de la evaluación del criterio 1.

        :param EvaluacionAcreditacionFisica evaluacion: Objeto EvaluacionAcreditacion de Física donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :param int num_t1: Número de publicaciones necesarias en el tercil 1 para el criterio.
        :return String con la evaluación de la comisión de Física
        """
        return 'En el resultado de la valoracion del primer criterio se han obtenido los siguientes resultados: \n' + 'Número de publicaciones totales necesarias: ' + str(evaluation.criterion.min_arts) + '. Obtenidas: ' + str(len(evaluation.arts_t1)+len(evaluation.arts_t2)) + '. \n Número de publicaciones necesarias en el tercil 1: ' + str(evaluation.criterion.num_t1) + '. Obtenidas: ' + str(len(evaluation.arts_t1)) + ". \n\n"

    def create_observation_criterion_2(self, evaluation: AccreditationEvaluationFisica) -> str:
        """
        Método para rellenar el campo observaciones con el resultado de la evaluación del critero 2.

        :param EvaluacionAcreditacionFisica evaluacion: Objeto EvaluacionAcreditacion de Física donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :param int num_t1_t2: Número de publicaciones necesarias en el tercil 1 y tercil 2 para el criterio.
        :return String con la evaluación de la comisión de Física
        """
        return 'En el resultado de la valoracion del segundo criterio se podría obtener una valoración ' +  ("positiva" if evaluation.positive else "negativa") + ' teniendo los siguientes resultados: \n' + 'Número de publicaciones totales necesarias: ' + str(evaluation.criterion.min_arts) + '. Obtenidas: ' + str(len(evaluation.arts_t1)+len(evaluation.arts_t2)) + '. \n Número de publicaciones necesarias entre el tercil 1 y el tercil 2: ' + str(evaluation.criterion.num_t1_t2) + '. Obtenidas: ' + str(len(evaluation.arts_t1)+len(evaluation.arts_t2)) + ". \n\n"
        
    def create_observation_criterion_3(self, evaluation: AccreditationEvaluationFisica) -> str:
        """
        Método para rellenar el campo observaciones con el resultado de la evaluación del criterio 3.

        :param EvaluacionAcreditacionFisica evaluacion: Objeto EvaluacionAcreditacion de Física donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :param int num_t1: Número de publicaciones necesarias en el tercil 1 para el criterio.
        :return String con la evaluación de la comisión de Física
        """
        return 'En el resultado de la valoracion del tercer criterio se podría obtener una valoración ' +  ("positiva" if evaluation.positive else "negativa") + ' teniendo los siguientes resultados: \n' + 'Número de publicaciones totales necesarias: ' + str(evaluation.criterion.min_t1) + '. Obtenidas: ' + str(len(evaluation.arts_t1)+len(evaluation.arts_t2)) + '. \n Número de publicaciones necesarias en el tercil 1: ' + str(evaluation.criterion.min_t1) + '. Obtenidas: ' + str(len(evaluation.arts_t1)) + ". \n\n"
    