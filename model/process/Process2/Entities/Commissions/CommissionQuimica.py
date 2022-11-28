from model.process.Process2.Entities.RO import RO
from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationQuimica import CriterionEvaluationQuimica, AccreditationEvaluationQuimica
import datetime
# comisión 3

class CommissionQuimica(Commission):
    """
    La comisión de Química se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluator, is_commission: bool = True):
        super().__init__(id, evaluator, is_commission)

    def get_accreditation_evaluation(self, scientific_production, accreditation: Accreditation) -> AccreditationEvaluationQuimica:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] scientific_production: listado de artículos de un investigador.
        :param accreditation acreditación que se está solicitando.
        :return El objeto EvaluacionAcreditación que contiene la evaluación de la acreditación solicitada.
        """
        evaluation = AccreditationEvaluationQuimica(scientific_production=scientific_production, accreditation=accreditation)
        if accreditation.type == AccreditationType.CATEDRA:
            criteria = self.get_configuration_criterion(accreditation.type, evaluation)
            if criteria:
                evaluation.criterion = CriterionEvaluationQuimica(criteria['min_publicaciones'],criteria['t1_publicaciones'], criteria['t1_ap_publicaciones'], criteria['max_anyo'])
            return self.get_catedra(scientific_production, evaluation=evaluation)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            criteria = self.get_configuration_criterion(accreditation.type, evaluation)
            if criteria:
                evaluation.criterion = CriterionEvaluationQuimica(criteria['min_publicaciones'],criteria['t1_publicaciones'], criteria['t1_ap_publicaciones'], criteria['max_anyo'])
            return self.get_titularidad(scientific_production, evaluation)

    def get_catedra(self, scientific_production, evaluation: AccreditationEvaluationQuimica) -> AccreditationEvaluationQuimica:
        """
        Método general de evaluación para la cátedra de un investigador.

        :param [] scientific_production: listado de artículos de un investigador.
        :param AccreditationEvaluationQuimica evaluation: Objeto que contiene el resultado del criterio de la comisión de Química.
        :return objeto AccreditationEvaluationQuimica con los resultados del criterio de la comisión de Química.
        """
        eval, arts_t1, arts_first_author = self.evaluate_criterion(scientific_production, evaluation.criterion.min_publications, evaluation.criterion.t1_publications, evaluation.criterion.t1_ap_publications, evaluation.criterion.max_year)
        evaluation.positive = eval
        evaluation.art_t1 = arts_t1
        evaluation.art_first_author = arts_first_author
        evaluation.observation += self.create_observaciones_critero(evaluation)
        return evaluation

    def get_titularidad(self, scientific_production, evaluacion: AccreditationEvaluationQuimica) -> AccreditationEvaluationQuimica:
        """
        Método general de evaluación para la titularidad de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionQuimica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Química.
        :return objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Química.
        """
        eval, arts_t1, arts_first_author = self.evaluate_criterion(scientific_production, evaluacion.criterion.min_publications, evaluacion.criterion.t1_publications, evaluacion.criterion.t1_ap_publications, evaluacion.criterion.max_year)
        evaluacion.positive = eval
        evaluacion.art_t1 = arts_t1
        evaluacion.art_first_author = arts_first_author
        evaluacion.observation += self.create_observaciones_critero(evaluacion)
        return evaluacion

    def evaluate_criterion(self, scientific_production, num_publications, t1_publicaciones, number_first_author, max_anios) -> tuple([bool, [],  []]):
        """
        Método para comprobar cuántos artículos pertenecen al T1 y si cumple con el mínimo establecido de artículos.

        :param [] scientific_production: listado de artículos de un investigador.
        :param int num_publicaciones: número de publicaciones necesarias para cumplir el criterio.
        :param int t1_publicaciones: número de publicaciones necesarias en el tercil 1.
        :param int number_first_author: número de publicaciones en las que tienes que ser primer autor.
        :param int max_anios: número máximo de años permitidos en las publicaciones.
        :return dupla formada por un booleano si se cumple con el criterio, una lista de artículos seleccionados en el tercil 1 y una lista de artículos en los que el investigador es primer autor.
        """
        arts_t1 = []
        arts_first_author = []
        result = False
        
        if len(scientific_production) >= num_publications:
            for art in scientific_production:
                articulo:RO = art
                # Ponemos el atributo posición pero no sé realmente si ese determina la posición en el artículo que estamos consultando.
                if articulo.get_tertile() == 1 and (datetime.date.today().year - int(articulo.get_year())) <= max_anios and articulo.author_position == 1:
                    arts_first_author.append(articulo)
                
                if articulo.get_tertile() == 1 and (datetime.date.today().year - int(articulo.get_year())) <= max_anios:
                    arts_t1.append(articulo)

            if arts_t1 and arts_first_author and len(arts_t1) >= num_publications and len(arts_t1) >= t1_publicaciones and len(arts_first_author) >= number_first_author:
                result = True

        return (result, arts_t1, arts_first_author)

    def create_observaciones_critero(self, evaluation:AccreditationEvaluationQuimica) -> str:
        """
        Método para rellenar el campo observaciones con el resultado de la evaluación del criterio.

        :param EvaluacionAcreditacionQuimica evaluacion: Objeto EvaluacionAcreditacion de Química donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :param int t1_publicaciones: Número de publicaciones necesarias en el tercil 1 para el criterio.
        :param int primer_autor: Número por el cual el investigador debe ser primer autor en la publicación del artículo.
        :param int max_anios: Número máximo de años que debe tener la publicacion del artículo.
        :return String con la evaluación de la comisión de Física
        """
        return 'En el resultado de la evaluación se podría obtener un resultado ' + \
         ("positivo" if evaluation.positive else "negativo") + '. \n Los resultados del criterio han sido los siguientes: \n' + 'Número de publicaciones totales necesarias: ' + str(evaluation.criterion.min_publications) + \
        '. Obtenidas: ' + str(len(evaluation.scientific_production)) + '.\n Número de publicaciones en el tercil 1 en los últimos ' + str(evaluation.criterion.max_year) + ' años: ' + str(evaluation.criterion.t1_publications) + '. Obtenidos: ' + str(len(evaluation.art_t1)) + ', de los cuales se necesita ser primer autor en ' + str(evaluation.criterion.t1_ap_publications) + ' de ellos, obtenidos: ' + str(len(evaluation.art_first_author)) + '. \n\n'