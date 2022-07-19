from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionCienciasComportamiento import CriterioAcreditacionCienciasComportamiento, EvaluacionAcreditacionCienciasComportamiento
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion

class ComisionCienciasComportamiento(Comision):
    """
    La comisión de Ciencias de la Naturaleza se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_evaluacion_acreditacion(self, produccion_cientifica: list, acreditacion: Acreditacion) -> EvaluacionAcreditacionCienciasComportamiento:
        """
        Método encargado de evaluar la solicitud de acreditación de la comisión de Ciencias del Comportamiento.

        :param [] produccion_cientifica: Lista con las publicaciones del investigador.
        :param Acreditacion acreditacion: Tipo de acreditación a la que está postulando el investigador.
        :return EvaluacionAcreditacionCienciasComportamiento Objeto con el resultado de la evaluación del investigador.
        """
        eval = EvaluacionAcreditacionCienciasComportamiento(produccion_cientifica=produccion_cientifica, acreditacion = acreditacion)
        if acreditacion.tipo == TipoAcreditacion.CATEDRA:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo)
            if criterios:
                eval.criterio = CriterioAcreditacionCienciasComportamiento(criterios['B']['min_publicaciones'],criterios['B2']['min_publicaciones'],criterios['B']['q1q2_articulos'],criterios['B2']['q1q2_articulos'],criterios['B']['q1q2_ap_articulos'],criterios['B2']['q1q2_ap_articulos'],criterios['min_porcentaje'])
            else:
                eval.criterio = CriterioAcreditacionCienciasComportamiento(20,16,10,8,6,5,80)         
            return self.get_evaluacion_catedra(produccion_cientifica, eval)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo)
            if criterios:
                eval.criterio = CriterioAcreditacionCienciasComportamiento(criterios['B']['min_publicaciones'],criterios['B2']['min_publicaciones'],criterios['B']['q1q2_articulos'],criterios['B2']['q1q2_articulos'],criterios['B']['q1q2_ap_articulos'],criterios['B2']['q1q2_ap_articulos'],criterios['min_porcentaje'])
            else:
                eval.criterio = CriterioAcreditacionCienciasComportamiento(10,8,6,5,4,3,80)
            return self.get_evaluacion_titularidad(produccion_cientifica, eval)

    def get_evaluacion_catedra(self, produccion_cientifica:list, evaluacion:EvaluacionAcreditacionCienciasComportamiento) -> EvaluacionAcreditacionCienciasComportamiento:
        """
        Método encargado de evaluar la cátedra de la comisión de Ciencias del Comportamiento.

        :param [] produccion_cientifica: Lista con las publicaciones del investigador.
        :param EvaluacionAcreditacionCienciasComportamiento eval: Tipo de Evaluación a la que está postulando el investigador.
        :return EvaluacionAcreditacionCienciasComportamiento Objeto con el resultado de la evaluación del investigador.
        """
        eval, publicaciones_t1_t2, publicaciones_autoria = self.criterio_catedra(produccion_cientifica, evaluacion.criterio.num_articulos, evaluacion.criterio.num_t1_t2, evaluacion.criterio.num_autoria, evaluacion.criterio.min_porcentaje)
        if eval:
            evaluacion.positiva = eval
            evaluacion.publicaciones_t1_t2 = publicaciones_t1_t2
            evaluacion.publicaciones_autoria = publicaciones_autoria
            evaluacion.observaciones = self.observacion_catedra(evaluacion)
        return evaluacion

    def get_evaluacion_titularidad(self, produccion_cientifica:list, evaluacion:EvaluacionAcreditacionCienciasComportamiento) -> EvaluacionAcreditacionCienciasComportamiento:
        """
        Método encargado de evaluar la titularidad de la comisión de Ciencias del Comportamiento.

        :param [] produccion_cientifica: Lista con las publicaciones del investigador.
        :param EvaluacionAcreditacionCienciasComportamiento eval: Tipo de Evaluación a la que está postulando el investigador.
        :return EvaluacionAcreditacionCienciasComportamiento Objeto con el resultado de la evaluación del investigador.
        """
        eval, publicaciones_t1_t2, publicaciones_autoria  = self.criterio_titularidad(produccion_cientifica,  evaluacion.criterio.num_articulos, evaluacion.criterio.num_t1_t2, evaluacion.criterio.num_autoria, evaluacion.criterio.min_porcentaje)
        if eval:
            evaluacion.positiva = eval
            evaluacion.publicaciones_t1_t2 = publicaciones_t1_t2
            evaluacion.publicaciones_autoria = publicaciones_autoria
            evaluacion.observaciones = self.observacion_catedra(evaluacion)
        return evaluacion

    def criterio_catedra(self, produccion_cientifica: list, num_publicaciones: int, num_t1_t2: int, num_autoria: int, porcentaje: int) -> tuple([bool, [], []]):
        """
        Método que define el criterio de una cátedra para la comisón de Ciencias del Comportamiento.

        :param [] produccion_cientifica: Listado de publicaciones de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones de tercil 1 y 2 mínimas necesarias para cumplir el criterio.
        :param int porcentaje: Número de porcentaje válido para cumplir los méritos.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones tanto de tercil 1 como de tercil 2.
        """
        result = False
        publicaciones_t1 = []
        publicaciones_t2 = []
        publicaciones_autoria = []
        if len(produccion_cientifica) >= num_publicaciones:
            for publicacion in produccion_cientifica:
                if publicacion.get_tercil() == 1:
                    publicaciones_t1.append(publicacion)
                elif publicacion.get_tercil() == 2:
                    publicaciones_t2.append(publicacion)
                elif publicacion.posicion_autor == 1:
                    publicaciones_autoria.append(publicacion)
            if (publicaciones_t1 and publicaciones_t2 and (len(publicaciones_t1) + len(publicaciones_t2)) >= num_t1_t2 and len(publicaciones_autoria) >= num_autoria) or (publicaciones_t1 and publicaciones_t2 and len(publicaciones_autoria) >= num_autoria*(porcentaje/100) and (len(publicaciones_t1) + len(publicaciones_t2))*(porcentaje/100) >= num_t1_t2*(porcentaje)/100):
                result = True
                return result, publicaciones_t1 + publicaciones_t2, publicaciones_autoria
        return result, publicaciones_t1 + publicaciones_t2, publicaciones_autoria

    def criterio_titularidad(self, produccion_cientifica: list, num_publicaciones: int, num_t1_t2: int, num_autoria: int, porcentaje: int) -> tuple([bool, [], []]):
        """
        Método que define el criterio de una titularidad para la comisón de Ciencias del Comportamiento.

        :param [] produccion_cientifica: Listado de publicaciones de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1: Número de publicaciones de tercil 1 mínimas necesarias para cumplir el criterio.
        :param int num_n1_n2: Número de publicaciones de tercil 1 y 2 mínimas necesarias para cumplir el criterio.
        :param int max_anios: Años máximos permitidos por publicación.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones tanto de tercil 1 como de tercil 2.
        """
        result = False
        publicaciones_t1 = []
        publicaciones_t2 = []
        publicaciones_autoria = []
        if len(produccion_cientifica) >= num_publicaciones:
            for publicacion in produccion_cientifica:
                if publicacion.get_tercil() == 1:
                    publicaciones_t1.append(publicacion)
                elif publicacion.get_tercil() == 2:
                    publicaciones_t2.append(publicacion)
                elif publicacion.posicion_autor == 1:
                    publicaciones_autoria.append(publicacion)
            if (publicaciones_t1 and publicaciones_t2 and (len(publicaciones_t1) + len(publicaciones_t2)) >= num_t1_t2 and len(publicaciones_autoria) >= num_autoria) or (publicaciones_t1 and publicaciones_t2 and len(publicaciones_autoria) >= num_autoria*(porcentaje/100) and (len(publicaciones_t1) + len(publicaciones_t2))*(porcentaje/100) >= num_t1_t2*(porcentaje/100)):
                result = True
                return result, publicaciones_t1 + publicaciones_t2, publicaciones_autoria
        return result, publicaciones_t1 + publicaciones_t2, publicaciones_autoria

    def observacion_catedra(self, evaluacion: EvaluacionAcreditacionCienciasComportamiento) -> str:
        """
        Método que completa el atributo observación del criterio de la cátedra para la comisión Ciencias del Comportamiento.

        :param EvaluacionAcreditacionCienciasComportamiento evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la cátedra.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la cátedra para la comisión de Ciencias del Comportamiento ha resultado ' + str(evaluacion.positiva) + '.\n Se han obtenido ' + str(len(evaluacion.publicaciones_t1_t2)) + ' publicaciones de nivel 1 y publicaciones de nivel 2.'

    def observacion_titularidad(self, evaluacion: EvaluacionAcreditacionCienciasComportamiento) -> str:
        """
        Método que completa el atributo observación del criterio de la titularidad para la comisión Ciencias del Comportamiento.

        :param EvaluacionAcreditacionCienciasComportamiento evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la titularidad.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la cátedra para la comisión de Ciencias del Comportamiento ha resultado ' + str(evaluacion.positiva) + '.\n Se han obtenido ' + str(len(evaluacion.publicaciones_t1_t2)) + ' publicaciones de nivel 1 y publicaciones de nivel 2.'
