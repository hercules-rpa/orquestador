from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion

"""
Criterio de evaluación de la acreditación de la comisión de Otras Especialidades Sanitarias,
refleja:
minimo_articulos: el número mínimo de artículos que tiene que tener
num_autoria: el número mínimo de artículos con autoría preferente
num_autoria_t1: el número mínimo de artículos con autoría preferente que deben estar en el primer tercil.
"""
class CriterioEvaluacionOtrasEspecialidadesSanitarias():
    def __init__(self, minimo_articulos:int, num_autoria: int, num_autoria_t1: int):

        self.minimo_articulos = minimo_articulos
        self.num_autoria = num_autoria
        self.num_autoria_t1 = num_autoria_t1

class EvaluacionAcreditacionOtrasEspecialidadesSanitarias(EvaluacionAcreditacion):
    def __init__(self, produccion_cientifica: list = [], positiva: bool = False, 
                acreditacion: Acreditacion = None, observacion: str = '', 
                valoracion_alcanzada: str = '', articulos_autoria: list = [], articulos_autoria_t1: list = [],
                criterio: CriterioEvaluacionOtrasEspecialidadesSanitarias = None):
        super().__init__(produccion_cientifica=produccion_cientifica, positiva=positiva, 
                                        acreditacion=acreditacion, observacion=observacion, valoracion_alcanzada=valoracion_alcanzada)
        self.articulos_autoria = articulos_autoria
        self.articulos_autoria_t1 = articulos_autoria_t1
        self.valoracion_alcanzada = valoracion_alcanzada
        self.criterio = criterio

    def get_publicaciones_autoria_preferente_t1(self):
        """
        Método que obtiene las publicaciones con autoria preferente en el tercil 1 que debe estar
        en la producción cientifíca del informe
        """
        num = self.criterio.num_autoria_t1
        if self.articulos_autoria_t1:
            
            if len(self.articulos_autoria_t1) >= num:
                return self.articulos_autoria_t1[0:num]
            return self.articulos_autoria_t1[0:]
        return None

    def get_publicaciones_autoria_preferente(self):
        """
        Método que obtiene las publicaciones con autoria preferente que deben estar en 
        la producción científica del informe.
        """
        result = []
        articulo_autoria_t1 = self.get_publicaciones_autoria_preferente_t1()
        num = self.criterio.num_autoria
        if self.articulos_autoria and articulo_autoria_t1:
            result = self.articulos_autoria

            for art in articulo_autoria_t1:
                result.remove(art)

            if len(self.articulos_autoria) >= (num - len(articulo_autoria_t1)):             
                result = self.articulos_autoria[0:(num - len(articulo_autoria_t1))]
            else:
                result = self.articulos_autoria[0:]
            result.extend(articulo_autoria_t1)

        return result

    def get_produccion_sustitutoria(self):
        """
        Método que obtiene las publicaciones en el tercer y cuarto cuartil que deben estar
        en la producción del informe
        """
        result = self.produccion_cientifica
        if result:
            autoria = self.get_publicaciones_autoria_preferente()
            if autoria:
                for art in autoria:
                    result.remove(art)
        
        return result