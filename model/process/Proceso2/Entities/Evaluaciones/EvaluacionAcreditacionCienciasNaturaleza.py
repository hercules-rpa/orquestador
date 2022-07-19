from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion


class CriterioAcreditacionCienciasNaturaleza():
    """
    Criterio de evaluación de la acreditación de la comisión de Ciencias de la Naturaleza:

    num_articulos: número de artículos que tiene que tener el investigador.
    minimo_articulos: mínimo de artículos que tiene que tener el investigador
    num_t1: el número de artículos mínimo que deben estar en el primer tercil.
    min_t1: el número mínimo de artículos mínimo que deben estar en el primer tercil.
    num_t1_t2: el número de artículos que deben estar en el primer y segundo tercil.
    min_t1_t2: el número de artículos mínimo que deben estar en el primer y segundo tercil.
    num_autor: el número de publicaciones en las que tiene que ser autor principal el investigador.
    min_anios: el número máximo de años que tiene que tener una publicación para que sea válida.
    """
    def __init__(self, num_articulos: int, minimo_articulos: int, num_t1: int, min_t1: int, num_t1_t2: int, min_t1_t2: int, num_autor: int, min_anios: int):
        self.num_articulos = num_articulos
        self.minimo_articulos = minimo_articulos
        self.num_t1 = num_t1
        self.min_t1 = min_t1
        self.num_t1_t2 = num_t1_t2
        self.min_t1_t2 = min_t1_t2
        self.num_autor = num_autor
        self.min_anios = min_anios
        
class EvaluacionAcreditacionCienciasNaturaleza(EvaluacionAcreditacion):
    """
    Resultado de la evaluación de la comisión de Ciencias de la Naturaleza de una solicitud de acreditación
    """
    def __init__(self, produccion_cientifica:list = [], positiva:bool=False, acreditacion:Acreditacion=None, observaciones:str='', valoracion_alcanzada:str='', publicaciones_t1:list=[], publicaciones_t2:list=[], publicaciones_autor:list=[], criterio: CriterioAcreditacionCienciasNaturaleza=None):
        super().__init__(produccion_cientifica=produccion_cientifica, positiva = positiva, acreditacion=acreditacion, observacion=observaciones)
        self.publicaciones_t1 = publicaciones_t1
        self.publicaciones_t2 = publicaciones_t2
        self.publicaciones_autor = publicaciones_autor
        self.valoracion_alcanzada = valoracion_alcanzada
        self.criterio = criterio

    def get_publicaciones_t1(self):
        """
        Método para saber las publicaciones del tercil uno que van a la producción principal.
        """
        p_t1 = []
        if self.publicaciones_t1:
            for publicacion in self.publicaciones_t1:
                p_t1.append(publicacion)
                if len(p_t1) == self.criterio.num_t1:
                    return p_t1
        return p_t1

    def get_publicaciones_t2(self):
        """
        Método para saber las publicaciones del tercil dos que van a la producción principal.
        """
        p_t1 = self.get_publicaciones_t1()
        p_t2 = []
        if self.publicaciones_t2:
            for publicacion in self.publicaciones_t2:
                p_t2.append(publicacion)
                if len(p_t1) + len(p_t2) == self.criterio.num_t1_t2:
                    return p_t2
        return p_t2

    def get_publicaciones_autor(self):
        """
        Método para saber las publicaciones en las que el investigador es autor principal que van a la producción principal.
        """
        p_autor = []
        if self.publicaciones_autor:
            for publicacion in self.publicaciones_autor:
                p_autor.append(publicacion)
                if len(p_autor) == self.criterio.num_autor:
                    return p_autor
        return p_autor

    def get_produccion_sustitutoria(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        """
        produccion_sustitutoria = []
        if self.publicaciones_t1 or self.publicaciones_t2:
            p1 = self.get_publicaciones_t1()
            p2 = self.get_publicaciones_t2()
            for publicacion in self.produccion_cientifica:
                if publicacion not in p1 and publicacion not in p2:
                    produccion_sustitutoria.append(publicacion)
        return produccion_sustitutoria