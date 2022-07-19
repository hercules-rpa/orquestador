from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion

class CriterioEvaluacionQuimica():
    """
    Criterio de evaluación de la acreditación de la comisión de Física:

    min_publicaciones: Número mínimo de publicaciones.
    t1_publicaciones: el número de artículos mínimo que deben estar en el primer tercil.
    t1_ap_publicaciones: el número de artículos mínimo como primer autor.
    max_anyo: el número de años mínimos para seleccionar los autores.
    """
    def __init__(self, min_publicaciones:int, t1_publicaciones:int, t1_ap_publicaciones:int, max_anyo:int):
        self.min_publicaciones = min_publicaciones
        self.t1_publicaciones = t1_publicaciones
        self.t1_ap_publicaciones = t1_ap_publicaciones
        self.max_anyo = max_anyo

class EvaluacionAcreditacionQuimica(EvaluacionAcreditacion):
    """
    Resultado de la comisión de Química para una solicitud de acreditación.
    """
    def __init__(self, produccion_cientifica: list = [], positiva: bool = False, acreditacion: Acreditacion = None, observacion: str = '', valoracion_alcanzada: str = '', articulos_t1: list = [], articulos_primero: list = [], criterio: CriterioEvaluacionQuimica = None):
        super().__init__(produccion_cientifica=produccion_cientifica, positiva=positiva, acreditacion=acreditacion, observacion=observacion, valoracion_alcanzada=valoracion_alcanzada)
        self.articulos_t1 = articulos_t1
        self.articulos_primero = articulos_primero
        self.criterio = criterio

    def get_publicaciones_t1(self):
        """
        Método para conseguir los artículos del tercil uno necesarios para la producción principal.
        """
        publicaciones_t1 = []
        if self.articulos_t1:
            for publicacion in self.articulos_t1:
                publicaciones_t1.append(publicacion)
                if len(publicaciones_t1) == self.criterio.t1_publicaciones:
                    return publicaciones_t1
        return publicaciones_t1

    def get_publicaciones_primero(self):
        """
        Método para conseguir las publicaciones en las que eres primer autor para la producción principal.
        """
        publicaciones_primero = []
        if self.articulos_primero:
            for publicacion in self.articulos_primero:
                publicaciones_primero.append(publicacion)
                if len(publicaciones_primero) == self.criterio.t1_ap_publicaciones:
                    return publicaciones_primero
        return publicaciones_primero

    def get_produccion_sustitutoria(self):
        """
        Método que prepara las publicaciones de producción sustitutoria.
        """
        produccion_sustitutoria = []
        p1 = self.articulos_t1
        p_primero = self.articulos_primero
        if p1 or p_primero:
            for publicacion in self.produccion_cientifica:
                if publicacion not in p1 and publicacion not in p_primero:
                    produccion_sustitutoria.append(publicacion)
        return produccion_sustitutoria
