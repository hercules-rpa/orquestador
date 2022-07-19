from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionFisica import CriterioEvaluacionFisica, EvaluacionAcreditacionFisica
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion
# comisión 2

class ComisionFisica(Comision):
    """
    La comisión de Física se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_evaluacion_acreditacion(self, produccion_cientifica, acreditacion: Acreditacion) -> EvaluacionAcreditacionFisica:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return El objeto EvaluacionAcreditación que contiene la evaluación de la acreditación solicitada.
        """
        evaluacion = EvaluacionAcreditacionFisica(produccion_cientifica, acreditacion)
        if acreditacion.tipo == TipoAcreditacion.CATEDRA:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo)
            if criterios:
                evaluacion.criterio = CriterioEvaluacionFisica(criterios['O1']['min_publicaciones'],criterios['O1']['t1_publicaciones'],criterios['O2']['t1t2_publicaciones'],criterios['O3']['t1_publicaciones'])
            else:
                evaluacion.criterio = CriterioEvaluacionFisica(50,30,50,38)
            return self.get_evaluacion_catedra(produccion_cientifica, evaluacion=evaluacion)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo)
            if criterios:
                evaluacion.criterio = CriterioEvaluacionFisica(criterios['O1']['min_publicaciones'],criterios['O1']['t1_publicaciones'],criterios['O2']['t1t2_publicaciones'],criterios['O3']['t1_publicaciones'])
            else:
                evaluacion.criterio = CriterioEvaluacionFisica(22,14,22,17)
            return self.get_evaluacion_titularidad(produccion_cientifica, evaluacion=evaluacion)

    def get_evaluacion_catedra(self, produccion_cientifica, evaluacion:EvaluacionAcreditacionFisica) -> EvaluacionAcreditacionFisica:
        """
        Método para la evaluación de la titularidad de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFisica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Física.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Física.
        """

        eval, articulos_t1, articulos_t2 = self.criterio1_T1(produccion_cientifica, evaluacion.criterio.minimo_articulos, evaluacion.criterio.num_t1)
        if eval:
            evaluacion.positiva = eval
            evaluacion.articulos_t1 = articulos_t1
            evaluacion.articulos_t2 = articulos_t2
            evaluacion.observaciones = self.create_observacion_critero_1(evaluacion)
            return evaluacion
        eval, articulos_t1, articulos_t2 = self.criterio2_T1_T2(produccion_cientifica, evaluacion.criterio.minimo_articulos, evaluacion.criterio.num_t1_t2)
        if eval:
            evaluacion.positiva = eval
            evaluacion.articulos_t1 = articulos_t1
            evaluacion.articulos_t2 = articulos_t2
            evaluacion.observaciones = self.create_observacion_critero_2(evaluacion)     
            return evaluacion
        eval, articulos_t1, articulos_t2 = self.criterio3_T1(produccion_cientifica, evaluacion.criterio.min_t1, evaluacion.criterio.min_t1)
        if eval:
            evaluacion.positiva = eval
            evaluacion.articulos_t1 = articulos_t1
            evaluacion.articulos_t2 = articulos_t2
            evaluacion.observaciones = self.create_observacion_critero_3(evaluacion)         
        return evaluacion

    def get_evaluacion_titularidad(self, produccion_cientifica, evaluacion:EvaluacionAcreditacionFisica) -> EvaluacionAcreditacionFisica:
        """
        Método para la evaluación de la titularidad de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFisica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Física.
        :return objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Física.
        """
        #TODO: El número de publicaciones, num_t1 y num_t1_t2 vendrán dados por el archivo de configuración
        eval, articulos_t1, articulos_t2 = self.criterio1_T1(produccion_cientifica, evaluacion.criterio.minimo_articulos, evaluacion.criterio.num_t1)
        if eval:
            evaluacion.positiva = eval
            evaluacion.articulos_t1 = articulos_t1
            evaluacion.articulos_t2 = articulos_t2
            evaluacion.observaciones = self.create_observacion_critero_1(evaluacion)
            return evaluacion
        
        eval, articulos_t1, articulos_t2 = self.criterio2_T1_T2(produccion_cientifica, evaluacion.criterio.minimo_articulos, evaluacion.criterio.num_t1_t2)
        if eval:
            evaluacion.positiva = eval
            evaluacion.articulos_t1 = articulos_t1
            evaluacion.articulos_t2 = articulos_t2 
            evaluacion.observaciones = self.create_observacion_critero_1(evaluacion)           
            return evaluacion

        eval, articulos_t1, articulos_t2 = self.criterio3_T1(produccion_cientifica, evaluacion.criterio.min_t1, evaluacion.criterio.min_t1)
        if eval:
            evaluacion.positiva = eval
            evaluacion.articulos_t1 = articulos_t1
            evaluacion.articulos_t2 = articulos_t2
            evaluacion.observaciones = self.create_observacion_critero_1(evaluacion)
            return evaluacion
        
        return evaluacion
    
    def criterio1_T1(self, produccion_cientifica, num_publicaciones, num_t1) -> tuple([bool, [], []]):
        """
        Método para comprobar cuántos artículos pertenecen al T1 y si cumple con el mínimo establecido de artículos.
        
        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param int num_publicaciones: número de publicaciones necesarias para cumplir el criterio.
        :param int num_t1: número de publicaciones necesarias en el tercil 1.
        :return dupla formada por un booleano si se cumple con el criterio y una lista de artículos seleccionados
        """
        articulos = []
        result = False
        if len(produccion_cientifica) >= num_publicaciones:
            for articulo in produccion_cientifica:
                if articulo.get_tercil() == 1:
                    articulos.append(articulo)

            if articulos and len(articulos) >= num_t1:
                result = True
                return (result, articulos, [])

        return (result, articulos, [])

    def criterio2_T1_T2(self, produccion_cientifica, num_publicaciones, num_t1_t2) -> tuple([bool, [], []]):
        """
        Método para comprobar cuántos artículos pertenecen al T1 y T2 y si cumple con el mínimo establecido de artículos.

        :param [] producción_científica: listado de artículos de un investigador.
        :param int num_publicaciones: número de publicaciones necesarias para cumplir el criterio.
        :param int num_t1_t2: número de publicaciones necesarias en los terciles 1 y 2.
        :return dupla formada por un booleano si se cumple con el criterio y una lista de artículos seleccionados.
        """

        articulos_t1 = []
        articulos_t2 = []
        result = False
        if len(produccion_cientifica) >= num_publicaciones:
            for articulo in produccion_cientifica:
                if articulo.get_tercil() == 1:
                    articulos_t1.append(articulo)
                elif articulo.get_tercil() == 2:
                    articulos_t2.append(articulo)

            if articulos_t1 and articulos_t2 and (len(articulos_t1) + len(articulos_t2)) >= num_t1_t2:
                result = True
                return (result, articulos_t1, articulos_t2)
        
        return (result, articulos_t1, articulos_t2)

    def criterio3_T1(self, produccion_cientifica, num_publicaciones, num_t1) -> tuple([bool, [], []]):
        """
        Método para comprobar cuantos artículos pertenecen al T1 y si cumple con el mínimo establecido de artículos.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param int num_publicaciones: número de publicaciones necesarias para cumplir el criterio.
        :param int num_t1: número de publicaciones necesarias en el tercil 1.
        :return dupla formada por un booleano si se cumple con el criterio y una lista de artículos seleccionados
        """

        articulos = []
        result = False
        if len(produccion_cientifica) >= num_publicaciones:
            for articulo in produccion_cientifica:
                if articulo.get_tercil() == 1:
                    articulos.append(articulo)

            if articulos and len(articulos) >= num_t1:
                result = True
                return (result, articulos)

        return (result, articulos, [])

    def create_observacion_critero_1(self, evaluacion: EvaluacionAcreditacionFisica) -> str:
        """
        Método para rellenar el campo observaciones con el resultado de la evaluación del criterio 1.

        :param EvaluacionAcreditacionFisica evaluacion: Objeto EvaluacionAcreditacion de Física donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :param int num_t1: Número de publicaciones necesarias en el tercil 1 para el criterio.
        :return String con la evaluación de la comisión de Física
        """
        return 'En el resultado de la valoracion del primer criterio se han obtenido los siguientes resultados: \n' + 'Número de publicaciones totales necesarias: ' + str(evaluacion.criterio.minimo_articulos) + '. Obtenidas: ' + str(len(evaluacion.articulos_t1)+len(evaluacion.articulos_t2)) + '. \n Número de publicaciones necesarias en el tercil 1: ' + str(evaluacion.criterio.num_t1) + '. Obtenidas: ' + str(len(evaluacion.articulos_t1))

    def create_observacion_critero_2(self, evaluacion: EvaluacionAcreditacionFisica) -> str:
        """
        Método para rellenar el campo observaciones con el resultado de la evaluación del critero 2.

        :param EvaluacionAcreditacionFisica evaluacion: Objeto EvaluacionAcreditacion de Física donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :param int num_t1_t2: Número de publicaciones necesarias en el tercil 1 y tercil 2 para el criterio.
        :return String con la evaluación de la comisión de Física
        """
        return 'En el resultado de la valoracion del segundo criterio se han obtenido los siguientes resultados: \n' + 'Número de publicaciones totales necesarias: ' + str(evaluacion.criterio.minimo_articulos) + '. Obtenidas: ' + str(len(evaluacion.articulos_t1)+len(evaluacion.articulos_t2)) + '. \n Número de publicaciones necesarias entre el tercil 1 y el tercil 2: ' + str(evaluacion.criterio.num_t1_t2) + '. Obtenidas: ' + str(len(evaluacion.articulos_t1)+len(evaluacion.articulos_t2))
        
    def create_observacion_critero_3(self, evaluacion: EvaluacionAcreditacionFisica) -> str:
        """
        Método para rellenar el campo observaciones con el resultado de la evaluación del criterio 3.

        :param EvaluacionAcreditacionFisica evaluacion: Objeto EvaluacionAcreditacion de Física donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :param int num_t1: Número de publicaciones necesarias en el tercil 1 para el criterio.
        :return String con la evaluación de la comisión de Física
        """
        return 'En el resultado de la valoracion del tercer criterio se han obtenido los siguientes resultados: \n' + 'Número de publicaciones totales necesarias: ' + str(evaluacion.criterio.min_t1) + '. Obtenidas: ' + str(len(evaluacion.articulos_t1)+len(evaluacion.articulos_t2)) + '. \n Número de publicaciones necesarias en el tercil 1: ' + str(evaluacion.criterio.min_t1) + '. Obtenidas: ' + str(len(evaluacion.articulos_t1))
    