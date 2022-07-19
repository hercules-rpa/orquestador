from model.process.Proceso2.Entities.Evaluaciones.Evaluacion import Evaluacion

"""
Clase que almacena el resultado de la clasificación de una producción científica en cuartiles.
"""
class InfoClasificacion():
    def __init__(self, publicaciones_q1:list=[], publicaciones_q2:list=[], 
        publicaciones_q3:list=[], publicaciones_q4:list=[], publicaciones_d1:list=[]):
        self.publicaciones_q1 = publicaciones_q1
        self.publicaciones_q2 = publicaciones_q2
        self.publicaciones_q3 = publicaciones_q3
        self.publicaciones_q4 = publicaciones_q4
        self.publicaciones_d1 = publicaciones_d1

class EvaluacionSexenio(Evaluacion):
    """
    Entidad que representa la evaluación que realiza un comité sobre una solicitud de sexenio.
    """
    def __init__(self, produccion_cientifica: list = [], observacion: str = '', 
        puntuacion: int = 0, produccion_principal:list=[], parametros:dict=None):
        super().__init__(produccion_cientifica, observacion)
        self.puntuacion = puntuacion        
        """
        Producción que se incluirá en el informe de sexenio como principal, está lista representa
        los artículos con mayor puntuación.
        """
        self.produccion_principal = produccion_principal
        self.parametros = parametros

    def get_produccion_sustitutoria(self):
        """
        Obtiene los artículos que forman parte de la producción sustitutoria eliminando
        de la lista de producción científica los artículos que forman parte de la producción
        principal.
        """
        if self.produccion_cientifica and self.produccion_principal:
            result = self.produccion_cientifica
            for art in self.produccion_principal:
                if art in result:
                    result.remove(art)
        return result

    def get_clasificacion_produccion(self) -> InfoClasificacion:
        """
        Método que clasifica las publicaciones dependiendo del cuartil al que pertenezcan.
        :return InfoCuartiles, clase que devuelve la clasificación.
        """
        result: InfoClasificacion = InfoClasificacion()
        if self.produccion_cientifica:
            for pc in self.produccion_cientifica:
                cuartil = pc.get_cuartil()
                if cuartil == 1:
                    result.publicaciones_q1.append(pc)
                elif cuartil == 2:
                    result.publicaciones_q2.append(pc)
                elif cuartil == 3:
                    result.publicaciones_q3.append(pc)
                elif cuartil == 4:
                    result.publicaciones_q4.append(pc)
                
                if pc.get_decil() == 1:
                    result.publicaciones_d1.append(pc)

        return result
                    
        
        