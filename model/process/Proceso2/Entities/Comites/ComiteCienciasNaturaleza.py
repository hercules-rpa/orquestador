from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio
from model.process.Proceso2.Entities.Comites.Comite import Comite
"""
Comité que se encarga de la evaluación de la solicitud de sexenios del área de 
Ciencias de la Naturaleza - id(4).
"""
class ComiteCienciasNaturaleza(Comite):
    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    def get_produccion_principal(self, articulos_clasificados:list, num:int) -> tuple([int, list]):        
        """
        Método encargado de la obtención de la producción principal con mejor baremo para 
        la solicitud del sexenio.
        :param [] articulos_clasificados: lista cuyos elementos son listas clasificadas por los criterios del sexenio.
        :param int num: número de artículos que se necesita como producción principal.
        :return tupla [int, list] que devuelve la puntuación total y la lista de artículos seleccionados.
        """
        num_faltantes = num
        produccion_principal = []
        puntuacion = 0
        if articulos_clasificados:
            for articulos in articulos_clasificados:
                if num_faltantes != 0:
                    results = []
                    if len(articulos) >= num_faltantes:
                        results = articulos[0:(num_faltantes+1)]
                    else:
                        results = articulos[0:]

                    if results:
                        for tupla in results:
                            produccion_principal.append(tupla[0])               
                            puntuacion += tupla[1]
                        num_faltantes -= len(results)
                else:
                    break    
        return (puntuacion, produccion_principal)

    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        """
        Método encargado de realizar la baremación del sexenio.
        :param [] produccion_científica: listado de artículos de un investigador.
        :return EvaluacionSexenio evaluación del sexenio.        
        """
        evaluacion:EvaluacionSexenio = EvaluacionSexenio(produccion_cientifica=produccion_cientifica,
        parametros=self.get_criterio())
        if produccion_cientifica:
            art_decil = []
            art_q1 = []
            art_q2 = []
            art_q3 = []
            art_q4 = []
            
            puntuaciones = evaluacion.parametros['puntuaciones']

            for element in produccion_cientifica:
                if element.get_decil() == 1:
                    art_decil.append((element, puntuaciones['puntuacion_d1']))
                elif element.get_cuartil() == 1:
                    art_q1.append((element, puntuaciones['puntuacion_q1']))
                elif element.get_cuartil() == 2:
                    art_q2.append((element, puntuaciones['puntuacion_q2']))
                elif element.get_cuartil() == 3:
                    art_q3.append((element, puntuaciones['puntuacion_q3']))
                elif element.get_cuartil() == 4:
                    art_q4.append((element, puntuaciones['puntuacion_q4'])) 

            articulos_clasificados = [art_decil, art_q1, art_q2, art_q3, art_q4]
            tupla = self.get_produccion_principal(articulos_clasificados, evaluacion.parametros['min_publicaciones'])
            if tupla:
                evaluacion.puntuacion = tupla[0]
                evaluacion.produccion_principal = tupla[1]        
                    
        return evaluacion



            
                

                
                

                

            


