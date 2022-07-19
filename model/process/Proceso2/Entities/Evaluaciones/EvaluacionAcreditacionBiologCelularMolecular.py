from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion

"""
Criterio de evaluación de la acreditación de la comisión de Biología Celular y Molecular,
refleja:
minimo_articulos: mínimo de artículos que tiene que tener
num_t1: el número de artículos mínimo que deben estar en el primer tercil.
num_autoria: el número de artículos mínimo con autoría preferente.
"""
class CriterioEvaluacionBiologiaCelularMolecular():
    def __init__(self, minimo_articulos_100:int, num_t1_100:int, num_autoria_100:int,
        minimo_articulos_75:int, num_t1_75:int, num_autoria_75:int):
        self.minimo_articulos_100 =minimo_articulos_100 
        self.num_t1_100 = num_t1_100
        self.num_autoria_100 = num_autoria_100
        self.minimo_articulos_75 =minimo_articulos_75
        self.num_t1_75 = num_t1_75
        self.num_autoria_75 = num_autoria_75

"""
Resultado de la evaluación de la comisión de Biología Celular y Molecular de una solicitud de acreditación
"""
class EvaluacionAcreditacionBiologCelularMolecular(EvaluacionAcreditacion):
    def __init__(self, produccion_cientifica:list = [], positiva:bool=False, 
        acreditacion:Acreditacion=None, observaciones:str='', valoracion_alcanzada:str='',
        publicaciones_t1:list=[], publicaciones_autoria_preferente:list=[], 
        criterio:CriterioEvaluacionBiologiaCelularMolecular=None):
        super().__init__(produccion_cientifica=produccion_cientifica, positiva = positiva, acreditacion=acreditacion, 
        observacion=observaciones)
        self.publicaciones_t1 = publicaciones_t1
        self.publicaciones_autoria_preferente = publicaciones_autoria_preferente
        self.valoracion_alcanzada = valoracion_alcanzada
        self.criterio = criterio

    def get_publicaciones_t1(self):
        """
        Método que obtiene las publicaciones en el primer tercil que deben estar en 
        la producción principal del informe.
        """
        num = self.criterio.num_t1_100
        if self.publicaciones_t1:
            if len(self.publicaciones_t1) < num: 
                num = self.criterio.num_t1_75

            if len(self.publicaciones_t1) >= num:             
                return self.publicaciones_t1[0:num]
            return self.publicaciones_t1[0:]
        return None
    
    def get_publicaciones_autoria_preferente(self):
        """
        Método que obtiene las publicaciones con autoria preferente que deben estar en 
        la producción científica del informe.
        """
        num = self.criterio.num_autoria_100
        if self.publicaciones_autoria_preferente:
            if len(self.publicaciones_autoria_preferente) < num: 
                num = self.criterio.num_autoria_75

            if len(self.publicaciones_autoria_preferente) >= num:             
                return self.publicaciones_autoria_preferente[0:num]
            return self.publicaciones_autoria_preferente[0:]
        return None


    def get_produccion_sustitutoria(self):
        """
        Método para obtener la producción sustitutoria.
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
