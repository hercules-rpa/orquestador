from model.process.Process2.Entities.Committee.Committee import Committee
from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.RO import RO

class CommitteeCienciasEconomicasYEmpresariales(Committee):
    """
    Comité encargado de la evaluación de solicitud de sexenios para la comisión de Biología celular y molecular.
    """
    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)
    
    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] scientific_production: listado de artículos de un investigador.
        :return SexenioEvaluation evaluación del sexenio.        
        """
        evaluation = SexenioEvaluation(scientific_production=scientific_production,
        parameters=self.get_criterion())
        clasification = evaluation.get_classification_production()

        if clasification:
            publications = []
            min_publications = evaluation.parameters['min_publicaciones']
            
            if len(clasification.publications_q1) >= min_publications:
                publications = clasification.publications_q1[0:min_publications]
            else:
                publications = clasification.publications_q1[0:]
                res = min_publications - len(publications)
                
                if len(clasification.publications_q2) >= res:
                        publications += clasification.publications_q2[0:res]
                elif len(clasification.publications_q2) >= 2:
                    publications += clasification.publications_q2[0:]
                    res = min_publications - len(publications)

                    if res > 0 and res <= evaluation.parameters['min_q1q2']:
                        if clasification.publications_q3:
                            if len(clasification.publications_q3) >= res:
                                publications += clasification.publications_q3[0:res]
                            else:
                                publications += clasification.publications_q3[0:]
                                res = min_publications - len(publications)
                        
                        if res > 0 and clasification.publications_q4:
                            if len(clasification.publications_q4) >= res:
                                publications += clasification.publications_q4[0:res]
                            else:
                                publications += clasification.publications_q4[0:]

            if len(publications) == min_publications:
                punctuation = 0
                for art in publications:
                    punctuation += self.get_punctuation_publication(art, evaluation.parameters['puntuaciones'])
                
                evaluation.punctuation = punctuation
                evaluation.main_production = publications
            
        return evaluation        

    def get_punctuation_publication(self, element:RO, punctuations:dict) -> int:
        """
        Método que calcula la puntuación que tiene un artículo en base al cuartil al que pertenece y al número de autores que tiene.
        :param RO artículo que se evaluará
        :param punctuations diccionario que nos proporciona las puntuaciones establecidas en la configuración
        :result int puntuación obtenida
        """
        punctuation = 0
        quartile = element.get_quartile()
        if quartile == 1:
            punctuation = punctuations['puntuacion_q1']
        elif quartile == 2:
            punctuation = punctuations['puntuacion_q2']
        elif quartile == 3:
            punctuation = punctuations['puntuacion_q3']
        elif quartile == 4:
            punctuation = punctuations['puntuacion_q4']
        return punctuation