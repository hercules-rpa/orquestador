from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionCienciasSociales import CriterioAcreditacionCienciasSociales, EvaluacionAcreditacionCienciasSociales
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion
# comisión 2

"""
    "19":{
        "name": "Ciencias sociales",
        "autoria_orden": false,
        "autoria_str" : "",
        "alerta_autores" : -1,
        "libros": true,
        "criterio":{
            "catedra":{
                "A":{
                    "min_publicaciones": 40,
                    "l1l2_publicaciones": 16
                },
                "B":{
                    "min_publicaciones": 30,
                    "l1_publicaciones": 4,
                    "l2_publicaciones": 8
                },
                "C":{
                    "min_publicaciones": 24,
                    "l1_publicaciones": 3,
                    "l2_publicaciones": 6
                }
            },
            "titularidad":{
                "A":{
                    "min_publicaciones": 24,
                    "l1l2_publicaciones": 8
                },
                "B":{
                    "min_publicaciones": 20,
                    "l1l2_publicaciones": 4
                },
                "C":{
                    "min_publicaciones": 16,
                    "l1l2_publicaciones": 4
                }
            }
        }
    },
"""

class ComisionCienciasSociales(Comision):
    """
    La comisión de Ciencias sociales se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)

    def get_evaluacion_acreditacion(self, produccion_cientifica, acreditacion: Acreditacion) -> EvaluacionAcreditacionCienciasSociales:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return El objeto EvaluacionAcreditación que contiene la evaluación de la acreditación solicitada.
        """
        evaluacion = EvaluacionAcreditacionCienciasSociales(produccion_cientifica=produccion_cientifica, acreditacion=acreditacion)
        if acreditacion.tipo == TipoAcreditacion.CATEDRA:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo)
            if criterios:
                evaluacion.criterio = CriterioAcreditacionCienciasSociales(criterios['A']['min_publicaciones'],criterios['B']['min_publicaciones'], criterios['A']['l1l2_publicaciones'],criterios['B']['l1_publicaciones'],criterios['B']['l2_publicaciones'], criterios['min_porcentaje'])
            else:
                evaluacion.criterio = CriterioAcreditacionCienciasSociales(50,30,20,4,8,80)
            return self.get_evaluacion_catedra(produccion_cientifica, evaluacion=evaluacion)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo)
            if criterios:
                evaluacion.criterio = CriterioAcreditacionCienciasSociales(criterios['A']['min_publicaciones'],criterios['B']['min_publicaciones'], criterios['A']['l1l2_publicaciones'],criterios['B']['l1l2_publicaciones'],criterios['B']['l1l2_publicaciones'], criterios['min_porcentaje'])
            else:
                evaluacion.criterio = CriterioAcreditacionCienciasSociales(30,20,10,4,4,80)
            return self.get_evaluacion_titularidad(produccion_cientifica, evaluacion=evaluacion)

    def get_evaluacion_catedra(self, produccion_cientifica, evaluacion:EvaluacionAcreditacionCienciasSociales) -> EvaluacionAcreditacionCienciasSociales:
        """
        Método para la evaluación de la cátedra de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionCienciasSociales evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Ciencias Sociales.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Ciencias Sociales.
        """
        #TODO: no entiendo a qué se refiere en el pdf de la ANECA "puntuación en méritos específicos >= 7" o "puntuación en méritos complementarios >= 7"
        eval, valoracion_alcanzada, articulos_n1, articulos_n2 = self.get_criterio_catedra_A(produccion_cientifica, evaluacion.criterio.num_articulos_A, evaluacion.criterio.num_t1_t2_A, evaluacion.criterio.min_porcentaje)
        if eval and valoracion_alcanzada == 'A':
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_n1
            evaluacion.publicaciones_n2 = articulos_n2
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observaciones_catedra(evaluacion, produccion_cientifica)
            return evaluacion
        eval, valoracion_alcanzada, articulos_n1, articulos_n2 = self.get_criterio_catedra_B_C_D(produccion_cientifica, evaluacion.criterio.num_articulos_BC, evaluacion.criterio.num_t1_t2_A, evaluacion.criterio.min_porcentaje)
        if eval and valoracion_alcanzada == 'B':
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_n1
            evaluacion.publicaciones_n2 = articulos_n2
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observaciones_catedra(evaluacion, produccion_cientifica)
            return valoracion_alcanzada
        if eval and valoracion_alcanzada == 'C':
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_n1
            evaluacion.publicaciones_n2 = articulos_n2
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observaciones_catedra(evaluacion, produccion_cientifica)
            return valoracion_alcanzada
        if eval and valoracion_alcanzada == 'D':
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_n1
            evaluacion.publicaciones_n2 = articulos_n2
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observaciones_catedra(evaluacion, produccion_cientifica)
            return valoracion_alcanzada

    def get_evaluacion_titularidad(self, produccion_cientifica, evaluacion:EvaluacionAcreditacionCienciasSociales) -> EvaluacionAcreditacionCienciasSociales:
        """
        Método para la evaluación de la titularidad de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionCienciasSociales evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Ciencias Sociales.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Ciencias Sociales.
        """
        #TODO: no entiendo a qué se refiere en el pdf de la ANECA "puntuación en méritos específicos >= 7" o "puntuación en méritos complementarios >= 7"
        eval, valoracion_alcanzada, articulos_n1, articulos_n2 = self.get_criterio_titularidad_A(produccion_cientifica, evaluacion.criterio.num_articulos_A, evaluacion.criterio.num_t1_t2_A, evaluacion.criterio.min_porcentaje)
        if eval and valoracion_alcanzada == 'A':
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_n1
            evaluacion.publicaciones_n2 = articulos_n2
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observaciones_titularidad(evaluacion, produccion_cientifica)
            return evaluacion
        eval, valoracion_alcanzada, articulos_n1, articulos_n2 = self.get_criterio_titularidad_B_C_D(produccion_cientifica, evaluacion.criterio.num_articulos_BC, evaluacion.criterio.num_t1_BC, evaluacion.criterio.num_t2_BC, evaluacion.criterio.min_porcentaje)
        if eval and valoracion_alcanzada == 'B':
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_n1
            evaluacion.publicaciones_n2 = articulos_n2
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observaciones_titularidad(evaluacion, produccion_cientifica)
            return valoracion_alcanzada
        if eval and valoracion_alcanzada == 'C':
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_n1
            evaluacion.publicaciones_n2 = articulos_n2
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observaciones_titularidad(evaluacion, produccion_cientifica)
            return valoracion_alcanzada
        if eval and valoracion_alcanzada == 'D':
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_n1
            evaluacion.publicaciones_n2 = articulos_n2
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observaciones_titularidad(evaluacion, produccion_cientifica)
            return valoracion_alcanzada

    def get_criterio_catedra_A(self, produccion_cientifica: list, num_publicaciones : int, num_n1_n2 : int, porcentaje_min : int) -> tuple([bool, str, [], []]):
        """
        Método para la evaluación del criterio que hay que superar para la obtención de una cátedra por parte del investigador.

        :param [] produccion_cientifica: Lista de producción científica de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones necesarias de nivel 1 (cuartiles 1 y 2) y nivel 2 (cuartiles 3 y 4).
        :param int porcentaje_min: Tanto por ciento mínimo necesario para determinar el critero de la cátedra de evaluación A a B.
        :return Tupla compuesta por un booleano que nos indica si es positiva la evaluación, un str con el típo de calificación en investigación y dos listas con los artículos de nivel 1 y nivel 2 presentados.
        """
        articulos_n1 = []
        articulos_n2 = []
        calificacion_investigacion = ''
        result = False
        if len(produccion_cientifica) >= num_publicaciones:
            for articulo in produccion_cientifica:
                if articulo.get_tercil() == 1:
                    articulos_n1.append(articulo)
                elif articulo.get_tercil() == 2:
                    articulos_n2.append(articulo)
            if articulos_n1 and articulos_n2 and (len(articulos_n1) + len(articulos_n2)) >= num_n1_n2:
                result = True
                calificacion_investigacion = 'A'
                return result, calificacion_investigacion, articulos_n1, articulos_n2
        if len(produccion_cientifica) >= (num_publicaciones*(porcentaje_min/100)):
            for articulo in produccion_cientifica:
                if articulo.get.tercil() == 1:
                    articulos_n1.append(articulo)
                elif articulo.get.tercil() == 2:
                    articulos_n2.append(articulo)
            if articulos_n1 and articulos_n2 and (len(articulos_n1) + len(articulos_n2)) >= (num_n1_n2*(porcentaje_min/100)):
                result = True
                calificacion_investigacion = 'A'
                return result, calificacion_investigacion, articulos_n1, articulos_n2
        return result, calificacion_investigacion, articulos_n1, articulos_n2

    def get_criterio_catedra_B_C_D(self, produccion_cientifica: list, num_publicaciones: int, num_n1: int, num_n2: int, porcentaje_min: int) -> tuple([bool, str, [], []]):
        """
        Método para la evaluación del criterio que hay que superar para la obtención de una cátedra por parte del investigador.

        :param [] produccion_cientifica: Lista de producción científica de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones necesarias de nivel 1 (cuartiles 1 y 2) y nivel 2 (cuartiles 3 y 4).
        :param int porcentaje_min: Tanto por ciento mínimo necesario para determinar el critero de la cátedra de evaluación A a B.
        :return Tupla compuesta por un booleano que nos indica si es positiva la evaluación, un str con el típo de calificación en investigación y dos listas con los artículos de nivel 1 y nivel 2 presentados.        
        """
        articulos_n1 = []
        articulos_n2 = []
        calificacion_investigacion = ''
        result = False
        if len(produccion_cientifica) >= num_publicaciones:
            for articulo in produccion_cientifica:
                if articulo.get.tercil() == 1:
                    articulos_n1.append(articulo)
                elif articulo.get.tercil() == 2:
                    articulos_n2.append(articulo)
            if articulos_n1 and articulos_n2 and len(articulos_n1) >= num_n1 and len(articulos_n2) >= num_n2:
                result = True
                calificacion_investigacion = 'B'
                return result, calificacion_investigacion, articulos_n1, articulos_n2
        if len(produccion_cientifica) >= (num_publicaciones*(porcentaje_min/100)):
            for articulo in produccion_cientifica:
                if articulo.get.tercil() == 1:
                    articulos_n1.append(articulo)
                elif articulo.get.tercil() == 2:
                    articulos_n2.append(articulo)
            if articulos_n1 and articulos_n2:
                if len(articulos_n1) >= (num_n1*(porcentaje_min/100)) and len(articulos_n2) >= (num_n2*(porcentaje_min/100)):
                    result = True
                    calificacion_investigacion = 'B'
                    return result, calificacion_investigacion, articulos_n1, articulos_n2
                else:
                    result = True
                    calificacion_investigacion = 'C'
                    return result, calificacion_investigacion, articulos_n1, articulos_n2
        result = False
        calificacion_investigacion = 'D'
        return result, calificacion_investigacion, articulos_n1, articulos_n2

    def get_criterio_titularidad_A(self, produccion_cientifica: list, num_publicaciones : int, num_n1_n2 : int, porcentaje_min : int) -> tuple([bool, str, [], []]):
        """
        Método para la evaluación del criterio que hay que superar para la obtención de una titularidad por parte del investigador.

        :param [] produccion_cientifica: Lista de producción científica de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones necesarias de nivel 1 (cuartiles 1 y 2) y nivel 2 (cuartiles 3 y 4).
        :param int porcentaje_min: Tanto por ciento mínimo necesario para determinar el critero de la cátedra de evaluación A a B.
        :return Tupla compuesta por un booleano que nos indica si es positiva la evaluación, un str con el típo de calificación en investigación y dos listas con los artículos de nivel 1 y nivel 2 presentados.
        """
        articulos_n1 = []
        articulos_n2 = []
        calificacion_investigacion = ''
        result = False
        if len(produccion_cientifica) >= num_publicaciones:
            for articulo in produccion_cientifica:
                if articulo.get_tercil() == 1:
                    articulos_n1.append(articulo)
                elif articulo.get_tercil() == 2:
                    articulos_n2.append(articulo)
            if articulos_n1 and articulos_n2 and (len(articulos_n1) + len(articulos_n2)) >= num_n1_n2:
                result = True
                calificacion_investigacion = 'A'
                return result, calificacion_investigacion, articulos_n1, articulos_n2
        if len(produccion_cientifica) >= (num_publicaciones*(porcentaje_min/100)):
            for articulo in produccion_cientifica:
                if articulo.get.tercil() == 1:
                    articulos_n1.append(articulo)
                elif articulo.get_tercil() == 2:
                    articulos_n2.append(articulo)
            if articulos_n1 and articulos_n2 and (len(articulos_n1) + len(articulos_n2)) >= (num_n1_n2*(porcentaje_min/100)):
                result = True
                calificacion_investigacion = 'A'
                return result, calificacion_investigacion, articulos_n1, articulos_n2
        result = False
        calificacion_investigacion = 'D'
        return result, calificacion_investigacion, articulos_n1, articulos_n2

    def get_criterio_titularidad_B_C_D(self, produccion_cientifica: list, num_publicaciones: int, num_n1: int, num_n2: int, porcentaje_min: int) -> tuple([bool, str, [], []]):
        """
        Método para la evaluación del criterio que hay que superar para la obtención de una titularidad por parte del investigador.

        :param [] produccion_cientifica: Lista de producción científica de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones necesarias de nivel 1 (cuartiles 1 y 2) y nivel 2 (cuartiles 3 y 4).
        :param int porcentaje_min: Tanto por ciento mínimo necesario para determinar el critero de la cátedra de evaluación A a B.
        :return Tupla compuesta por un booleano que nos indica si es positiva la evaluación, un str con el típo de calificación en investigación y dos listas con los artículos de nivel 1 y nivel 2 presentados.        
        """
        articulos_n1 = []
        articulos_n2 = []
        calificacion_investigacion = ''
        result = False
        if len(produccion_cientifica) >= num_publicaciones:
            for articulo in produccion_cientifica:
                if articulo.get.tercil() == 1:
                    articulos_n1.append(articulo)
                elif articulo.get_tercil() == 2:
                    articulos_n2.append(articulo)
            if articulos_n1 and articulos_n2 and len(articulos_n1) >= num_n1 and len(articulos_n2) >= num_n2:
                result = True
                calificacion_investigacion = 'B'
                return result, calificacion_investigacion, articulos_n1, articulos_n2
        if len(produccion_cientifica) >= (num_publicaciones*(porcentaje_min/100)):
            for articulo in produccion_cientifica:
                if articulo.get.tercil() == 1:
                    articulos_n1.append(articulo)
                elif articulo.get_tercil() == 2:
                    articulos_n2.append(articulo)
            if articulos_n1 and articulos_n2:
                if len(articulos_n1) >= (num_n1*(porcentaje_min/100)) and len(articulos_n2) >= (num_n2*(porcentaje_min/100)):
                    result = True
                    calificacion_investigacion = 'B'
                    return result, calificacion_investigacion, articulos_n1, articulos_n2
                else:
                    result = True
                    calificacion_investigacion = 'C'
                    return result, calificacion_investigacion, articulos_n1, articulos_n2     
        return result, calificacion_investigacion, articulos_n1, articulos_n2

    def create_observaciones_catedra(self, evaluacion: EvaluacionAcreditacionCienciasSociales, produccion_cientifica: list) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la cátedra.

        :param EvaluacionAcreditacionCienciasSociales evaluacion: Objeto EvaluacionAcreditacion de Ciencias Sociales donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :return String con la evaluación de la comisión de Ciencias Sociales.
        """
        return "En el resultado de la valoración para el criterio de la cátedra se ha obtenido un resultado " + "positivo" if evaluacion.positiva else "negativo" + " con una valoración " + evaluacion.valoracion_alcanzada if evaluacion.valoracion_alcanzada != '' else "-" + ".\n Número de publicaciones necesarias " + evaluacion.criterio.num_publicaciones + ". Obtenidas: " + str(len(produccion_cientifica)) + " de las cuales las de nivel 1 hemos obtenido " + str(len(evaluacion.articulos_n1)) + " y de nivel 2 hemos obtenido: " + str(len(evaluacion.articulos_n2)) + "." 

    def create_observaciones_titularidad(self, evaluacion: EvaluacionAcreditacionCienciasSociales, produccion_cientifica: list) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la titularidad.

        :param EvaluacionAcreditacionCienciasSociales evaluacion: Objeto EvaluacionAcreditacion de Ciencias Sociales donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :return String con la evaluación de la comisión de Ciencias Sociales.
        """
        return "En el resultado de la valoración para el criterio de la titularidad se ha obtenido un resultado " + "positivo" if evaluacion.positiva else "negativo" + " con una valoración " + evaluacion.valoracion_alcanzada if evaluacion.valoracion_alcanzada != '' else "-" + ".\n Número de publicaciones necesarias " + evaluacion.criterio.num_publicaciones + ". Obtenidas: " + str(len(produccion_cientifica)) + " de las cuales las de nivel 1 hemos obtenido " + str(len(evaluacion.articulos_n1)) + " y de nivel 2 hemos obtenido: " + str(len(evaluacion.articulos_n2)) + "." 