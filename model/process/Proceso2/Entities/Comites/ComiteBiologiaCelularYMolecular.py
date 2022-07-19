from model.process.Proceso2.Entities.RO import RO
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionSexenios.EvaluacionSexenio import EvaluacionSexenio, InfoClasificacion
from model.process.Proceso2.Entities.Comites.Comite import Comite


class ComiteBiologiaCelularYMolecular(Comite):
    """
    Comité encargado de la evaluación de solicitud de sexenios para la comisión de Biología celular y molecular.
    
    :return EvaluacionSexenio: objeto con el resultado de la evaluación.
    """
    def __init__(self, id, evaluador, es_comision: bool = False):
        super().__init__(id, evaluador, es_comision)

    def get_evaluacion_sexenio(self, produccion_cientifica) -> EvaluacionSexenio:
        evaluacion = EvaluacionSexenio(produccion_cientifica=produccion_cientifica, 
            parametros= self.get_criterio())
        clasificacion = evaluacion.get_clasificacion_produccion()

        tupla = self.criterio1(clasificacion, evaluacion.parametros)
        if tupla and tupla[0] > 0:
            evaluacion = self.hidratar_evaluacion(tupla, evaluacion)
        else:
            tupla = self.criterio2(clasificacion, evaluacion.parametros)
            if tupla and tupla[0] > 0:
                evaluacion = self.hidratar_evaluacion(tupla, evaluacion)
            else:
                tupla = self.criterio3(clasificacion, evaluacion.parametros)                
                if tupla and tupla[0] > 0:
                    evaluacion = self.hidratar_evaluacion(tupla, evaluacion)
                else:
                    tupla = self.criterio4(clasificacion, evaluacion.parametros)
                    if tupla and tupla[0] > 0:
                        evaluacion = self.hidratar_evaluacion(tupla, evaluacion)
        return evaluacion        
        
    
    def hidratar_evaluacion(self, tupla:tuple([int, list]), evaluacion:EvaluacionSexenio) -> EvaluacionSexenio:
        """
        Método que sirve para hidratar las propiedades puntuación y producción principal de las evaluaciones.
        :param tupla tupla que contiene la puntuación y la lista de publicaciones
        :param evaluación evaluación del sexenio
        :return evaluación evaluación resultante
        """
        if tupla and evaluacion: 
            evaluacion.puntuacion = tupla[0]
            evaluacion.produccion_principal = tupla[1]
        return evaluacion
   
    def get_puntuacion(self, element: RO, puntuaciones:dict) -> int:
        """
        Método que obtiene la puntuación de un RO en base a los criterios establecidos
        por el comité.
        :param RO elemento que se evaluará para asignar la puntuación
        :return int puntuación obtenida
        """
        puntuacion = 0
        if element:
            if element.get_decil() == 1:
                if element.posicion_autor == 1:
                    puntuacion = puntuaciones['puntuacion_d1_autoria_destacada']
                elif element.posicion_autor == 2 and element.nautores <= 6:
                    puntuacion = puntuaciones['puntuacion_d1_autoria_secundaria']
                else:
                    puntuacion = puntuaciones['puntuacion_d1_mas_6_autores']
            else:
                cuartil = element.get_cuartil()
                if cuartil == 1:
                    if element.posicion_autor == 1:
                        puntuacion = puntuaciones['puntuacion_q1_autoria_destacada']
                    elif element.posicion_autor == 2 and element.nautores <= 6:
                        puntuacion = puntuaciones['puntuacion_q1_autoria_secundaria']
                    else:
                        puntuacion = puntuaciones['puntuacion_q1_mas_6_autores']
                elif cuartil == 2:
                    if element.posicion_autor == 1:
                        puntuacion = puntuaciones['puntuacion_q2_autoria_destacada']
                    elif element.posicion_autor == 2 and element.nautores <= 6:
                        puntuacion = puntuaciones['puntuacion_q2_autoria_secundaria']
                    else:
                        puntuacion = puntuaciones['puntuacion_q2_mas_6_autores']
                elif cuartil == 3:
                    if element.posicion_autor == 1:
                        puntuacion = puntuaciones['puntuacion_q3_autoria_destacada']
                    elif element.posicion_autor == 2 and element.nautores <= 6:
                        puntuacion = puntuaciones['puntuacion_q3_autoria_secundaria']
                    else:
                        puntuacion = puntuaciones['puntuacion_q3_mas_6_autores']
                elif cuartil == 4:
                    if element.posicion_autor == 1:
                        puntuacion = puntuaciones['puntuacion_q4_autoria_destacada']
                    elif element.posicion_autor == 2 and element.nautores <= 6:
                        puntuacion = puntuaciones['puntuacion_q4_autoria_secundaria']
                    else:
                        puntuacion = puntuaciones['puntuacion_q4_mas_6_autores']
        return puntuacion

    def get_puntuacion_total(self, elements:list, puntuaciones:dict) -> int:
        """
        Método que obtiene la puntuación total de una colección.
        :param list lista de elementos de la que se va a obtener la puntuación.
        :return int puntuación total.
        """
        puntuacion =0
        if elements:
            for element in elements:
                puntuacion += self.get_puntuacion(element, puntuaciones)

        return puntuacion
                
    def criterio1(self, clasificacion: InfoClasificacion, parametros:dict) -> tuple([int, list]):
        """
        Método que evalúa si se tiene 5 aportaciones en Q1 (firmante en cualquier posición).
        :param InfoClasificacion clasificación de la producción científica del investigador.
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal
        """
        puntuacion = 0
        results = []
        criterio = parametros['criterio1']
        if clasificacion and len(clasificacion.publicaciones_q1) >= criterio['num_publicaciones_q1']:
            results = clasificacion.publicaciones_q1[0:criterio['num_publicaciones_q1']]

        if results:
            puntuacion = self.get_puntuacion_total(results,parametros['puntuaciones'])

        return (puntuacion, results)

    def es_firmante_destacado(self, element: RO) -> bool:
        """
        Método que comprueba si el investigador es un firmante destacado en el artículo,
        para ello, debe ser:
        - primer firmante
        - segundo firmante 
        - segundo firmante pero que no tenga más de seis autores la publicación
        :param RO elemento a analizar
        :return bool true si es firmante destacado.
        """
        if element.posicion_autor == 1:
            return True
        elif element.posicion_autor > 6 and element.posicion_autor == 2:
            return True
        elif element.posicion_autor <= 6 and element.posicion_autor == 2:
            return True
        return False

    def criterio2(self, clasificacion: InfoClasificacion, parametros:dict) -> tuple([int, list]):
        """
        Método que evalúa si se tiene 5 aportaciones en Q2, 
        de las cuales 3 con firmante destacado.
        :param InfoClasificacion clasificación de la producción científica del investigador.
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal.
        """
        puntuacion = 0
        results = []
        criterio = parametros['criterio2']
        if clasificacion and len(clasificacion.publicaciones_q2) >= criterio['num_publicaciones_q2']:
            arts_firmante_destacado = []
            aux = []
            i = 0

            while len(clasificacion.publicaciones_q2) < i:
                element = arts_firmante_destacado[i]
                if self.es_firmante_destacado(element):
                    arts_firmante_destacado.append(element)
                else:
                    aux.append(element)
                i += 1

            if len(arts_firmante_destacado) >= criterio['num_publicaciones_q2']:
                results = arts_firmante_destacado[0:criterio['num_publicaciones_q2']]
            elif len(arts_firmante_destacado) >= criterio['num_firmante_destacado']:
                results = arts_firmante_destacado

                if aux:
                    restantes = criterio['num_publicaciones_q2'] - len(arts_firmante_destacado)
                    if len(aux) >= restantes:
                        results += aux[0:restantes]
                    else:
                        results += aux[0:]

        if len(results) == criterio['num_publicaciones_q2']:
            puntuacion += self.get_puntuacion_total(results, parametros['puntuaciones'] )

        return (puntuacion, results)

    def get_elements_firmante_destacado(self, elements: list) -> list:
        """
        Método que obtiene la cantidad de elementos que tienen firmante destacado de la lista.
        :param list: lista que contiene los elementos a analizar.
        :return list: lista con los elementos que tienen firmante destacado.
        """
        results = []
        i = 0
        while(len(elements) < i and len(results) < 3):
            element = elements[i]
            if self.es_firmante_destacado(element):
                results.append(element)
        return results

    def criterio3(self, clasificacion: InfoClasificacion, parametros:dict) -> tuple([int, list]):
        """
        Método que evalúa si hay menos de 5 Aportaciones:
            - 3 D1 como persona firmante destacada en todas ellas.
            - 4 Q1 con autoría destacada en al menos 2.
        :param InfoClasificacion clasificación de la producción científica del investigador.
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal
        """
        results = []
        puntuacion = 0
        criterio = parametros['criterio3']
        if clasificacion:
            if len(clasificacion.publicaciones_d1) >= criterio['num_publicaciones_d1']:
                elements = self.get_elements_firmante_destacado(clasificacion.publicaciones_d1)
                if len(elements) >= criterio['num_publicaciones_d1']:
                    results = elements[0:criterio['num_publicaciones_d1']]
                    puntuacion = self.get_puntuacion_total(results, parametros['puntuaciones'])


            if not results and len(clasificacion.publicaciones_q1) >= criterio['num_publicaciones_q1']:
                elements = self.get_elements_firmante_destacado(clasificacion.publicaciones_q1)
                if len(elements) >= criterio['num_firmante_destacado_q1']:
                    results = elements[0:criterio['num_firmante_destacado_q1']]                
                    #TODO: comprobar que funciona
                    i=0
                    while(len(results) < 4 and len(clasificacion.publicaciones_q1) < i):                   
                        art = clasificacion.publicaciones_q1[i]
                        if art not in results:
                            results.append(art)

                    if len(results) == criterio['num_publicaciones_q1']:
                        puntuacion = self.get_puntuacion_total(results, parametros['puntuaciones']) 

        return (puntuacion, results)

    def criterio4(self, clasificacion:InfoClasificacion, parametros:dict) -> tuple([int, list]):
        """
        Método que evalúa el críterio: 5 Aportaciones: 5 Q1/Q2 combinadas.
        :param InfoClasificacion clasificación de la producción científica del investigador.
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal
        """
        puntuacion = 0
        results = []
        criterio = parametros['criterio4']
        if clasificacion and clasificacion.publicaciones_q1 and clasificacion.publicaciones_q2:
            results = clasificacion.publicaciones_q1[0:]
            restantes = criterio['num_publicaciones_q1q2']-len(clasificacion.publicaciones_q1)

            if len(clasificacion.publicaciones_q2) >= restantes:
                results += clasificacion.publicaciones_q2[0:restantes]

            if len(results) == criterio['num_publicaciones_q1q2']:
                puntuacion = self.get_puntuacion_total(results, parametros['puntuaciones'])

        return (puntuacion, results)