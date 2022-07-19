from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion

"""
Criterio de evaluación de la acreditación de la comisión de Medicina Clinica y Especialidades Clinicas,
refleja:
minimo_articulos: mínimo de artículos que tiene que tener
num_t1: el número de artículos mínimo que deben estar en el primer tercil.
num_autoria: el número de artículos mínimo con autoría preferente.
num_autoria_t1: el número de artículos mínimo con autoría prefente en el primer tercil.
"""
class CriterioEvaluacionMedicinaClinicaYespecialidades():
    def __init__(self, minimo_articulos:int, num_t1:int, num_autoria:int, num_autoria_t1:int):
        
        self.minimo_articulos = minimo_articulos
        self.num_t1 = num_t1
        self.num_autoria = num_autoria
        self.num_autoria_t1 = num_autoria_t1
"""
Resultado de la comisión de Medicina clínica y Especialidades clínicas para una solicitud de acreditación.
"""

class EvaluacionAcreditacionMedicinaClinicaYEspecialidades(EvaluacionAcreditacion):
    def __init__(self, produccion_cientifica: list = [], positiva: bool = False, 
                acreditacion: Acreditacion = None, observacion: str = '', valoracion_alcanzada: str = '',
                articulos_t1: list = [], articulos_t2: list = [], articulos_autoria: list = [], articulos_autoria_t1: list = [],
                                        criterio:CriterioEvaluacionMedicinaClinicaYespecialidades=None):
        super().__init__(produccion_cientifica=produccion_cientifica, positiva=positiva, 
                                        acreditacion=acreditacion, observacion=observacion, valoracion_alcanzada=valoracion_alcanzada)
        self.articulos_t1 = articulos_t1
        self.articulos_t2 = articulos_t2
        self.articulos_autoria = articulos_autoria
        self.articulos_autoria_t1 = articulos_autoria_t1
        self.criterio = criterio

    def get_publicaciones_t1(self):
        """
        Método que obtiene las publicaciones en el primer tercil que deb estar en 
        la producción principal del informe
        """
        num = self.criterio.num_t1
        if self.articulos_t1:
            if len(self.articulos_t1) >= num:
                return self.articulos_t1[0:num]
            return self.articulos_t1[0:]
        return None
    
    def get_publicaciones_autoria_preferente(self):
        """
        Método que obtiene las publicaciones con autoria preferente que deben estar en 
        la producción científica del informe
        """
        num = self.criterio.num_autoria
        result = []
        articulo_autoria_t1 = self.get_publicaciones_autoria_preferente_t1()
        
        for art in articulo_autoria_t1:
            result.remove(art)

        if len(self.articulos_autoria) >= (num - len(articulo_autoria_t1)):             
            result = self.articulos_autoria[0:(num - len(articulo_autoria_t1))]
        else:
            result = self.articulos_autoria[0:]
        result.extend(articulo_autoria_t1)

        return result

    def get_publicaciones_autoria_preferente_t1(self):
        """
        Método que obtiene las publicaciones con autoria preferente en el tercil 1 que deben
        estar en la producción científica del informe
        """
        num = self.criterio.num_autoria_t1
        if self.articulos_autoria_t1:
            if len(self.articulos_autoria_t1) >= num:
                return self.articulos_autoria_t1[0:num]
            return self.articulos_autoria_t1[0:]
        return None

    def get_produccion_sustitutoria(self):
        """
        Método que obtiene las publicaciones en el tercer y cuarto cuartil que deben estar
        en la producción del informe
        """
        result = self.produccion_cientifica
        if result:
            elements = self.get_publicaciones_t1()
            autoria = self.get_publicaciones_autoria_preferente()
            for art in autoria:
                if art not in elements:
                    elements.append(art)
            
            if elements:
                for elem in elements:
                    result.remove(elem)
        return result