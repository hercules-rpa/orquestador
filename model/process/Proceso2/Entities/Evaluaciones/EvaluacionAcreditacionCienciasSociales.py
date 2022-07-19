from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion

class CriterioAcreditacionCienciasSociales():
    """
    Criterio de evaluación de la acreditación de la comisión de Ciencias Sociales:

    num_articulos: número de artículos que tiene que tener el investigador.
    minimo_articulos: mínimo de artículos que tiene que tener el investigador
    num_t1_t2: el número de artículos que deben estar en el primer y segundo tercil.
    min_t1_t2: el número de artículos mínimo que deben estar en el primer y segundo tercil.
    min_porcentaje: el número mínimo de porcentaje que tiene que considerar el criterio.
    """
    def __init__(self, num_articulos_A: int, num_articulos_BC: int, num_t1_t2_A: int, num_t1_BC: int, num_t2_BC: int, min_porcentaje: int):
        self.num_articulos_A = num_articulos_A
        self.num_articulos_BC = num_articulos_BC
        self.num_t1_t2_A = num_t1_t2_A
        self.num_t1_BC = num_t1_BC
        self.num_t2_BC = num_t2_BC
        self.min_porcentaje = min_porcentaje
        

class EvaluacionAcreditacionCienciasSociales(EvaluacionAcreditacion):
    """
    Resultado de la comisión de Ciencias Sociales para una solicitud de acreditación.
    """
    def __init__(self, produccion_cientifica: list = [], positiva: bool = False, acreditacion: Acreditacion = None, observacion: str = '', valoracion_alcanzada: str = '', publicaciones_n1: list = [], publicaciones_n2: list = [], criterio: CriterioAcreditacionCienciasSociales=None):
        super().__init__(produccion_cientifica=produccion_cientifica, positiva=positiva, acreditacion=acreditacion, observacion=observacion)
        self.publicaciones_n1 = publicaciones_n1
        self.publicaciones_n2 = publicaciones_n2
        self.valoracion_alcanzada = valoracion_alcanzada
        self.criterio = criterio

    def get_publicaciones_n1_n2(self):
        """
        Método para obtener las publicaciones del tercil primero y segundo en la producción principal.
        """
        p_n1_n2 = []
        if self.publicaciones_n1 or self.publicaciones_n2:
            for articulo in self.publicaciones_n1:
                p_n1_n2.append(articulo)
                if len(p_n1_n2) == self.criterio.num_t1_t2_A:
                    return p_n1_n2
            for articulo in self.publicaciones_n2:
                p_n1_n2.append(articulo)
                if len(p_n1_n2) == self.criterio.num_t1_t2_A:
                    return p_n1_n2
        return p_n1_n2

    def get_produccion_sustitutoria(self):
        """
        Método para obtener la producción científica sustitutoria para esta comisión de Ciencias Sociales.
        """
        p_sustitutoria = []
        if self.produccion_cientifica:
            p_n1_n2 = self.get_publicaciones_n1_n2()
            for articulo in self.produccion_cientifica:
                if articulo not in p_n1_n2:
                    p_sustitutoria.append(articulo)
        return p_sustitutoria
