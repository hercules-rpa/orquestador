from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationCienciasComportamiento import CriterionEvaluationCienciasComportamiento, AccreditationEvaluationCienciasComportamiento
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType

class CommissionCienciasComportamiento(Commission):
    """
    La comisión de Ciencias de la Naturaleza se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluator, is_commission: bool = True):
        super().__init__(id, evaluator, is_commission)
        
    def get_accreditation_evaluation(self, scientific_production: list, accreditation: Accreditation) -> AccreditationEvaluationCienciasComportamiento:
        """
        Método encargado de evaluar la solicitud de acreditación de la comisión de Ciencias del Comportamiento.

        :param [] scientific_production: Lista con las publicaciones del investigador.
        :param Accreditation accreditation: Tipo de acreditación a la que está postulando el investigador.
        :return AccreditationEvaluationCienciasComportamiento Objeto con el resultado de la evaluación del investigador.
        """
        eval = AccreditationEvaluationCienciasComportamiento(scientific_production=scientific_production, accreditation = accreditation)
        if accreditation.type == AccreditationType.CATEDRA:
            criterion = self.get_configuration_criterion(accreditation.type)
            if criterion:
                eval.criterion = CriterionEvaluationCienciasComportamiento(criterion['B']['min_publicaciones'],criterion['B2']['min_publicaciones'],criterion['B']['q1q2_articulos'],criterion['B2']['q1q2_articulos'],criterion['B']['q1q2_ap_articulos'],criterion['B2']['q1q2_ap_articulos'],criterion['min_porcentaje'])    
            return self.get_catedra(scientific_production, eval)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            criterion = self.get_configuration_criterion(accreditation.type)
            if criterion:
                eval.criterion = CriterionEvaluationCienciasComportamiento(criterion['B']['min_publicaciones'],criterion['B2']['min_publicaciones'],criterion['B']['q1q2_articulos'],criterion['B2']['q1q2_articulos'],criterion['B']['q1q2_ap_articulos'],criterion['B2']['q1q2_ap_articulos'],criterion['min_porcentaje'])
            return self.get_titularidad(scientific_production, eval)

    def get_catedra(self, scientific_production:list, eval:AccreditationEvaluationCienciasComportamiento) -> AccreditationEvaluationCienciasComportamiento:
        """
        Método encargado de evaluar la cátedra de la comisión de Ciencias del Comportamiento.

        :param [] scientific_production: Lista con las publicaciones del investigador.
        :param EvaluacionAcreditacionCienciasComportamiento eval: Tipo de Evaluación a la que está postulando el investigador.
        :return EvaluacionAcreditacionCienciasComportamiento Objeto con el resultado de la evaluación del investigador.
        """
        result, publications_t1_t2, publications_authorship = self.criterion_catedra(scientific_production, eval.criterion.num_art, eval.criterion.num_t1_t2, eval.criterion.num_authorship, eval.criterion.min_percent)
        if result:
            eval.positive = result
            eval.publications_t1_t2 = publications_t1_t2
            eval.publications_authorship = publications_authorship
            eval.observation += self.observation_catedra(eval)
        return eval

    def get_titularidad(self, scientific_production:list, eval:AccreditationEvaluationCienciasComportamiento) -> AccreditationEvaluationCienciasComportamiento:
        """
        Método encargado de evaluar la titularidad de la comisión de Ciencias del Comportamiento.

        :param [] scientific_production: Lista con las publicaciones del investigador.
        :param AccreditationEvaluationCienciasComportamiento eval: Tipo de Evaluación a la que está postulando el investigador.
        :return AccreditationEvaluationCienciasComportamiento Objeto con el resultado de la evaluación del investigador.
        """
        result, publications_t1_t2, publications_authorship  = self.criterion_titularidad(scientific_production,  eval.criterion.num_art, eval.criterion.num_t1_t2, eval.criterion.num_authorship, eval.criterion.min_percent)
        if eval:
            eval.positive = result
            eval.publications_t1_t2 = publications_t1_t2
            eval.publications_authorship = publications_authorship
        eval.observation += self.observation_titularidad(eval)
        return eval

    def criterion_catedra(self, scientific_production: list, num_publications: int, 
    num_t1_t2: int, num_authorship: int, percent: int) -> tuple([bool, [], []]):
        """
        Método que define el criterio de una cátedra para la comisón de Ciencias del Comportamiento.

        :param [] scientific_production: Listado de publicaciones de un investigador.
        :param int num_publications: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones de tercil 1 y 2 mínimas necesarias para cumplir el criterio.
        :param int percent: Número de porcentaje válido para cumplir los méritos.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones tanto de tercil 1 como de tercil 2.
        """
        result = False
        publications_t1 = []
        publications_t2 = []
        publications_authorship = []
        if len(scientific_production) >= num_publications:
            for publication in scientific_production:
                if publication.get_tertile() == 1:
                    publications_t1.append(publication)
                elif publication.get_tertile() == 2:
                    publications_t2.append(publication)
                elif publication.author_position == 1:
                    publications_authorship.append(publication)
            if (publications_t1 and publications_t2 and (len(publications_t1) + len(publications_t2)) >= num_t1_t2 and len(publications_authorship) >= num_authorship) or (publications_t1 and publications_t2 and len(publications_authorship) >= num_authorship*(percent/100) and (len(publications_t1) + len(publications_t2))*(percent/100) >= num_t1_t2*(percent)/100):
                result = True
                return result, publications_t1 + publications_t2, publications_authorship
        return result, publications_t1 + publications_t2, publications_authorship

    def criterion_titularidad(self, scientific_production: list, num_publications: int, 
    num_t1_t2: int, num_authorship: int, percent: int) -> tuple([bool, [], []]):
        """
        Método que define el criterio de una titularidad para la comisón de Ciencias del Comportamiento.

        :param [] scientific_production: Listado de publicaciones de un investigador.
        :param int num_publications: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1: Número de publicaciones de tercil 1 mínimas necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones de tercil 1 y 2 mínimas necesarias para cumplir el criterio.
        :param int max_year: Años máximos permitidos por publicación.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones tanto de tercil 1 como de tercil 2.
        """
        result = False
        publications_t1 = []
        publications_t2 = []
        publications_authorship = []
        if len(scientific_production) >= num_publications:
            for publicacion in scientific_production:
                if publicacion.get_tertile() == 1:
                    publications_t1.append(publicacion)
                elif publicacion.get_tertile() == 2:
                    publications_t2.append(publicacion)
                elif publicacion.author_position == 1:
                    publications_authorship.append(publicacion)
            if (publications_t1 and publications_t2 and (len(publications_t1) + len(publications_t2)) >= num_t1_t2 and len(publications_authorship) >= num_authorship) or (publications_t1 and publications_t2 and len(publications_authorship) >= num_authorship*(percent/100) and (len(publications_t1) + len(publications_t2))*(percent/100) >= num_t1_t2*(percent/100)):
                result = True
                return result, publications_t1 + publications_t2, publications_authorship
        return result, publications_t1 + publications_t2, publications_authorship

    def observation_catedra(self, eval: AccreditationEvaluationCienciasComportamiento) -> str:
        """
        Método que completa el atributo observación del criterio de la cátedra para la comisión Ciencias del Comportamiento.

        :param AccreditationEvaluationCienciasComportamiento eval: Objeto AccreditationEvaluation con la información necesaria de la evaluación del criterio de la cátedra.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la cátedra para la comisión de Ciencias del Comportamiento ha resultado ' +  ("positivo" if eval.positive else "negativo") + '.\n Se han obtenido ' + str(len(eval.publications_t1_t2)) + ' publicaciones de nivel 1 y publicaciones de nivel 2.\n\n'

    def observation_titularidad(self, eval: AccreditationEvaluationCienciasComportamiento) -> str:
        """
        Método que completa el atributo observación del criterio de la titularidad para la comisión Ciencias del Comportamiento.

        :param EvaluacionAcreditacionCienciasComportamiento evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la titularidad.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la cátedra para la comisión de Ciencias del Comportamiento ha resultado ' +  ("positivo" if eval.positive else "negativo") + '.\n Se han obtenido ' + str(len(eval.publications_t1_t2)) + ' publicaciones de nivel 1 y publicaciones de nivel 2.\n\n'
