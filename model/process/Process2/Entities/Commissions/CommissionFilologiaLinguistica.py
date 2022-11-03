from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationFilologiaLinguistica import CriterionEvaluationFilologiaLinguistica, AccreditationEvaluationFilologiaLinguistica
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationCategory, AccreditationType
# comisión 21

class CommissionFilologiaLinguistica(Commission):
    """
    La comisión de Filología y Lingüistica se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_accreditation_evaluation(self, scientific_production: list, 
    accreditation: Accreditation) -> AccreditationEvaluationFilologiaLinguistica:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando. Encajar la subcategoría "investigación" o "docencia"
        :return El objeto EvaluacionAcreditación que contiene la evaluación de la acreditación solicitada.
        """
        evaluation = AccreditationEvaluationFilologiaLinguistica(scientific_production=scientific_production, accreditation=accreditation)
        if accreditation.type == AccreditationType.CATEDRA:        
            criteria = self.get_configuration_criterion(accreditation.type)
            if criteria:
                evaluation.criterion = CriterionEvaluationFilologiaLinguistica(criteria['B']['min_publicaciones'], criteria['B']['n1_publicaciones'], criteria['min_porcentaje'])
            if accreditation.category == AccreditationCategory.DOCENCIA:
                return self.get_catedra_docencia(scientific_production, evaluation=evaluation)
            elif accreditation.category == AccreditationCategory.INVESTIGACION: 
                return self.get_catedra_investigacion(scientific_production, evaluation=evaluation)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            criteria = self.get_configuration_criterion(accreditation.type)
            if criteria:
                evaluation.criterion = CriterionEvaluationFilologiaLinguistica(criteria['B']['min_publicaciones'], criteria['B']['n1_publicaciones'], criteria['min_porcentaje'])      
            if accreditation.category == AccreditationCategory.DOCENCIA:
                return self.get_titularidad_docencia(scientific_production, evaluation=evaluation)
            elif accreditation.category == AccreditationCategory.INVESTIGACION:
                return self.get_titularidad_investigacion(scientific_production, evaluation=evaluation)

    def get_catedra_investigacion(self, scientific_production: list, 
    evaluation: AccreditationEvaluationFilologiaLinguistica) -> AccreditationEvaluationFilologiaLinguistica:
        """
        Método para la evaluación de la cátedra de investigación de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Filología y Lingüistica.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Filología y Lingüistica.
        """

        eval, arts_t1 = self.criterion_investigacion_catedra(scientific_production, evaluation.criterion.num_arts, evaluation.criterion.num_t1, evaluation.criterion.min_percent)
        if eval:
            evaluation.positive = eval
            evaluation.publications_n1 = arts_t1
            evaluation.observation = self.observation_catedra_investigacion(evaluation)
        return evaluation

    def get_catedra_docencia(self, scientific_production: list, 
    evaluation: AccreditationEvaluationFilologiaLinguistica) -> AccreditationEvaluationFilologiaLinguistica:
        """
        Método para la evaluación de la cátedra de docencia de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Filología y Lingüistica.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Filología y Lingüistica.
        """
        evaluation.positive = False
        evaluation.publications_n1 = []
        evaluation.observation = self.observation_catedra_investigacion(evaluation)
        return evaluation

    def get_titularidad_investigacion(self, scientific_production: list, 
    evaluation: AccreditationEvaluationFilologiaLinguistica) -> AccreditationEvaluationFilologiaLinguistica:
        """
        Método para la evaluación de la cátedra de docencia de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Filología y Lingüistica.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Filología y Lingüistica.
        """

        eval, arts_t1 = self.criterion_investigacion_titularidad(scientific_production,  evaluation.criterion.num_arts, evaluation.criterion.num_t1, evaluation.criterion.min_percent)
        if eval:
            evaluation.positive = eval
            evaluation.publications_n1 = arts_t1
        evaluation.observation += self.observation_titularidad_investigacion(evaluation)
        return evaluation

    def get_titularidad_docencia(self, scientific_production: list, 
    evaluation: AccreditationEvaluationFilologiaLinguistica) -> AccreditationEvaluationFilologiaLinguistica:
        """
        Método para la evaluación de la cátedra de docencia de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Filología y Lingüistica.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Filología y Lingüistica.
        """

        evaluation.positive = False
        evaluation.publications_n1 = []
        evaluation.observation += "No es posible evaluar los criterios de esta acreditación ya que se tiene en cuenta la experiencia."
        return evaluation

    def criterion_investigacion_catedra(self, scientific_production: list, num_publications: int, 
    num_n1: int, min_percent: int) -> tuple([bool, []]):
        """
        Método que define el criterio de una cátedra de investigación.

        :param [] produccion_cientifica: Listado de publicaciones de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1: Número de publicaciones de nivel 1 necesarias para cumplir el criterio.
        :param int porcentaje_min: Porcentaje sobre el total necesario para considerar que el critero esté completo.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones de nivel 1.
        """
        result = False
        publications_n1 = []

        if len(scientific_production) >= num_publications*(min_percent/100):
            for article in scientific_production:
                if article.get_tertile() == 1:
                    publications_n1.append(article)
            if len(publications_n1) >= num_n1*(min_percent/100):
                #Option 1
                result = True
                return result, publications_n1
            elif len(publications_n1) >= (num_n1*(min_percent/100)):
                #Option 2
                result = True
                return result, publications_n1
        return result, publications_n1

    def observation_catedra_investigacion(self, evaluation: AccreditationEvaluationFilologiaLinguistica) -> str:
        """
        Método que completa el atributo observación del criterio de la cátedra de investigación.

        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la cátedra de la investigación.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la cátedra de investigación ha resultado ' + str(evaluation.positive) + '.\n Se han obtenido ' + str(len(evaluation.publications_n1)) + ' publicaciones de nivel 1. No se están contando las monografías para esta comisión.'


    def criterion_investigacion_titularidad(self, scientific_production: list, num_publications: int, 
    num_n1: int, min_percent: int) -> tuple([bool, []]):
        """
        Método que define el criterio de una cátedra de titularidad.

        :param [] produccion_cientifica: Listado de publicaciones de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1: Número de publicaciones de nivel 1 necesarias para cumplir el criterio.
        :param int porcentaje_min: Porcentaje sobre el total necesario para considerar que el critero esté completo.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones de nivel 1.
        """
        result = False
        publications_n1 = []

        if len(scientific_production) >= num_publications*(min_percent/100):
            for art in scientific_production:
                if art.get_tertile() == 1:
                    publications_n1.append(art)
            if len(publications_n1) >= num_n1*(min_percent/100):
                result = True
                return result, publications_n1
        return result, publications_n1    

    def observation_titularidad_investigacion(self, evaluation: AccreditationEvaluationFilologiaLinguistica) -> str:
        """
        Método que completa el atributo observación del criterio de la titularidad de investigación.

        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la cátedra de la investigación.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la titularidad de investigación ha resultado ' + ("positivo" if evaluation.positive else "negativo") + '.\n Se han obtenido ' + str(len(evaluation.publications_n1)) + ' publicaciones de nivel 1. No se están contando las monografías para esta comisión. \n\n'
