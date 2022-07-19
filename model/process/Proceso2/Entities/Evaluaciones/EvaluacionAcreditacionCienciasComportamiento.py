from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion

class CriterioAcreditacionCienciasComportamiento():
    """
    Criterio de evaluación de la acreditación de la comisión de Ciencias del Comportamiento:

    num_articulos: número de artículos necesarios que tiene que tener el investigador.
    minimo_articulos: mínimo de artículos que tiene que tener el investigador.
    num_t1_t2: el número de artículos que deben estar en el primer y segundo tercil.
    min_t1_t2: el número de artículos mínimo que deben estar en el primer y segundo tercil.
    num_autoria: el número de autorías que tiene que tener el investigador.
    min_autoria: el número mínimo de autorías que tiene que tener un investigador.
    min_porcentaje: número mínimo de porcentaje que tiene que tener para cumplir el criterio.
    """
    def __init__(self, num_articulos: int, minimo_articulos: int, num_t1_t2: int, min_t1_t2: int, num_autoria: int, min_autoria: int, porcentaje: int):
        self.num_articulos = num_articulos
        self.minimo_articulos = minimo_articulos
        self.num_t1_t2 = num_t1_t2
        self.min_t1_t2 = min_t1_t2
        self.num_autoria = num_autoria
        self.min_autoria = min_autoria
        self.min_porcentaje = porcentaje

class EvaluacionAcreditacionCienciasComportamiento(EvaluacionAcreditacion):
    """
    Resultado de la evaluación de la comisión de Ciencias del Comportamiento de una solicitud de acreditación
    """
    def __init__(self, produccion_cientifica:list = [], positiva:bool=False, acreditacion:Acreditacion=None, observaciones:str='', publicaciones_autoria:list=[], publicaciones_t1_t2:list=[], criterio: CriterioAcreditacionCienciasComportamiento=None):
        super().__init__(produccion_cientifica=produccion_cientifica, positiva = positiva, acreditacion=acreditacion, observacion=observaciones)
        self.publicaciones_autoria = publicaciones_autoria
        self.publicaciones_t1_t2 = publicaciones_t1_t2
        self.criterio = criterio

    def get_publicaciones_t1_t2(self):
        """
        Método para obtener las publicaciones del tercil primero y segundo para la producción principal.
        """
        p_t1_t2 = []
        if self.publicaciones_t1_t2:
            for publicacion in self.publicaciones_t1_t2:
                if publicacion.get_tercil() == 1 or publicacion.get_tercil() == 2:
                    p_t1_t2.append(publicacion)
                    if len(p_t1_t2) == self.criterio.min_t1_t2:
                        return p_t1_t2
        return p_t1_t2

    def get_publicaciones_autoria(self):
        """
        Método para obtener las publicaciones que cumplan el criterio de autoría.
        """
        p_autoria = []
        if self.publicaciones_autoria:
            for publicacion in self.publicaciones_autoria:
                p_autoria.append(publicacion)
                if publicacion == self.criterio.num_autoria:
                    return p_autoria
        return p_autoria

    def get_produccion_sustitutoria(self):
        """
        Método para obtener la producción sustitutoria.
        """
        p_sustitutoria = []
        p_t1_t2 = self.get_publicaciones_t1_t2()
        p_autoria = self.get_publicaciones_autoria()
        if self.produccion_cientifica:
            for publicacion in self.produccion_cientifica:
                if publicacion not in p_t1_t2 and publicacion not in p_autoria:
                    p_sustitutoria.append(publicacion)
        return p_sustitutoria