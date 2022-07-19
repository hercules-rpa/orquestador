from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion


class CriterioEvaluacionCienciasEconomicasYEmpresariales():
    def __init__(self, num_Q1_Q2 : int,  num_Q3_Q4: int,  num_D1: int):
        self.num_Q1_Q2 = num_Q1_Q2
        self.num_Q3_Q4 = num_Q3_Q4
        self.num_D1 = num_D1

class EvaluacionAcreditacionCienciasEconomicasYEmpresariales(EvaluacionAcreditacion):
    def __init__(self, produccion_cientifica: list = [], positiva: bool = False, 
        acreditacion: Acreditacion = None, observacion: str = '', 
        valoracion_alcanzada: str = '', articulos_Q1_Q2: list = [], 
        articulos_Q3_Q4 :list = [],articulos_D1: list = [],
        criterio: CriterioEvaluacionCienciasEconomicasYEmpresariales = None ):
        super().__init__(produccion_cientifica=produccion_cientifica, positiva=positiva, 
                        acreditacion=acreditacion, observacion=observacion, valoracion_alcanzada=valoracion_alcanzada)
        self.articulos_Q1_Q2 = articulos_Q1_Q2
        self.articulos_Q3_Q4 = articulos_Q3_Q4
        self.articulos_D1 = articulos_D1
        self.criterio = criterio

    def get_publicaciones_D1(self):

        """
        Métodop que obtiene las publicaciones en el primer decil que deben estar
        en la producción del informe.
        """
        num = self.criterio.num_D1
        if self.articulos_D1:
            if len(self.articulos_D1) >= num:
                return self.articulos_D1[0:num]
            return self.articulos_D1[0:]
        return None        

    def get_publicaciones_Q1_Q2(self):
        """
        Métodop que obtiene las publicaciones en el primer y segundo cuartil que deben estar
        en la producción del informe.
        """
        num = self.criterio.num_Q1_Q2
        if self.articulos_Q1_Q2:
            if len(self.articulos_Q1_Q2) >= num:
                return self.articulos_Q1_Q2[0:num]
            return self.articulos_Q1_Q2s_Q1[0:]
        return None

    def get_publicaciones_Q3_Q4(self):
        """
        Método que obtiene las publicaciones en el tercer y cuarto cuartil que deben estar
        en la producción del informe
        """
        num = self.criterio.num_Q3_Q4
        if self.articulos_Q3_Q4:
            if len(self.articulos_Q3_Q4) >= num:
                return self.articulos_Q3_Q4[0:num]
            return self.articulos_Q3_Q4[0:]
        return None
        
    def get_produccion_sustitutoria(self):
        """
        Método que obtiene las publicaciones en el tercer y cuarto cuartil que deben estar
        en la producción del informe
        """
        produccion_sustitutoria = []
        if self.produccion_cientifica:
            Q1_Q2 = self.get_publicaciones_Q1_Q2()
            Q3_Q4 = self.get_publicaciones_Q3_Q4()
            D1 = self.get_publicaciones_D1()
            for articulo in self.produccion_cientifica:
                if articulo not in Q1_Q2 and articulo not in Q3_Q4 and articulo not in D1:
                    produccion_sustitutoria.append(articulo)
        return produccion_sustitutoria
