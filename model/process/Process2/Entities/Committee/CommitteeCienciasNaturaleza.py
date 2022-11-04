from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation
from model.process.Process2.Entities.Committee.Committee import Committee
"""
Comité que se encarga de la evaluación de la solicitud de sexenios del área de 
Ciencias de la Naturaleza - id(4).
"""
class CommitteeCienciasNaturaleza(Committee):
    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    def get_main_production(self, articles:list, num:int) -> tuple([int, list]):        
        """
        Método encargado de la obtención de la producción principal con mejor baremo para 
        la solicitud del sexenio.
        :param [] articles: lista cuyos elementos son listas clasificadas por los criterios del sexenio.
        :param int num: número de artículos que se necesita como producción principal.
        :return tupla [int, list] que devuelve la puntuación total y la lista de artículos seleccionados.
        """
        num_falt = num
        main_production = []
        punctation = 0
        if articles:
            for article in articles:
                if num_falt != 0:
                    results = []
                    if len(article) >= num_falt:
                        results = article[0:(num_falt+1)]
                    else:
                        results = article[0:]

                    if results:
                        for tupl in results:
                            main_production.append(tupl[0])               
                            punctation += tupl[1]
                        num_falt -= len(results)
                else:
                    break    
        return (punctation, main_production)

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] scientific_production: listado de artículos de un investigador.
        :return SexenioEvaluation evaluación del sexenio.        
        """
        evaluation:SexenioEvaluation = SexenioEvaluation(scientific_production=scientific_production,
        parameters=self.get_criterion())
        if scientific_production:
            art_decil = []
            art_q1 = []
            art_q2 = []
            art_q3 = []
            art_q4 = []
            
            punctuations = evaluation.parameters['puntuaciones']

            for element in scientific_production:
                quartile = element.get_quartile()
                if element.get_decile() == 1:
                    art_decil.append((element, punctuations['puntuacion_d1']))
                elif element.quartile == 1:
                    art_q1.append((element, punctuations['puntuacion_q1']))
                elif element.quartile == 2:
                    art_q2.append((element, punctuations['puntuacion_q2']))
                elif element.quartile == 3:
                    art_q3.append((element, punctuations['puntuacion_q3']))
                elif element.quartile == 4:
                    art_q4.append((element, punctuations['puntuacion_q4'])) 

            collection_articles = [art_decil, art_q1, art_q2, art_q3, art_q4]
            tupla = self.get_main_production(collection_articles, evaluation.parameters['min_publicaciones'])
            if tupla:
                evaluation.punctuation = tupla[0]
                evaluation.main_production = tupla[1]        
                    
        return evaluation



            
                

                
                

                

            


