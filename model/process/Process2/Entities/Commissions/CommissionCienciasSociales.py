from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationCienciasSociales import CriterionEvaluationCienciasSociales, AccreditationEvaluationCienciasSociales
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType


class CommissionCienciasSociales(Commission):
    """
    La comisión de Ciencias sociales se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluator, is_commission: bool = True):
        super().__init__(id, evaluator, is_commission)

    def get_accreditation_evaluation(self, scientific_production, accreditation: Accreditation) -> AccreditationEvaluationCienciasSociales:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return El objeto AccreditationEvaluationCienciasSociales que contiene la evaluación de la acreditación solicitada.
        """
        evaluation = AccreditationEvaluationCienciasSociales(scientific_production=scientific_production, accreditation=accreditation)
        if accreditation.type == AccreditationType.CATEDRA:
            criteria = self.get_configuration_criterion(accreditation.type)
            if criteria:
                evaluation.criterion = CriterionEvaluationCienciasSociales(criteria['A']['min_publicaciones'],criteria['B']['min_publicaciones'], criteria['A']['l1l2_publicaciones'],criteria['B']['l1_publicaciones'],criteria['B']['l2_publicaciones'], criteria['min_porcentaje'])
            return self.get_catedra(scientific_production, evaluation)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            criteria = self.get_configuration_criterion(accreditation.type)
            if criteria:
                evaluation.criterion = CriterionEvaluationCienciasSociales(criteria['A']['min_publicaciones'],criteria['B']['min_publicaciones'], criteria['A']['l1l2_publicaciones'],criteria['B']['l1l2_publicaciones'],criteria['B']['l1l2_publicaciones'], criteria['min_porcentaje'])
            return self.get_titularidad(scientific_production, evaluation)

    def get_catedra(self, scientific_production, evaluation:AccreditationEvaluationCienciasSociales) -> AccreditationEvaluationCienciasSociales:
        """
        Método para la evaluación de la cátedra de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionCienciasSociales evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Ciencias Sociales.
        :return El objeto AccreditationEvaluationCienciasSociales con los resultados del criterio de la comisión de Ciencias Sociales.
        """
        eval, assessment, art_n1, art_n2 = self.get_criterio_catedra_A(scientific_production, evaluation.criterion.num_art_A, evaluation.criterion.num_t1_t2_A, evaluation.criterion.min_percent)
        evaluation.observation += self.create_observations_catedra(evaluation, scientific_production)
        if eval and assessment == 'A':
            evaluation.positive = eval
            evaluation.publications_n1 = art_n1
            evaluation.publications_n2 = art_n2
            evaluation.assessment = assessment
            return evaluation
        eval, assessment, art_n1, art_n2 = self.get_criterio_catedra_B_C_D(scientific_production, evaluation.criterion.num_art_BC, evaluation.criterion.num_t1_t2_A, evaluation.criterion.min_percent)
        if eval and assessment == 'B':
            evaluation.positive = eval
            evaluation.publications_n1 = art_n1
            evaluation.publications_n2 = art_n2
            evaluation.assessment = assessment
            evaluation.observation = self.create_observations_catedra(evaluation, scientific_production)
            return assessment
        if eval and assessment == 'C':
            evaluation.positive = eval
            evaluation.publications_n1 = art_n1
            evaluation.publications_n2 = art_n2
            evaluation.assessment = assessment
            evaluation.observation = self.create_observations_catedra(evaluation, scientific_production)
            return assessment
        if eval and assessment == 'D':
            evaluation.positive = eval
            evaluation.publications_n1 = art_n1
            evaluation.publications_n2 = art_n2
            evaluation.assessment = assessment
            evaluation.observation = self.create_observations_catedra(evaluation, scientific_production)
            return assessment

    def get_titularidad(self, scientific_production, evaluation:AccreditationEvaluationCienciasSociales) -> AccreditationEvaluationCienciasSociales:
        """
        Método para la evaluación de la titularidad de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param AccreditationEvaluationCienciasSociales evaluacion: El resultado del criterio de la comisión de Ciencias Sociales.
        :return El objeto AccreditationEvaluationCienciasSociales con los resultados del criterio de la comisión de Ciencias Sociales.
        """
        eval, assessment, art_n1, art_n2 = self.get_criterion_titularidad_A(scientific_production, evaluation.criterion.num_art_A, evaluation.criterion.num_t1_t2_A, evaluation.criterion.min_percent)
        evaluation.observation += self.create_observations_titularidad(evaluation, scientific_production)
        if eval and assessment == 'A':
            evaluation.positive = eval
            evaluation.publications_n1 = art_n1
            evaluation.publications_n2 = art_n2
            evaluation.assessment = assessment
            return evaluation
        eval, assessment, art_n1, art_n2 = self.get_criterion_titularidad_B_C_D(scientific_production, evaluation.criterion.num_art_BC, evaluation.criterion.num_t1_BC, evaluation.criterion.num_t2_BC, evaluation.criterion.min_percent)
        evaluation.observation += self.create_observations_titularidad(evaluation, scientific_production)
        if eval and assessment == 'B':
            evaluation.positive = eval
            evaluation.publications_n1 = art_n1
            evaluation.publications_n2 = art_n2
            evaluation.assessment = assessment
            return assessment
        if eval and assessment == 'C':
            evaluation.positive = eval
            evaluation.publications_n1 = art_n1
            evaluation.publications_n2 = art_n2
            evaluation.assessment = assessment
            evaluation.observation = self.create_observations_titularidad(evaluation, scientific_production)
            return assessment
        if eval and assessment == 'D':
            evaluation.positive = eval
            evaluation.publications_n1 = art_n1
            evaluation.publications_n2 = art_n2
            evaluation.assessment = assessment
            evaluation.observation = self.create_observations_titularidad(evaluation, scientific_production)
            return assessment

    def get_criterio_catedra_A(self, scientific_production: list, num_publications : int, 
    num_n1_n2 : int, min_percent : int) -> tuple([bool, str, [], []]):
        """
        Método para la evaluación del criterio que hay que superar para la obtención de una cátedra por parte del investigador.

        :param [] produccion_cientifica: Lista de producción científica de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones necesarias de nivel 1 (cuartiles 1 y 2) y nivel 2 (cuartiles 3 y 4).
        :param int porcentaje_min: Tanto por ciento mínimo necesario para determinar el critero de la cátedra de evaluación A a B.
        :return Tupla compuesta por un booleano que nos indica si es positiva la evaluación, un str con el típo de calificación en investigación y dos listas con los artículos de nivel 1 y nivel 2 presentados.
        """
        art_n1 = []
        art_n2 = []
        assessment = ''
        result = False
        if len(scientific_production) >= num_publications:
            for article in scientific_production:
                if article.get_tertile() == 1:
                    art_n1.append(article)
                elif article.get_tertile() == 2:
                    art_n2.append(article)
            if art_n1 and art_n2 and (len(art_n1) + len(art_n2)) >= num_n1_n2:
                result = True
                assessment = 'A'
                return result, assessment, art_n1, art_n2
        if len(scientific_production) >= (num_publications*(min_percent/100)):
            for article in scientific_production:
                if article.get_tertile() == 1:
                    art_n1.append(article)
                elif article.get_tertile() == 2:
                    art_n2.append(article)
            if art_n1 and art_n2 and (len(art_n1) + len(art_n2)) >= (num_n1_n2*(min_percent/100)):
                result = True
                assessment = 'A'
                return result, assessment, art_n1, art_n2
        return result, assessment, art_n1, art_n2

    def get_criterio_catedra_B_C_D(self, scientific_production: list, num_publications: int,
    num_n1: int, num_n2: int, min_percent: int) -> tuple([bool, str, [], []]):
        """
        Método para la evaluación del criterio que hay que superar para la obtención de una cátedra por parte del investigador.

        :param [] produccion_cientifica: Lista de producción científica de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones necesarias de nivel 1 (cuartiles 1 y 2) y nivel 2 (cuartiles 3 y 4).
        :param int porcentaje_min: Tanto por ciento mínimo necesario para determinar el critero de la cátedra de evaluación A a B.
        :return Tupla compuesta por un booleano que nos indica si es positiva la evaluación, un str con el típo de calificación en investigación y dos listas con los artículos de nivel 1 y nivel 2 presentados.        
        """
        art_n1 = []
        art_n2 = []
        assessment = ''
        result = False
        if len(scientific_production) >= num_publications:
            for article in scientific_production:
                if article.get_tertile() == 1:
                    art_n1.append(article)
                elif article.get_tertile() == 2:
                    art_n2.append(article)
            if art_n1 and art_n2 and len(art_n1) >= num_n1 and len(art_n2) >= num_n2:
                result = True
                assessment = 'B'
                return result, assessment, art_n1, art_n2
        if len(scientific_production) >= (num_publications*(min_percent/100)):
            for article in scientific_production:
                if article.get_tertile() == 1:
                    art_n1.append(article)
                elif article.get_tertile() == 2:
                    art_n2.append(article)
            if art_n1 and art_n2:
                if len(art_n1) >= (num_n1*(min_percent/100)) and len(art_n2) >= (num_n2*(min_percent/100)):
                    result = True
                    assessment = 'B'
                    return result, assessment, art_n1, art_n2
                else:
                    result = True
                    assessment = 'C'
                    return result, assessment, art_n1, art_n2
        result = False
        assessment = 'D'
        return result, assessment, art_n1, art_n2

    def get_criterion_titularidad_A(self, scientific_production: list, 
    num_publications : int, num_n1_n2 : int, min_percent : int) -> tuple([bool, str, [], []]):
        """
        Método para la evaluación del criterio que hay que superar para la obtención de una titularidad por parte del investigador.

        :param [] produccion_cientifica: Lista de producción científica de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones necesarias de nivel 1 (cuartiles 1 y 2) y nivel 2 (cuartiles 3 y 4).
        :param int porcentaje_min: Tanto por ciento mínimo necesario para determinar el critero de la cátedra de evaluación A a B.
        :return Tupla compuesta por un booleano que nos indica si es positiva la evaluación, un str con el típo de calificación en investigación y dos listas con los artículos de nivel 1 y nivel 2 presentados.
        """
        art_n1 = []
        art_n2 = []
        assessment = ''
        result = False
        if len(scientific_production) >= num_publications:
            for article in scientific_production:
                if article.get_tertile() == 1:
                    art_n1.append(article)
                elif article.get_tertile() == 2:
                    art_n2.append(article)
            if art_n1 and art_n2 and (len(art_n1) + len(art_n2)) >= num_n1_n2:
                result = True
                assessment = 'A'
                return result, assessment, art_n1, art_n2
        if len(scientific_production) >= (num_publications*(min_percent/100)):
            for article in scientific_production:
                if article.get_tertile() == 1:
                    art_n1.append(article)
                elif article.get_tertile() == 2:
                    art_n2.append(article)
            if art_n1 and art_n2 and (len(art_n1) + len(art_n2)) >= (num_n1_n2*(min_percent/100)):
                result = True
                assessment = 'A'
                return result, assessment, art_n1, art_n2
        result = False
        assessment = 'D'
        return result, assessment, art_n1, art_n2

    def get_criterion_titularidad_B_C_D(self, scientific_production: list, 
    num_publications: int, num_n1: int, num_n2: int, min_percent: int) -> tuple([bool, str, [], []]):
        """
        Método para la evaluación del criterio que hay que superar para la obtención de una titularidad por parte del investigador.

        :param [] produccion_cientifica: Lista de producción científica de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones necesarias de nivel 1 (cuartiles 1 y 2) y nivel 2 (cuartiles 3 y 4).
        :param int porcentaje_min: Tanto por ciento mínimo necesario para determinar el critero de la cátedra de evaluación A a B.
        :return Tupla compuesta por un booleano que nos indica si es positiva la evaluación, un str con el típo de calificación en investigación y dos listas con los artículos de nivel 1 y nivel 2 presentados.        
        """
        art_n1 = []
        art_n2 = []
        assessment = ''
        result = False
        if len(scientific_production) >= num_publications:
            for article in scientific_production:
                if article.get_tertile() == 1:
                    art_n1.append(article)
                elif article.get_tertile() == 2:
                    art_n2.append(article)
            if art_n1 and art_n2 and len(art_n1) >= num_n1 and len(art_n2) >= num_n2:
                result = True
                assessment = 'B'
                return result, assessment, art_n1, art_n2
        if len(scientific_production) >= (num_publications*(min_percent/100)):
            for article in scientific_production:
                if article.get_tertile() == 1:
                    art_n1.append(article)
                elif article.get_tertile() == 2:
                    art_n2.append(article)
            if art_n1 and art_n2:
                if len(art_n1) >= (num_n1*(min_percent/100)) and len(art_n2) >= (num_n2*(min_percent/100)):
                    result = True
                    assessment = 'B'
                    return result, assessment, art_n1, art_n2
                else:
                    result = True
                    assessment = 'C'
                    return result, assessment, art_n1, art_n2     
        return result, assessment, art_n1, art_n2

    def create_observations_catedra(self, evaluation: AccreditationEvaluationCienciasSociales,
     scientific_production: list) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la cátedra.

        :param EvaluacionAcreditacionCienciasSociales evaluacion: Objeto EvaluacionAcreditacion de Ciencias Sociales donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :return String con la evaluación de la comisión de Ciencias Sociales.
        """
        return "En el resultado de la valoración para el criterio de la cátedra se podría obtener un resultado " + ("positivo" if evaluation.positive else "negativo") + " con una valoración " + (evaluation.assessment if evaluation.assessment != '' else "-") + ".\n Número de publicaciones necesarias " + str(evaluation.criterion.num_art_A) + ". Obtenidas: " + str(len(scientific_production)) + " de las cuales las de nivel 1 hemos obtenido " + str(len(evaluation.publications_n1)) + " y de nivel 2 hemos obtenido: " + str(len(evaluation.publications_n2)) + ".\n\n" 

    def create_observations_titularidad(self, evaluation: AccreditationEvaluationCienciasSociales, 
    scientific_production: list) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la titularidad.

        :param EvaluacionAcreditacionCienciasSociales evaluacion: Objeto EvaluacionAcreditacion de Ciencias Sociales donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :return String con la evaluación de la comisión de Ciencias Sociales.
        """
        return "En el resultado de la valoración para el criterio de la titularidad se podría obtener un resultado " + ("positivo" if evaluation.positive else "negativo") + " con una valoración " + (evaluation.assessment if evaluation.assessment != '' else "-") + ".\n Número de publicaciones necesarias " + str(evaluation.criterion.num_art_A) + ". Obtenidas: " + str(len(scientific_production)) + " de las cuales las de nivel 1 hemos obtenido " + str(len(evaluation.publications_n1)) + " y de nivel 2 hemos obtenido: " + str(len(evaluation.publications_n2)) + ".\n\n" 