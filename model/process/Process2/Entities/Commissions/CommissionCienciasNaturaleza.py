from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationCienciasNaturaleza import CriterionEvaluationCienciasNaturaleza, AccreditationEvaluationCienciasNaturaleza
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType

import datetime

class CommissionCienciasNaturaleza(Commission):
    """
    La comisión de Ciencias de la Naturaleza se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluator, is_commission: bool = True):
        super().__init__(id, evaluator, is_commission)
        
    def get_accreditation_evaluation(self, scientific_production: list, accreditation: Accreditation) -> AccreditationEvaluationCienciasNaturaleza:
        """
        Método encargado de evaluar la solicitud de acreditación de la comisión de Ciencias de la Naturaleza.

        :param [] produccion_cientifica: Lista con las publicaciones del investigador.
        :param Acreditacion acreditacion: Tipo de acreditación a la que está postulando el investigador.
        :return EvaluacionACreditacionCienciasNaturaleza Objeto con el resultado de la evaluación del investigador.
        """
        eval = AccreditationEvaluationCienciasNaturaleza(scientific_production=scientific_production, accreditation = accreditation)
        if accreditation.type == AccreditationType.CATEDRA:
            criteria = self.get_configuration_criterion(accreditation.type,'B')
            if criteria:
                eval.criterion = CriterionEvaluationCienciasNaturaleza(criteria['num_publicaciones'], criteria['min_publicaciones'], criteria['t1_publicaciones'], criteria['min_t1_publicaciones'], criteria['t1_t2publicaciones'], criteria['min_t1_t2publicaciones'], criteria['autoria_preferente'], criteria['max_anyo'])           
            return self.get_catedra(scientific_production, eval)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            criteria = self.get_configuration_criterion(accreditation.type,'B')
            if criteria:
                eval.criterion = CriterionEvaluationCienciasNaturaleza(criteria['num_publicaciones'], criteria['min_publicaciones'], criteria['t1_publicaciones'], criteria['min_t1_publicaciones'], criteria['t1_t2publicaciones'], criteria['min_t1_t2publicaciones'], criteria['autoria_preferente'], criteria['max_anyo'])
            return self.get_titularidad(scientific_production, eval)

    def get_catedra(self, scientific_production:list, evaluation:AccreditationEvaluationCienciasNaturaleza) -> AccreditationEvaluationCienciasNaturaleza:
        """
        Método encargado de evaluar la cátedra de la comisión de Ciencias de la Naturaleza.

        :param [] produccion_cientifica: Lista con las publicaciones del investigador.
        :param EvaluacionAccreditacionCienciasNaturaleza eval: Tipo de Evaluación a la que está postulando el investigador.
        :return EvaluacionAccreditacionCienciasNaturaleza Objeto con el resultado de la evaluación del investigador.
        """
        eval, publications_t1, publications_t2, publication_author = self.get_criterio_catedra(scientific_production, evaluation.criterion.num_arts, evaluation.criterion.min_arts, evaluation.criterion.num_t1, evaluation.criterion.min_t1, evaluation.criterion.num_t1_t2, evaluation.criterion.min_t1_t2, evaluation.criterion.num_authors, evaluation.criterion.min_years)
        if eval:
            evaluation.positive = eval
            evaluation.publications_t1 = publications_t1
            evaluation.publications_t2 = publications_t2
            evaluation.publications_author = publication_author
        evaluation.observation += self.observation_catedra(evaluation)
        return evaluation

    def get_titularidad(self, scientific_production:list, evaluation:AccreditationEvaluationCienciasNaturaleza) -> AccreditationEvaluationCienciasNaturaleza:
        """
        Método encargado de evaluar la titularidad de la comisión de Ciencias de la Naturaleza.

        :param [] produccion_cientifica: Lista con las publicaciones del investigador.
        :param EvaluacionAccreditacionCienciasNaturaleza eval: Tipo de Evaluación a la que está postulando el investigador.
        :return EvaluacionAccreditacionCienciasNaturaleza Objeto con el resultado de la evaluación del investigador.
        """
        eval, publications_t1, publications_t2, publications_author = self.criterio_titularidad(scientific_production, evaluation.criterion.num_arts, evaluation.criterion.min_arts, evaluation.criterion.num_t1, evaluation.criterion.min_t1, evaluation.criterion.num_t1_t2, evaluation.criterion.min_t1_t2, evaluation.criterion.num_authors, evaluation.criterion.min_years)
        if eval:
            evaluation.positive = eval
            evaluation.publications_t1 = publications_t1
            evaluation.publications_t2 = publications_t2
            evaluation.publications_author = publications_author
        evaluation.observation += self.observacion_titularidad(evaluation)
        return evaluation

    def get_criterio_catedra(self, scientific_production: list, num_publications: int, 
    min_publications: int, num_t1: int, min_t1: int, num_t1_t2: int, min_t1_t2: int, 
    author: int, max_years: int) -> tuple([bool, [], [], []]):
        """
        Método que define el criterio de una cátedra para la comisón de Ciencias de la Naturaleza.

        :param [] produccion_cientifica: Listado de publicaciones de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1: Número de publicaciones de tercil 1 mínimas necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones de tercil 1 y 2 mínimas necesarias para cumplir el criterio.
        :param int max_anios: Años máximos permitidos por publicación.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones tanto de tercil 1 como de tercil 2.
        """
        result = False
        publications_t1 = []
        publications_t2 = []
        publications_author = []
        if len(scientific_production) >= min_publications:
            for publication in scientific_production:
                if publication.get_tertile() == 1 and (datetime.date.today().year - int(publication.get_year())) >= max_years:
                    if publication.author_position == 1:
                        publications_author.append(publication)
                    publications_t1.append(publication)
                elif publication.get_tertile() == 2 and (datetime.date.today().year - int(publication.get_year())) >= max_years:
                    if publication.author_position == 1:
                        publications_author.append(publication)
                    publications_t2.append(publication)
            if publications_t1 and publications_t2 and (len(publications_t1) + len(publications_t2)) >= num_publications and (len(publications_t1) + len(publications_t2)) >= num_t1_t2 or len(publications_t1) >= num_t1 :
                result = True
                return result, publications_t1, publications_t2, publications_author
            elif publications_t1 and publications_t2 and (len(publications_t1) + len(publications_t2)) >= min_publications and len(publications_author) >= author and ((len(publications_t1) + len(publications_t2)) >= min_t1_t2 or len(publications_t1) >= min_t1):
                result = True
                return result, publications_t1, publications_t2, publications_author
        return result, publications_t1, publications_t2, publications_author

    def criterio_titularidad(self, scientific_production: list, num_publications: int, 
    min_publications: int, num_t1: int, min_t1: int, num_t1_t2: int, min_t1_t2: int, 
    author: int, max_years: int) -> tuple([bool, [], [], []]):
        """
        Método que define el criterio de una titularidad para la comisón de Ciencias de la Naturaleza.

        :param [] scientific_production: Listado de publicaciones de un investigador.
        :param int num_publications: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1: Número de publicaciones de tercil 1 mínimas necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones de tercil 1 y 2 mínimas necesarias para cumplir el criterio.
        :param int max_years: Años máximos permitidos por publicación.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones tanto de tercil 1 como de tercil 2.
        """
        result = False
        publications_t1 = []
        publications_t2 = []
        publications_author = []
        if len(scientific_production) >= min_publications:
            for publication in scientific_production:
                if publication.get_tertile() == 1 and (datetime.date.today().year - int(publication.get_year())) >= max_years:
                    if publication.author_position == 1:
                        publications_author.append(publication)
                    publications_t1.append(publication)
                elif publication.get_tertile() == 2 and (datetime.date.today().year - int(publication.get_year())) >= max_years:
                    if publication.author_position == 1:
                        publications_author.append(publication)
                    publications_t2.append(publication)
            if publications_t1 and publications_t2 and (len(publications_t1) + len(publications_t2)) >= num_publications and len(publications_author) >= author and (len(publications_t1) + len(publications_t2)) >= num_t1_t2 or len(publications_t1) >= num_t1:
                result = True
                return result, publications_t1, publications_t2, publications_author
            elif publications_t1 and publications_t2 and (len(publications_t1) + len(publications_t2)) >= min_publications and len(publications_author) >= author and ((len(publications_t1) + len(publications_t2)) >= min_t1_t2 or len(publications_t1) >= min_t1):
                result = True
                return result, publications_t1, publications_t2, publications_author
        return result, publications_t1, publications_t2, publications_author

    def observation_catedra(self, evaluation: AccreditationEvaluationCienciasNaturaleza) -> str:
        """
        Método que completa el atributo observación del criterio de la cátedra para la comisión Ciencias de la Naturaleza.

        :param EvaluacionAcreditacionCienciasNaturaleza evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la cátedra.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la cátedra para la comisión de Ciencias de la Naturaleza podría ser ' +  ("positivo" if evaluation.positive else "negativo") + '.\n Se han obtenido ' + str(len(evaluation.publications_t1)) + ' publicaciones de nivel 1 y ' + str(len(evaluation.publications_t2)) + ' publicaciones de nivel 2.\n\n'


    def observacion_titularidad(self, evaluation: AccreditationEvaluationCienciasNaturaleza) -> str:
        """
        Método que completa el atributo observación del criterio de la titularidad para la comisión Ciencias de la Naturaleza.

        :param EvaluacionAcreditacionCienciasNaturaleza evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la titularidad.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la cátedra para la comisión de Ciencias de la Naturaleza podría ser ' +  ("positivo" if evaluation.positive else "negativo") + '.\n Se han obtenido ' + str(len(evaluation.publications_t1)) + ' publicaciones de nivel 1 y ' + str(len(evaluation.publications_t2)) + ' publicaciones de nivel 2.\n\n'