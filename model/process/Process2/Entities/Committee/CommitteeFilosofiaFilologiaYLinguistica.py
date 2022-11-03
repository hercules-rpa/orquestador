from model.process.Process2.Entities.RO import RO
from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.Committee.Committee import Committee


class CommitteeFilosofiaFilologiaYLinguistica(Committee):
    """
    Comité que evalúa las solicitudes de sexenios del área Filosofía, Filología y Lingüistica. (11)
    """
    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    def get_punctuation_article(self, element:RO, punctuations:dict) -> int:
        """
        Método que obtiene la puntuación de un artículo.
        :param RO elemento a analizar para obtener su puntuación
        :param punctuations diccionario con las puntuaciones
        :return puntuación obtenida
        """
        punctuation = 0
        if element.quartile:
            if element.get_quartile() == 4:
                punctuation = punctuations['puntuacion_q4_publicaciones']
            else:
                punctuation = punctuations['puntuacion_q1q2q3_publicaciones']
        return punctuation

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] scientific_production: listado de artículos de un investigador.
        :return SexenioEvaluation evaluación del sexenio.        
        """
        eval = SexenioEvaluation(scientific_production=scientific_production,
        parameters=self.get_criterion())
        
        if len(scientific_production) >= eval.parameters['min_publicaciones']:
            eval.main_production = scientific_production[0:eval.parameters['min_publicaciones']]
        else: 
            eval.main_production = scientific_production[0:]

        eval.observation = 'En los requisitos que se han evaluado no se indican el número de artículos mínimo, por esto, se ha indicado como producción científica ' + \
            'principal los primeros artículos obtenidos. \n'

        if eval.main_production:
            puntuaciones = eval.parameters['puntuaciones']
            for elem in eval.main_production:
                eval.punctuation += self.get_punctuation_article(elem, puntuaciones)
        return eval