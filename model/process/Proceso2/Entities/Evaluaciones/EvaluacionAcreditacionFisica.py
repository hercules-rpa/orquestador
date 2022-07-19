from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion

class CriterioEvaluacionFisica():
    """
    Criterio de evaluación de la acreditación de la comisión de Física:

    minimo_articulos: mínimo de artículos que tiene que tener
    num_t1: el número de artículos mínimo que deben estar en el primer tercil.
    num_autoria: el número de artículos mínimo con autoría preferente.
    """
    def __init__(self, minimo_articulos:int, num_t1:int, num_t1_t2:int, min_t1:int):
        self.minimo_articulos = minimo_articulos
        self.num_t1 = num_t1
        self.num_t1_t2 = num_t1_t2
        self.min_t1 = min_t1

class EvaluacionAcreditacionFisica(EvaluacionAcreditacion):
    """
    Resultado de la comisión de Física para una solicitud de acreditación.
    """
    def __init__(self, produccion_cientifica: list = [], positiva: bool = False,acreditacion: Acreditacion = None, observacion: str = '',valoracion_alcanzada: str = '', articulos_t1: list = [], articulos_t2: list = [], criterio: CriterioEvaluacionFisica = None):
        super().__init__(produccion_cientifica=produccion_cientifica, positiva=positiva, acreditacion=acreditacion, observacion=observacion, valoracion_alcanzada=valoracion_alcanzada)
        self.articulos_t1 = articulos_t1
        self.articulos_t2 = articulos_t2
        self.criterio = criterio

    def get_publicaciones_t1(self):
        """
        Obtiene los artículos que forman parte de las publicaciones en t1 que deben estar en la producción principal.
        """
        publicaciones_necesarias_t1 = []
        if self.articulos_t1:
            for publicacion in self.articulos_t1:
                publicaciones_necesarias_t1.append(publicacion)
                if len(publicaciones_necesarias_t1) == self.criterio.num_t1:
                    return publicaciones_necesarias_t1
        return publicaciones_necesarias_t1

    def get_publicaciones_t1_t2(self):
        """
        Obtiene los artículos que forman parte de las publicaciones en t1 y t2 que deben estar en la producción principal.
        """
        publicaciones_necesarias_t1_t2 = []
        if self.produccion_cientifica:
            if self.articulos_t1:
                for publicacion in self.articulos_t1:
                    publicaciones_necesarias_t1_t2.append(publicacion)
                    if len(publicaciones_necesarias_t1_t2) == self.criterio.num_t1_t2:
                        return publicaciones_necesarias_t1_t2
            if self.articulos_t2:
                for publicacion in self.articulos_t2:
                    publicaciones_necesarias_t1_t2.append(publicacion)
                    if len(publicaciones_necesarias_t1_t2) == self.criterio.num_t1_t2:
                        return publicaciones_necesarias_t1_t2                
        return publicaciones_necesarias_t1_t2

    def get_produccion_sustitutoria(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        """
        produccion_sustitutoria = []
        if self.articulos_t1 or self.articulos_t2:
            p1 = self.get_publicaciones_t1()
            p1_p2 = self.get_publicaciones_t1_t2()
            for publicacion in self.produccion_cientifica:
                if publicacion not in p1 and publicacion not in p1_p2:
                    produccion_sustitutoria.append(publicacion)
        return produccion_sustitutoria
        