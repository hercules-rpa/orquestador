from model.process.Process2.Entities.Accreditation import Accreditation
from model.process.Process2.Entities.Evaluations.AccreditationEvaluation import AccreditationEvaluation

class CriterionEvaluationCienciasNaturaleza():
    """
    Criterio de evaluación de la acreditación de la comisión de Ciencias de la Naturaleza:

    num_arts: número de artículos que tiene que tener el investigador.
    min_arts: mínimo de artículos que tiene que tener el investigador
    num_t1: el número de artículos mínimo que deben estar en el primer tercil.
    min_t1: el número mínimo de artículos mínimo que deben estar en el primer tercil.
    num_t1_t2: el número de artículos que deben estar en el primer y segundo tercil.
    min_t1_t2: el número de artículos mínimo que deben estar en el primer y segundo tercil.
    num_authors: el número de publicaciones en las que tiene que ser autor principal el investigador.
    min_years: el número máximo de años que tiene que tener una publicación para que sea válida.
    """
    def __init__(self, num_arts: int, minimo_arts: int, num_t1: int, min_t1: int, 
    num_t1_t2: int, min_t1_t2: int, num_authors: int, min_years: int):
        self.num_arts = num_arts
        self.min_arts = minimo_arts
        self.num_t1 = num_t1
        self.min_t1 = min_t1
        self.num_t1_t2 = num_t1_t2
        self.min_t1_t2 = min_t1_t2
        self.num_authors = num_authors
        self.min_years = min_years
        
class AccreditationEvaluationCienciasNaturaleza(AccreditationEvaluation):
    """
    Resultado de la evaluación de la comisión de Ciencias de la Naturaleza de una solicitud de acreditación
    """
    def __init__(self, scientific_production:list = [], positive:bool=False, 
    accreditation:Accreditation=None, observation:str='', assessment:str='', 
    publications_t1:list=[], publications_t2:list=[], publications_author:list=[], 
    criterion: CriterionEvaluationCienciasNaturaleza=None):
        super().__init__(scientific_production=scientific_production, positive = positive, accreditation=accreditation, observation=observation)
        self.publications_t1 = publications_t1
        self.publications_t2 = publications_t2
        self.publications_author = publications_author
        self.assessment = assessment
        self.criterion = criterion

    def get_publications_t1(self):
        """
        Método para saber las publicaciones del tercil uno que van a la producción principal.
        :return list lista de publicaciones en el primer tercil
        """
        p_t1 = []
        if self.publications_t1:
            for publicacion in self.publications_t1:
                p_t1.append(publicacion)
                if len(p_t1) == self.criterion.num_t1:
                    return p_t1
        return p_t1

    def get_publications_t2(self):
        """
        Método para saber las publicaciones del tercil dos que van a la producción principal.
        :return list lista de publicaciones en el segundo tercil
        """
        p_t1 = self.get_publications_t1()
        p_t2 = []
        if self.publications_t2:
            for publication in self.publications_t2:
                p_t2.append(publication)
                if len(p_t1) + len(p_t2) == self.criterion.num_t1_t2:
                    return p_t2
        return p_t2

    def get_publications_author(self):
        """
        Método para saber las publicaciones en las que el investigador es autor principal que van a la producción principal.
        :return list lista de publicaciones 
        """
        p_autor = []
        if self.publications_author:
            for publication in self.publications_author:
                p_autor.append(publication)
                if len(p_autor) == self.criterion.num_authors:
                    return p_autor
        return p_autor

    def get_substitute_production(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        :return list lista de producción sustitutoria
        """
        result = []
        if self.publications_t1 or self.publications_t2:
            p1 = self.get_publications_t1()
            p2 = self.get_publications_t2()
            for publicacion in self.scientific_production:
                if publicacion not in p1 and publicacion not in p2:
                    result.append(publicacion)
        return result