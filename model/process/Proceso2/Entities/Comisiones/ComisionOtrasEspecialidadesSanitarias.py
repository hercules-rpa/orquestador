from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion
from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionOtrasEspecialidadesSanitairas import CriterioEvaluacionOtrasEspecialidadesSanitarias, EvaluacionAcreditacionOtrasEspecialidadesSanitarias


class ComisionOtrasEspecialidadesSanitarias(Comision):
    def get_evaluacion_acreditacion(self, produccion_cientifica, acreditacion: Acreditacion) -> EvaluacionAcreditacionOtrasEspecialidadesSanitarias:

        evaluacion = EvaluacionAcreditacionOtrasEspecialidadesSanitarias(produccion_cientifica=produccion_cientifica, acreditacion=acreditacion)
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return El objeto EvaluacionAcreditación que contiene la evaluación de la acreditación solicitada.
        """
        if acreditacion.tipo == TipoAcreditacion.CATEDRA:
            return self.get_evaluacion_catedra(produccion_cientifica, evaluacion=evaluacion)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            return self.get_evaluacion_titularidad(produccion_cientifica, evaluacion=evaluacion)

    def set_criterio_evaluacion(self, evaluacion:EvaluacionAcreditacionOtrasEspecialidadesSanitarias, valoracion:str=''):
        """
        Método que hidrata el criterio a la propiedad criterio de la evaluación.
        :param evaluación sobre la que se hidratará el criterio
        :param valoración valoración que se utilizará para obtener los parámetros 
        """
        if evaluacion:
            conf = self.get_criterio_acreditacion(evaluacion.acreditacion.tipo, valoracion)
            if conf:
                evaluacion.criterio = CriterioEvaluacionOtrasEspecialidadesSanitarias(conf['min_publicaciones'],conf['n_autoria_preferente'],conf['t1_ap_publicaciones'])

    def get_evaluacion_catedra(self, produccion_cientifica, evaluacion:EvaluacionAcreditacionOtrasEspecialidadesSanitarias) -> EvaluacionAcreditacionOtrasEspecialidadesSanitarias:
        """
        Método para la evaluación de la cátedra de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionOtrasEspecialidadesSanitarias evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Otras Especialidades Sanitarias.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Otras Especialidades Sanitarias.
        """
        self.set_criterio_evaluacion(evaluacion,"A")
        eval, valoracion_alcanzada, articulos_autoria, articulos_autoria_t1 = self.get_criterio_1(produccion_cientifica, evaluacion.criterio, "A")
        if eval and valoracion_alcanzada == 'A':
            evaluacion.positiva = eval
            evaluacion.articulos_autoria = articulos_autoria
            evaluacion.articulos_autoria_t1 = articulos_autoria_t1
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            return evaluacion

        self.set_criterio_evaluacion(evaluacion,"B")
        eval, valoracion_alcanzada, articulos_autoria, articulos_autoria_t1 = self.get_criterio_1(produccion_cientifica, evaluacion.criterio,"B")
        if eval and valoracion_alcanzada == 'B':
            evaluacion.positiva = eval
            evaluacion.articulos_autoria = articulos_autoria
            evaluacion.articulos_autoria_t1 = articulos_autoria_t1
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observacion(evaluacion, "A")
            return evaluacion

        self.set_criterio_evaluacion(evaluacion,"C")
        eval, valoracion_alcanzada, articulos_autoria, articulos_autoria_t1 = self.get_criterio_1(produccion_cientifica, evaluacion.criterio, "C")
        if eval and valoracion_alcanzada == 'C':
            evaluacion.positiva = eval
            evaluacion.articulos_autoria = articulos_autoria
            evaluacion.articulos_autoria_t1 = articulos_autoria_t1
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observacion(evaluacion, "B")
            return evaluacion
        
        if eval and valoracion_alcanzada == 'D':
            evaluacion.positiva = eval
            evaluacion.articulos_autoria = articulos_autoria
            evaluacion.articulos_autoria_t1 = articulos_autoria_t1
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observacion(evaluacion, "C")
            return evaluacion

    def get_evaluacion_titularidad(self, produccion_cientifica, evaluacion:EvaluacionAcreditacionOtrasEspecialidadesSanitarias) -> EvaluacionAcreditacionOtrasEspecialidadesSanitarias:
        """
        Método para la evaluación de la titularidad de un investigador

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionOtrasEspecialidadesSanitarias evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Otras Especialidades Sanitarias.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Otras Especialidades Sanitarias.
        """
        self.set_criterio_evaluacion(evaluacion,"A")
        eval, valoracion_alcanzada, articulos_autoria, articulos_autoria_t1 = self.get_criterio_1(produccion_cientifica, evaluacion.criterio, "A")
        if eval and valoracion_alcanzada == 'A':
            evaluacion.positiva = eval
            evaluacion.articulos_autoria = articulos_autoria
            evaluacion.articulos_autoria_t1 = articulos_autoria_t1
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            return evaluacion

        self.set_criterio_evaluacion(evaluacion,"B")
        eval, valoracion_alcanzada, articulos_autoria, articulos_autoria_t1 = self.get_criterio_1(produccion_cientifica, evaluacion.criterio,"B")
        if eval and valoracion_alcanzada == 'B':
            evaluacion.positiva = eval
            evaluacion.articulos_autoria = articulos_autoria
            evaluacion.articulos_autoria_t1 = articulos_autoria_t1
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observacion(evaluacion, "A")
            return evaluacion

        self.set_criterio_evaluacion(evaluacion,"C")
        eval, valoracion_alcanzada, articulos_autoria, articulos_autoria_t1 = self.get_criterio_1(produccion_cientifica, evaluacion.criterio, "C")
        if eval and valoracion_alcanzada == 'C':
            evaluacion.positiva = eval
            evaluacion.articulos_autoria = articulos_autoria
            evaluacion.articulos_autoria_t1 = articulos_autoria_t1
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observacion(evaluacion, "B")
            return evaluacion
        
        if eval and valoracion_alcanzada == 'D':
            evaluacion.positiva = eval
            evaluacion.articulos_autoria = articulos_autoria
            evaluacion.articulos_autoria_t1 = articulos_autoria_t1
            evaluacion.valoracion_alcanzada = valoracion_alcanzada
            evaluacion.observaciones = self.create_observacion(evaluacion, "C")
            return evaluacion

    def get_criterio_1(self, produccion_cientifica: list, criterio: CriterioEvaluacionOtrasEspecialidadesSanitarias, calificacion: str) -> tuple([bool, str, [], []]):
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param [] produccion_cientifica listado de artículos de un investigador.
        :param CriterioEvaluacionOtrasEspecialidadesSanitarias criterio clase que almacena los numeros necesarios para superar el criterio de evaluacion
        :param str calificacion calificacion con la que se valora el criterio en caso de superarlo
        :return tupla formada por un booleano si se cumple alguno de los criterios, una cadena de texto con la calificación de la investigacion, una lista de articulos con autoria preferente y una lista de articulos con autoria preferente en tercil 1
        """
        #TODO El numero de publicaciones, numero de articulos con autoria preferente y numero de articulos con autoria preferente en tercil 1 ventrán dados por el archivo de configuración
        articulos_autoria = []
        articulos_autoria_t1 = []
        calificacion_investigacion = ''
        result = False
        if len(produccion_cientifica) >= criterio.minimo_articulos:
            autoria_result, articulos_autoria = self.criterio_autoria_preferente(produccion_cientifica, criterio.num_autoria)
            if autoria_result:
                for articulo in articulos_autoria:
                    if articulo.get_tercil() == 1:
                        articulos_autoria_t1.append(articulo)
                if len(articulos_autoria_t1) >= criterio.num_autoria_t1:
                    calificacion_investigacion = calificacion
                    result = True
                    return result, calificacion_investigacion, articulos_autoria, articulos_autoria_t1
        calificacion_investigacion = 'D'
        return result, calificacion_investigacion, articulos_autoria, articulos_autoria_t1

    def criterio_autoria_preferente(self, produccion_cientifica, num_publicaciones):
        """
        Método que comprueba el criterio de autoria preferente
        (Primer/a firmante, coautoría, ultimo/a firmante y autor/a de correspondencia).
        """
        publicaciones = []
        result: bool = False
        print(num_publicaciones)
        if produccion_cientifica and len(produccion_cientifica) >= num_publicaciones:
            for art in produccion_cientifica:
                if (len(publicaciones) < num_publicaciones) and (art.posicion_autor == 1 or (art.posicion_autor == art.nautores)):
                    publicaciones.append(art)
        if publicaciones and len(publicaciones) == num_publicaciones:
            result = True

        return (result, publicaciones)

    def create_observacion(self, eval: EvaluacionAcreditacionOtrasEspecialidadesSanitarias, 
        valoracion:str) -> str:
        """
        Método que construye el mensaje que se mostrará si no se cumplen los criterios para
        la valoración 
        """

        num_publicaciones = eval.criterio.minimo_articulos
        num_autoria = eval.criterio.num_autoria
        num_autoria_t1 = eval.criterio.num_autoria_t1
        
        observacion = 'Es posible que no alcance la valoración ' + valoracion+ ' porque se han obtenido los siguientes resultados: \n' + \
            'Número de publicaciones obtenidas necesarias: ' + str(num_publicaciones) + ' obtenidas: ' + str(len(eval.produccion_cientifica)) + '\n' 
        observacion += 'Autoría preferente, necesarias: ' + \
            str(num_autoria) + ' obtenidas: '
        if eval.articulos_autoria:
            observacion += str(len(eval.articulos_autoria)) + '\n'
        else:
            observacion += '0 \n'
        observacion += 'Autoría preferente en T1, necesarias: ' + \
            str(num_autoria_t1) + ' obtenidas: '
        if eval.articulos_autoria_t1:
            observacion += str(len(eval.articulos_autoria_t1)) + '\n'
        else:
            observacion += '0 \n'


        return observacion