from model.process.Proceso2.Entities.Comites.Comite import Comite
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio
from model.process.Proceso2.Entities.RO import RO

class ComiteCienciasEconomicasYEmpresariales(Comite):
    """
    Comité encargado de la evaluación de solicitud de sexenios para la comisión de Biología celular y molecular.
    """
    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)
    
    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        evaluacion = EvaluacionSexenio(produccion_cientifica=produccion_cientifica,
        parametros=self.get_criterio())
        clasificacion = evaluacion.get_clasificacion_produccion()

        if clasificacion:
            publicaciones = []
            min_publicaciones = evaluacion.parametros['min_publicaciones']
            
            if len(clasificacion.publicaciones_q1) >= min_publicaciones:
                publicaciones = clasificacion.publicaciones_q1[0:min_publicaciones]
            else:
                publicaciones = clasificacion.publicaciones_q1[0:]
                restantes = min_publicaciones - len(publicaciones)
                
                if len(clasificacion.publicaciones_q2) >= restantes:
                        publicaciones += clasificacion.publicaciones_q2[0:restantes]
                elif len(clasificacion.publicaciones_q2) >= 2:
                    publicaciones += clasificacion.publicaciones_q2[0:]
                    restantes = min_publicaciones - len(publicaciones)

                    if restantes > 0 and restantes <= evaluacion.parametros['min_q1q2']:
                        if clasificacion.publicaciones_q3:
                            if len(clasificacion.publicaciones_q3) >= restantes:
                                publicaciones += clasificacion.publicaciones_q3[0:restantes]
                            else:
                                publicaciones += clasificacion.publicaciones_q3[0:]
                                restantes = min_publicaciones - len(publicaciones)
                        
                        if restantes > 0 and clasificacion.publicaciones_q4:
                            if len(clasificacion.publicaciones_q4) >= restantes:
                                publicaciones += clasificacion.publicaciones_q4[0:restantes]
                            else:
                                publicaciones += clasificacion.publicaciones_q4[0:]

            if len(publicaciones) == min_publicaciones:
                puntuacion = 0
                for art in publicaciones:
                    puntuacion += self.get_puntuacion_publicacion(art, evaluacion.parametros['puntuaciones'])
                
                evaluacion.puntuacion = puntuacion
                evaluacion.produccion_principal = publicaciones
            
        return evaluacion        

    def get_puntuacion_publicacion(self, element:RO, puntuaciones:dict) -> int:
        """
        Método que calcula la puntuación que tiene un artículo en base al cuartil al que pertenece y al número de autores que tiene.
        :param RO artículo que se evaluará
        :param puntuaciones diccionario que nos proporciona las puntuaciones establecidas en la configuración
        :result int puntuación obtenida
        """
        puntuacion = 0
        cuartil = element.get_cuartil()
        if cuartil == 1:
            puntuacion = puntuaciones['puntuacion_q1']
        elif cuartil == 2:
            puntuacion = puntuaciones['puntuacion_q2']
        elif cuartil == 3:
            puntuacion = puntuaciones['puntuacion_q3']
        elif cuartil == 4:
            puntuacion = puntuaciones['puntuacion_q4']
        return puntuacion