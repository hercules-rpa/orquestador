from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType
from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationOtrasEspecialidadesSanitarias import CriterionEvaluationOtrasEspecialidadesSanitarias, AccreditationEvaluationOtrasEspecialidadesSanitarias


class CommissionOtrasEspecialidadesSanitarias(Commission):
    def get_accreditation_evaluation(self, scientific_production, 
    accreditation: Accreditation) -> AccreditationEvaluationOtrasEspecialidadesSanitarias:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] scientific_production: listado de artículos de un investigador.
        :param Accreditation accreditation: tipo de acreditación que se está solicitando.
        :return El objeto AccreditationEvaluation que contiene la evaluación de la acreditación solicitada.
        """
        evaluation = AccreditationEvaluationOtrasEspecialidadesSanitarias(scientific_production=scientific_production, acreditacion=accreditation)
        
        if accreditation.type == AccreditationType.CATEDRA:
            return self.get_catedra(scientific_production, evaluation)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            return self.get_titularidad(scientific_production, evaluation)

    def set_criterion(self, evaluation:AccreditationEvaluationOtrasEspecialidadesSanitarias,
    assessment:str=''):
        """
        Método que hidrata el criterio a la propiedad criterio de la evaluación.
        :param evaluación sobre la que se hidratará el criterio
        :param valoración valoración que se utilizará para obtener los parámetros 
        """
        if evaluation:
            conf = self.get_configuration_criterion(evaluation.accreditation.type, assessment)
            if conf:
                evaluation.criterion = CriterionEvaluationOtrasEspecialidadesSanitarias(conf['min_publicaciones'],conf['n_autoria_preferente'],conf['t1_ap_publicaciones'])

    def get_catedra(self, scientific_production, evaluation:AccreditationEvaluationOtrasEspecialidadesSanitarias) -> AccreditationEvaluationOtrasEspecialidadesSanitarias:
        """
        Método para la evaluación de la cátedra de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionOtrasEspecialidadesSanitarias evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Otras Especialidades Sanitarias.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Otras Especialidades Sanitarias.
        """
        self.set_criterion(evaluation,"A")
        eval, assessment, arts_authorship, arts_authorship_t1 = self.get_criterion_1(scientific_production, evaluation.criterion, "A")
        evaluation.observation = self.create_observation(evaluation, "A")
        if eval and assessment == 'A':
            evaluation.positive = eval
            evaluation.articles_authorship = arts_authorship
            evaluation.articles_authorship_t1 = arts_authorship_t1
            evaluation.assessment = assessment
            return evaluation

        self.set_criterion(evaluation,"B")
        eval, assessment, arts_authorship, arts_authorship_t1 = self.get_criterion_1(scientific_production, evaluation.criterion,"B")
        evaluation.observation = self.create_observation(evaluation, "B")
        if eval and assessment == 'B':
            evaluation.positive = eval
            evaluation.articles_authorship = arts_authorship
            evaluation.articles_authorship_t1 = arts_authorship_t1
            evaluation.assessment = assessment
            return evaluation

        self.set_criterion(evaluation,"C")
        eval, assessment, arts_authorship, arts_authorship_t1 = self.get_criterion_1(scientific_production, evaluation.criterion, "C")
        evaluation.observation = self.create_observation(evaluation, "C")
        if eval and assessment == 'C':
            evaluation.positive = eval
            evaluation.articles_authorship = arts_authorship
            evaluation.articles_authorship_t1 = arts_authorship_t1
            evaluation.assessment = assessment
            return evaluation

        evaluation.positive = eval
        evaluation.articles_authorship = arts_authorship
        evaluation.articles_authorship_t1 = arts_authorship_t1
        evaluation.assessment = assessment
        evaluation.observation = self.create_observation(evaluation, "C")
        return evaluation

    def get_titularidad(self, scientific_production, evaluation:AccreditationEvaluationOtrasEspecialidadesSanitarias) -> AccreditationEvaluationOtrasEspecialidadesSanitarias:
        """
        Método para la evaluación de la titularidad de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionOtrasEspecialidadesSanitarias evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Otras Especialidades Sanitarias.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Otras Especialidades Sanitarias.
        """
        self.set_criterion(evaluation,"A")
        eval, assessment, arts_authorship, arts_authorship_t1 = self.get_criterion_1(scientific_production, evaluation.criterion, "A")
        if eval and assessment == 'A':
            evaluation.positive = eval
            evaluation.articles_authorship = arts_authorship
            evaluation.articles_authorship_t1 = arts_authorship_t1
            evaluation.assessment = assessment
            evaluation.observation = self.create_observation(evaluation, "A")
            return evaluation

        self.set_criterion(evaluation,"B")
        eval, assessment, arts_authorship, arts_authorship_t1 = self.get_criterion_1(scientific_production, evaluation.criterion,"B")
        if eval and assessment == 'B':
            evaluation.positive = eval
            evaluation.articles_authorship = arts_authorship
            evaluation.articles_authorship_t1 = arts_authorship_t1
            evaluation.assessment = assessment
            evaluation.observation = self.create_observation(evaluation, "A")
            return evaluation

        self.set_criterion(evaluation,"C")
        eval, assessment, arts_authorship, arts_authorship_t1 = self.get_criterion_1(scientific_production, evaluation.criterion, "C")
        if eval and assessment == 'C':
            evaluation.positive = eval
            evaluation.articles_authorship = arts_authorship
            evaluation.articles_authorship_t1 = arts_authorship_t1
            evaluation.assessment = assessment
            evaluation.observation = self.create_observation(evaluation, "B")
            return evaluation
        
        evaluation.positive = eval
        evaluation.articles_authorship = arts_authorship
        evaluation.articles_authorship_t1 = arts_authorship_t1
        evaluation.assessment = assessment
        evaluation.observation = self.create_observation(evaluation, "C")
        return evaluation

    def get_criterion_1(self, scientific_production: list, criterion: CriterionEvaluationOtrasEspecialidadesSanitarias, assessment: str) -> tuple([bool, str, [], []]):
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param [] produccion_cientifica listado de artículos de un investigador.
        :param CriterioEvaluacionOtrasEspecialidadesSanitarias criterio clase que almacena los numeros necesarios para superar el criterio de evaluacion
        :param str assessment valoración con la que se valora el criterio en caso de superarlo
        :return tupla formada por un booleano si se cumple alguno de los criterios, una cadena de texto con la calificación de la investigacion, una lista de articulos con autoria preferente y una lista de articulos con autoria preferente en tercil 1
        """
        arts_authorship = []
        arts_authorship_t1 = []
        assessment = ''
        result = False
        if len(scientific_production) >= criterion.min_arts:
            authorship_result, arts_authorship = self.get_criterion_authorship(scientific_production, criterion.num_authorship)
            if authorship_result:
                for article in arts_authorship:
                    if article.get_tertile() == 1:
                        arts_authorship_t1.append(article)
                if len(arts_authorship_t1) >= criterion.num_authorship_t1:
                    assessment = assessment
                    result = True
        else:
            assessment = 'D'
        return result, assessment, arts_authorship, arts_authorship_t1

    def get_criterion_authorship(self, scientific_production, num_publications):
        """
        Método que comprueba el criterio de autoria preferente
        (Primer/a firmante, coautoría, ultimo/a firmante y autor/a de correspondencia).
        """
        publications = []
        result: bool = False
        if scientific_production and len(scientific_production) >= num_publications:
            for art in scientific_production:
                if (len(publications) < num_publications) and (art.author_position == 1 or (art.author_position == art.authors_number)):
                    publications.append(art)
        if publications and len(publications) == num_publications:
            result = True

        return (result, publications)

    def create_observation(self, eval: AccreditationEvaluationOtrasEspecialidadesSanitarias, 
        assessment:str) -> str:
        """
        Método que construye el mensaje que se mostrará si no se cumplen los criterios para
        la valoración 
        """
        num_publications = eval.criterion.min_arts
        num_authorship = eval.criterion.num_authorship
        num_authorship_t1 = eval.criterion.num_authorship_t1
        
        observation = 'La valoración podría ser ' + ("positiva" if eval.positive else "negativa") + ' obteniendo en la calificación ' + (assessment if assessment != "" else "-") + '. Los resultados son los siguientes: \n' + \
            'Número de publicaciones obtenidas necesarias: ' + str(num_publications) + ' obtenidas: ' + str(len(eval.scientific_production)) + '\n' 
        observation += 'Autoría preferente, necesarias: ' + \
            str(num_authorship) + ' obtenidas: '
        if eval.articles_authorship:
            observation += str(len(eval.articles_authorship)) + '\n'
        else:
            observation += '0 \n'
        observation += 'Autoría preferente en T1, necesarias: ' + \
            str(num_authorship_t1) + ' obtenidas: '
        if eval.articles_authorship_t1:
            observation += str(len(eval.articles_authorship_t1)) + '\n'
        else:
            observation += '0 \n'

        return observation