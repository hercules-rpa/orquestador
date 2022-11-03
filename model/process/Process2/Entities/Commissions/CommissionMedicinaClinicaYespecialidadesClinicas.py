from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType
from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationMedicinaClinicaYEspecialidades import CriterionEvaluationMedicinaClinicaYespecialidades, AccreditationEvaluationMedicinaClinicaYEspecialidades

#comisión 7

"""
La comisión de Medicina Clínica y Especialidades Clínicas se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
"""

class CommissionMedicinaClinicaYespecialidadesClinicas(Commission):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_accreditation_evaluation(self, scientific_production, accreditation: Accreditation) -> AccreditationEvaluationMedicinaClinicaYEspecialidades:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return objeto EvaluacionAcreditacionMedicinaClinicaYEspecialidades con los resultados del criterio de la comisión de Medicina clinica y Especialidades clinicas.
        """
        evaluation = AccreditationEvaluationMedicinaClinicaYEspecialidades(scientific_production=scientific_production, accreditation=accreditation)

        if accreditation.type == AccreditationType.CATEDRA:
            self.set_criterion(evaluation)
            return self.get_catedra(scientific_production, evaluation=evaluation)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            self.set_criterion(evaluation)
            return self.get_titularidad(scientific_production, evaluation=evaluation)
        
    def set_criterion(self, evaluation:AccreditationEvaluationMedicinaClinicaYEspecialidades):
        """
        Método que hidrata el criterio a la propiedad criterio de la evaluación.
        :param evaluación sobre la que se hidratará el criterio
        """
        if evaluation:
            conf = self.get_configuration_criterion(evaluation.accreditation.type)
            if conf:
                evaluation.criterion = CriterionEvaluationMedicinaClinicaYespecialidades(conf['min_publicaciones'],conf['t1_publicaciones'],conf['min_autor'],conf['t1_ap_publicaciones'])

    def get_catedra(self, scientific_production, evaluation:AccreditationEvaluationMedicinaClinicaYEspecialidades) -> AccreditationEvaluationMedicinaClinicaYEspecialidades:
        """
        Método para la evaluación de la catedra de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param AccreditationEvaluationMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Medicina clinica y Especialidades clinicas.
        :return objeto AccreditationEvaluationMedicinaClinicaYEspecialidades con los resultados del criterio de la comisión de Medicina clinica y Especialidades clinicas.
        """
        eval, arts_t1, arts_t2, arts_authorship, arts_authorship_t1 = self.criterion1_T1(scientific_production, evaluation.criterion.min_arts, evaluation.criterion.num_t1, evaluation.criterion.num_authorship, evaluation.criterion.num_authorship_t1)
        evaluation.positive = eval
        evaluation.arts_t1 = arts_t1
        evaluation.arts_t2 = arts_t2
        evaluation.arts_authorship = arts_authorship
        evaluation.arts_authorship_t1 = arts_authorship_t1
        evaluation.observation += self.create_observations_catedra(evaluation, scientific_production)
        return evaluation

    def get_titularidad(self, scientific_production, evaluation:AccreditationEvaluationMedicinaClinicaYEspecialidades) -> AccreditationEvaluationMedicinaClinicaYEspecialidades:
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param EvaluacionAcreditacionMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Medicina clinica y Especialidades clinicas.
        :return objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Medicina clinica y Especialidades clinicas.
        """
        eval, arts_t1, arts_t2, arts_authorship, arts_authorship_t1 = self.criterion1_T1(scientific_production, evaluation.criterion.min_arts, evaluation.criterion.num_t1, evaluation.criterion.num_authorship, evaluation.criterion.num_authorship_t1)
        evaluation.positive = eval
        evaluation.arts_t1 = arts_t1
        evaluation.arts_t2 = arts_t2
        evaluation.arts_authorship = arts_authorship
        evaluation.arts_authorship_t1 = arts_authorship_t1
        evaluation.observation += self.create_observations_titularidad(evaluation, scientific_production)
        return evaluation

    def criterion1_T1(self, scientific_production, num_publications, num_t1, 
    num_authorship, num_authorship_t1) -> tuple([bool, [], [], [], []]):
        """
        Método para comprobar cuántos articulos pertenecen al T1 y al T2, de cuantos tiene la autoría preferente y si cumple con el minimo establecido de artículos.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param int num_publicaciones: número de publicaciones necesarias para cumplir el criterio.
        :param int num_t1: número de publicacions necesarias en el tercil 1.
        :param int num_autoría: numero de publicaciones con autoría preferente necesarias.
        :param int num_autoría_t1: numero de publicaciones con autoría preferente en el tercil 1 necesarias
        :return tupla formada por un booleano si se cumple el criterio, una lista de articulos en el tercil 1, una lista de articulos en tercil 2, una lista de articulos con autoría preferente y una lista de articulos con autoría preferente en tercil 1.
        """
        arts_t1 = []
        arts_t2 = []
        arts_authorship = []
        arts_authorship_t1 = []
        result = False
        if len(scientific_production) >= num_publications:
            for article in scientific_production:
                if article.get_tertile() == 1:
                    arts_t1.append(article)
                
                if article.get_tertile() == 1:
                    arts_t2.append(article)
            authorship_result, arts_authorship = self.criterion_authorship(scientific_production, num_authorship)
            if authorship_result:
                for article in arts_authorship:
                    if article.get_tertile() == 1:
                        arts_authorship_t1.append(article)
        
            if arts_t1 and arts_t2 and arts_authorship and arts_authorship_t1 and (len(arts_t1) + len(arts_t2)) >= num_publications and len(arts_t1) >= num_t1 and len(arts_authorship) >= num_authorship and len(arts_authorship_t1) >= num_authorship_t1:
                result = True
            else:
                result = False

        return (result, arts_t1, arts_t2, arts_authorship, arts_authorship_t1)

    def criterion_authorship(self, scientific_production, num_publications):
        """
        Método que comprueba el criterio de autoría preferente
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

    def create_observations_catedra(self, evaluation: AccreditationEvaluationMedicinaClinicaYEspecialidades, 
    scientific_production: list) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la cátedra.

        :param AccreditationEvaluationMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacion de Otras Especialidades Sanitarias donde almacenamos los datos de la evaluación.
        :param list scientific_production: Lista de publicaciones proporcionadas para la evaluación.
        :return String con la evaluación de la comisión de Otras especialidades Sanitarias.
        """
        return "En el resultado de la valoración para el criterio de la cátedra se podría obtener un resultado " + ("positivo" if evaluation.positive else "negativo") + " con los siguientes resultados: \n  Número de publicaciones necesarias " + str(evaluation.criterion.min_arts) + ". Obtenidas: " + str(len(scientific_production)) + ". \n Número de publicaciones necesarias en el tercil 1: " + str(evaluation.criterion.num_t1) + " Obtenidas: " + str(len(evaluation.arts_t1)) + " \n Número de publicaciones con autoría preferente " + str(evaluation.criterion.num_authorship) + " Obtenidas: " + str(len(evaluation.arts_authorship_t1)) + " Número de publicaciones con autoría preferente en tercil 1: " + str(evaluation.criterion.num_authorship_t1) + " Obtenidas: " + str(len(evaluation.arts_authorship_t1)) + ".\n\n"

    def create_observations_titularidad(self, evaluation: AccreditationEvaluationMedicinaClinicaYEspecialidades, 
    scientific_production: list) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la titularidad.

        :param AccreditationEvaluationMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacion de Otras Especialidades Sanitarias donde almacenamos los datos de la evaluación.
        :param list scientific_production: Lista de publicaciones proporcionadas para la evaluación.
        :return String con la evaluación de la comisión de Otras Especialidades Sanitarias.
        """
        return "En el resultado de la valoración para el criterio de la titularidad se podría obtener un resultado " + ("positivo" if evaluation.positive else "negativo") + " con los siguientes resultados: \n  Número de publicaciones necesarias " + str(evaluation.criterion.min_arts) + ". Obtenidas: " + str(len(scientific_production)) + ". \n Número de publicaciones necesarias en el tercil 1: " + str(evaluation.criterion.num_t1) + " Obtenidas: " + str(len(evaluation.arts_t1)) + " \n Número de publicaciones con autoría preferente " + str(evaluation.criterion.num_authorship) + " Obtenidas: " + str(len(evaluation.arts_authorship_t1)) + " Número de publicaciones con autoría preferente en tercil 1: " + str(evaluation.criterion.num_authorship_t1) + " Obtenidas: " + str(len(evaluation.arts_authorship_t1)) + ".\n\n"
