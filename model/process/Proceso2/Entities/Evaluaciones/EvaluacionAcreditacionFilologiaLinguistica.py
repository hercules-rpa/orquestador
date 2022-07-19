from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion

class CriterioAcreditacionFilologiaLinguistica():
    """
    Criterio de evaluación de la acreditación de la comisión de Filología Lingüística

    num_articulos: número de artículos que tiene que tener el investigador.
    num_t1: número de artículos mínimo que deben estar en el primer tercil.
    num_monograficas: número de artículos minimo incluido en monografícas
    """

    def __init__(self, num_articulos: int, num_t1: int, min_porcentaje: int):
        self.num_articulos = num_articulos
        self.num_t1 = num_t1
        self.min_porcentaje = min_porcentaje


class EvaluacionAcreditacionFilologiaLinguistica(EvaluacionAcreditacion):
    """
    Resultado de la comisión de Filología y Lingüistica para una solicitud de acreditación.
    """
    def __init__(self, produccion_cientifica: list = [], positiva: bool = False, acreditacion: Acreditacion = None, observacion: str = '', publicaciones_n1: list = [], criterio: CriterioAcreditacionFilologiaLinguistica=None):
        super().__init__(produccion_cientifica=produccion_cientifica, positiva=positiva, acreditacion=acreditacion, observacion=observacion)
        self.publicaciones_n1 = publicaciones_n1
        self.criterio = criterio

    def get_publicaciones_n1(self):
        """
        Obtiene los artículos que forman parte de las publicaciones de nivel 1 que deben estar en la prucción principal
        """
        num = self.criterio.num_t1
        if self.publicaciones_n1:
            if len(self.publicaciones_n1) >= num:
                return self.publicaciones_n1[0:num]
            return self.publicaciones_n1[0:]
        return None

    def get_produccion_sustitutoria(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        """
        produccion_sustitutoria = []
        if self.publicaciones_n1 or self.monografias_n1:
            p_n1 = self.get_publicaciones_n1()
            for publicacion in self.produccion_cientifica:
                if publicacion not in p_n1:
                    produccion_sustitutoria.append(publicacion)
        return produccion_sustitutoria
        