
from model.process.Proceso2.Entities.Acreditacion import Acreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacion import EvaluacionAcreditacion

"""
El criterio de relevancia define el número de artículos que se necesita de cada tipo
para que una evaluación sea positiva.
"""
class CriterioRelevancia():
    def __init__(self, num_relevantes:int, num_muy_relevantes:int):
        self.num_relevantes = num_relevantes
        self.num_muy_relevantes = num_muy_relevantes

        print('relevantes: ' + str(num_relevantes))

"""
Evaluación resultante de analizar una solicitud de acreditación de las comisiones que tienen como criterio las relevancias de las publicaciones.
"""
class EvaluacionAcreditacionRelevancia(EvaluacionAcreditacion):
    def __init__(self, articulos:list = [], positiva:bool=False, acreditacion:Acreditacion=None, 
        observacion:str='', valoracion_alcanzada:str='', articulos_relevantes:list=[],
        articulos_muyrelevantes:list=[], criterio:CriterioRelevancia = None):
        
        super().__init__(produccion_cientifica=articulos, positiva = positiva, 
        acreditacion = acreditacion, observacion=observacion)
        self.valoracion_alcanzada = valoracion_alcanzada
        self.articulos_relevantes = articulos_relevantes
        self.articulos_muyrelevantes = articulos_muyrelevantes
        self.criterio = criterio

    def get_articulos_relevantes(self):
        """
        Método para obtener los articulos relevantes.
        """
        if self.articulos_relevantes:
            if len(self.articulos_relevantes) >= self.criterio.num_relevantes:
                return self.articulos_relevantes[0:self.criterio.num_relevantes]
            return self.articulos_relevantes[0:]
        return None    

    def get_articulos_muy_relevantes(self):
        """
        Método para obtener los articulos muy relevantes.
        """
        if self.articulos_muyrelevantes:
            if len(self.articulos_muyrelevantes) >= self.criterio.num_muy_relevantes:
                return self.articulos_muyrelevantes[0:self.criterio.num_muy_relevantes]
            return self.articulos_muyrelevantes[0:]
        return None
    
    def get_produccion_sustitutoria(self):
        """
        Método para obtener la producción sustitutoria.
        """
        result = self.produccion_cientifica
        if result:
            articulos = self.get_articulos_relevantes()
            muy_relevantes = self.get_articulos_muy_relevantes()
            if muy_relevantes:
                articulos += muy_relevantes
            
            if articulos:
                for art in articulos:
                    result.remove(art)
        return result
            