from model.process.Process2.Entities.Evaluations.Evaluation import Evaluation

"""
Clase que almacena el resultado de la clasificación de una producción científica en cuartiles.
"""
class ClassificationInfo():
    def __init__(self, publications_q1:list=[], publications_q2:list=[], 
        publications_q3:list=[], publications_q4:list=[], publications_d1:list=[]):
        self.publications_q1 = publications_q1
        self.publications_q2 = publications_q2
        self.publications_q3 = publications_q3
        self.publications_q4 = publications_q4
        self.publications_d1 = publications_d1

class SexenioEvaluation(Evaluation):
    """
    Entidad que representa la evaluación que realiza un comité sobre una solicitud de sexenio.
    """
    def __init__(self, scientific_production: list = [], observation: str = '', 
        punctuation: int = 0, main_production:list=[], parameters:dict=None):
        super().__init__(scientific_production, observation)
        self.punctuation = punctuation        
        """
        Producción que se incluirá en el informe de sexenio como principal, está lista representa
        los artículos con mayor puntuación.
        """
        self.main_production = main_production
        self.parameters = parameters

    def get_substitute_production(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        :return list retorna una lista con la producción sustitutoria
        """
        result = None
        if self.scientific_production and self.main_production:
            result = self.scientific_production
            for art in self.main_production:
                if art in result:
                    result.remove(art)
        return result

    def get_classification_production(self) -> ClassificationInfo:
        """
        Método que clasifica las publicaciones dependiendo del cuartil al que pertenezcan.
        :return ClassificationInfo, clase que devuelve la clasificación.
        """
        result: ClassificationInfo = ClassificationInfo()
        if self.scientific_production:
            for pc in self.scientific_production:
                quartile = pc.get_quartile()
                if quartile == 1:
                    result.publications_q1.append(pc)
                elif quartile == 2:
                    result.publications_q2.append(pc)
                elif quartile == 3:
                    result.publications_q3.append(pc)
                elif quartile == 4:
                    result.publications_q4.append(pc)
                
                if pc.get_decile() == 1:
                    result.publications_d1.append(pc)

        return result
                    
        
        