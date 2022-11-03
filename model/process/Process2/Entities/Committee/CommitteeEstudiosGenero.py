from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.Committee.CommitteeCienciasSociales import CommitteeCienciasSociales

class CommitteeEstudiosGenero(CommitteeCienciasSociales):
    """
    Comité que evalúa el área de Estudios de Género dentro del comité 7.1.
    """
    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        evaluation = SexenioEvaluation(scientific_production=scientific_production, parameters=self.get_criterion('estudiosgenero'))
        clasification = evaluation.get_classification_production()

        if clasification:
            min_publications = evaluation.parameters['min_publicaciones']
            if clasification.publications_q1:
                if len(clasification.publications_q1) >= min_publications:
                    evaluation.main_production = clasification.publications_q1[0:4]
                else:
                    evaluation.main_production = clasification.publications_q1[0:]
                    rest = min_publications-len(evaluation.main_production)
                    
                    if clasification.publications_q2:
                        if len(clasification.publications_q2) >= rest:
                            evaluation.main_production += clasification.publications_q2[0:rest]
                        
                        else:
                            evaluation.main_production += clasification.publications_q2[0:]
                            rest = min_publications-len(evaluation.main_production)

                    if rest == 1:
                        if clasification.publications_q3:
                            evaluation.main_production.append(clasification.publications_q3[0])
                        elif clasification.publications_q4:
                            evaluation.main_production.append(clasification.publications_q4[0])
                                                
                    if len(evaluation.main_production) >= min_publications:
                        for art in evaluation.main_production:
                            evaluation.punctuation += self.get_punctuation_article(art, evaluation.parameters)

        return evaluation