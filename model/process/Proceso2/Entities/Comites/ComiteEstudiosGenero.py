from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio
from model.process.Proceso2.Entities.Comites.ComiteCienciasSociales import ComiteCienciasSociales

class ComiteEstudiosGenero(ComiteCienciasSociales):
    """
    Comité que evalúa el área de Estudios de Género dentro del comité 7.1.
    """
    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        evaluacion = EvaluacionSexenio(produccion_cientifica=produccion_cientifica, parametros=self.get_criterio('estudiosgenero'))
        clasificacion = evaluacion.get_clasificacion_produccion()

        if clasificacion:
            min_publicaciones = evaluacion.parametros['min_publicaciones']
            if clasificacion.publicaciones_q1:
                if len(clasificacion.publicaciones_q1) >= min_publicaciones:
                    evaluacion.produccion_principal = clasificacion.publicaciones_q1[0:4]
                else:
                    evaluacion.produccion_principal = clasificacion.publicaciones_q1[0:]
                    restantes = min_publicaciones-len(evaluacion.produccion_principal)
                    
                    if clasificacion.publicaciones_q2:
                        if len(clasificacion.publicaciones_q2) >= restantes:
                            evaluacion.produccion_principal += clasificacion.publicaciones_q2[0:restantes]
                        
                        else:
                            evaluacion.produccion_principal += clasificacion.publicaciones_q2[0:]
                            restantes = min_publicaciones-len(evaluacion.produccion_principal)

                    if restantes == 1:
                        if clasificacion.publicaciones_q3:
                            evaluacion.produccion_principal.append(clasificacion.publicaciones_q3[0])
                        elif clasificacion.publicaciones_q4:
                            evaluacion.produccion_principal.append(clasificacion.publicaciones_q4[0])
                                                
                    if len(evaluacion.produccion_principal) >= min_publicaciones:
                        for art in evaluacion.produccion_principal:
                            evaluacion.puntuacion += self.get_puntuacion_articulo(art, evaluacion.parametros)

        return evaluacion