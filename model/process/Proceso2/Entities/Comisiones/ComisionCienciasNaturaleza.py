from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionCienciasNaturaleza import CriterioAcreditacionCienciasNaturaleza, EvaluacionAcreditacionCienciasNaturaleza
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion

import datetime

class ComisionCienciasNaturaleza(Comision):
    """
    La comisión de Ciencias de la Naturaleza se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_evaluacion_acreditacion(self, produccion_cientifica: list, acreditacion: Acreditacion) -> EvaluacionAcreditacionCienciasNaturaleza:
        """
        Método encargado de evaluar la solicitud de acreditación de la comisión de Ciencias de la Naturaleza.

        :param [] produccion_cientifica: Lista con las publicaciones del investigador.
        :param Acreditacion acreditacion: Tipo de acreditación a la que está postulando el investigador.
        :return EvaluacionACreditacionCienciasNaturaleza Objeto con el resultado de la evaluación del investigador.
        """
        evaluacion = EvaluacionAcreditacionCienciasNaturaleza(produccion_cientifica=produccion_cientifica, acreditacion = acreditacion)
        if acreditacion.tipo == TipoAcreditacion.CATEDRA:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo,'B')
            if criterios:
                evaluacion.criterio = CriterioAcreditacionCienciasNaturaleza(criterios['num_publicaciones'], criterios['min_publicaciones'], criterios['t1_publicaciones'], criterios['min_t1_publicaciones'], criterios['t1_t2publicaciones'], criterios['min_t1_t2publicaciones'], criterios['autoria_preferente'], criterios['max_anyo'])
            else:
                evaluacion.criterio = CriterioAcreditacionCienciasNaturaleza(40,30,10,8,25,19,10,10)            
            return self.get_evaluacion_catedra(produccion_cientifica, evaluacion)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo,'B')
            if criterios:
                evaluacion.criterio = CriterioAcreditacionCienciasNaturaleza(criterios['num_publicaciones'], criterios['min_publicaciones'], criterios['t1_publicaciones'], criterios['min_t1_publicaciones'], criterios['t1_t2publicaciones'], criterios['min_t1_t2publicaciones'], criterios['autoria_preferente'], criterios['max_anyo'])
            else:
                evaluacion.criterio = CriterioAcreditacionCienciasNaturaleza(15,11,5,4,10,8,3,10)
            return self.get_evaluacion_titularidad(produccion_cientifica, evaluacion)

    def get_evaluacion_catedra(self, produccion_cientifica:list, evaluacion:EvaluacionAcreditacionCienciasNaturaleza) -> EvaluacionAcreditacionCienciasNaturaleza:
        """
        Método encargado de evaluar la cátedra de la comisión de Ciencias de la Naturaleza.

        :param [] produccion_cientifica: Lista con las publicaciones del investigador.
        :param EvaluacionACreditacionCienciasNaturaleza eval: Tipo de Evaluación a la que está postulando el investigador.
        :return EvaluacionACreditacionCienciasNaturaleza Objeto con el resultado de la evaluación del investigador.
        """
        eval, publicaciones_t1, publicaciones_t2, publicaciones_autor = self.criterio_catedra(produccion_cientifica, evaluacion.criterio.num_articulos, evaluacion.criterio.minimo_articulos, evaluacion.criterio.num_t1, evaluacion.criterio.min_t1, evaluacion.criterio.num_t1_t2, evaluacion.criterio.min_t1_t2, evaluacion.criterio.num_autor, evaluacion.criterio.min_anios)
        if eval:
            evaluacion.positiva = eval
            evaluacion.publicaciones_t1 = publicaciones_t1
            evaluacion.publicaciones_t2 = publicaciones_t2
            evaluacion.publicaciones_autor = publicaciones_autor
            evaluacion.observaciones = self.observacion_catedra(evaluacion)
        return evaluacion

    def get_evaluacion_titularidad(self, produccion_cientifica:list, evaluacion:EvaluacionAcreditacionCienciasNaturaleza) -> EvaluacionAcreditacionCienciasNaturaleza:
        """
        Método encargado de evaluar la titularidad de la comisión de Ciencias de la Naturaleza.

        :param [] produccion_cientifica: Lista con las publicaciones del investigador.
        :param EvaluacionACreditacionCienciasNaturaleza eval: Tipo de Evaluación a la que está postulando el investigador.
        :return EvaluacionACreditacionCienciasNaturaleza Objeto con el resultado de la evaluación del investigador.
        """
        eval, publicaciones_t1, publicaciones_t2, publicaciones_autor = self.criterio_titularidad(produccion_cientifica, evaluacion.criterio.num_articulos, evaluacion.criterio.minimo_articulos, evaluacion.criterio.num_t1, evaluacion.criterio.min_t1, evaluacion.criterio.num_t1_t2, evaluacion.criterio.min_t1_t2, evaluacion.criterio.num_autor, evaluacion.criterio.min_anios)
        if eval:
            evaluacion.positiva = eval
            evaluacion.publicaciones_t1 = publicaciones_t1
            evaluacion.publicaciones_t2 = publicaciones_t2
            evaluacion.publicaciones_autor = publicaciones_autor
            evaluacion.observaciones = self.observacion_titularidad(evaluacion)
        return evaluacion

    def criterio_catedra(self, produccion_cientifica: list, num_publicaciones: int, min_publicaciones: int, num_t1: int, min_t1: int, num_t1_t2: int, min_t1_t2: int, autor: int, max_anios: int) -> tuple([bool, [], [], []]):
        """
        Método que define el criterio de una cátedra para la comisón de Ciencias de la Naturaleza.

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
        publicaciones_autor = []
        if len(produccion_cientifica) >= min_publicaciones:
            for publicacion in produccion_cientifica:
                if publicacion.get_tercil() == 1 and (datetime.date.today().year - int(publicacion.get_anio())) >= max_anios:
                    if publicacion.posicion_autor == 1:
                        publicaciones_autor.append(publicacion)
                    publicaciones_t1.append(publicacion)
                elif publicacion.get_tercil() == 2 and (datetime.date.today().year - int(publicacion.get_anio())) >= max_anios:
                    if publicacion.posicion_autor == 1:
                        publicaciones_autor.append(publicacion)
                    publicaciones_t2.append(publicacion)
            if publicaciones_t1 and publicaciones_t2 and (len(publicaciones_t1) + len(publicaciones_t2)) >= num_publicaciones and (len(publicaciones_t1) + len(publicaciones_t2)) >= num_t1_t2 or len(publicaciones_t1) >= num_t1 :
                result = True
                return result, publicaciones_t1, publicaciones_t2, publicaciones_autor
            elif publicaciones_t1 and publicaciones_t2 and (len(publicaciones_t1) + len(publicaciones_t2)) >= min_publicaciones and len(publicaciones_autor) >= autor and ((len(publicaciones_t1) + len(publicaciones_t2)) >= min_t1_t2 or len(publicaciones_t1) >= min_t1):
                result = True
                return result, publicaciones_t1, publicaciones_t2, publicaciones_autor
        return result, publicaciones_t1, publicaciones_t2, publicaciones_autor

    def criterio_titularidad(self, produccion_cientifica: list, num_publicaciones: int, min_publicaciones: int, num_t1: int, min_t1: int, num_t1_t2: int, min_t1_t2: int, autor: int, max_anios: int) -> tuple([bool, [], [], []]):
        """
        Método que define el criterio de una titularidad para la comisón de Ciencias de la Naturaleza.

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
        publicaciones_autor = []
        if len(produccion_cientifica) >= min_publicaciones:
            for publicacion in produccion_cientifica:
                if publicacion.get_tercil() == 1 and (datetime.date.today().year - int(publicacion.get_anio())) >= max_anios:
                    if publicacion.posicion_autor == 1:
                        publicaciones_autor.append(publicacion)
                    publicaciones_t1.append(publicacion)
                elif publicacion.get_tercil() == 2 and (datetime.date.today().year - int(publicacion.get_anio())) >= max_anios:
                    if publicacion.posicion_autor == 1:
                        publicaciones_autor.append(publicacion)
                    publicaciones_t2.append(publicacion)
            if publicaciones_t1 and publicaciones_t2 and (len(publicaciones_t1) + len(publicaciones_t2)) >= num_publicaciones and len(publicaciones_autor) >= autor and (len(publicaciones_t1) + len(publicaciones_t2)) >= num_t1_t2 or len(publicaciones_t1) >= num_t1:
                result = True
                return result, publicaciones_t1, publicaciones_t2, publicaciones_autor
            elif publicaciones_t1 and publicaciones_t2 and (len(publicaciones_t1) + len(publicaciones_t2)) >= min_publicaciones and len(publicaciones_autor) >= autor and ((len(publicaciones_t1) + len(publicaciones_t2)) >= min_t1_t2 or len(publicaciones_t1) >= min_t1):
                result = True
                return result, publicaciones_t1, publicaciones_t2, publicaciones_autor
        return result, publicaciones_t1, publicaciones_t2, publicaciones_autor

    def observacion_catedra(self, evaluacion: EvaluacionAcreditacionCienciasNaturaleza) -> str:
        """
        Método que completa el atributo observación del criterio de la cátedra para la comisión Ciencias de la Naturaleza.

        :param EvaluacionAcreditacionCienciasNaturaleza evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la cátedra.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la cátedra para la comisión de Ciencias de la Naturaleza ha resultado ' + str(evaluacion.positiva) + '.\n Se han obtenido ' + str(len(evaluacion.publicaciones_t1)) + ' publicaciones de nivel 1 y ' + str(len(evaluacion.publicaciones_t2)) + ' publicaciones de nivel 2.'

    def observacion_titularidad(self, evaluacion: EvaluacionAcreditacionCienciasNaturaleza) -> str:
        """
        Método que completa el atributo observación del criterio de la titularidad para la comisión Ciencias de la Naturaleza.

        :param EvaluacionAcreditacionCienciasNaturaleza evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la titularidad.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la cátedra para la comisión de Ciencias de la Naturaleza ha resultado ' + str(evaluacion.positiva) + '.\n Se han obtenido ' + str(len(evaluacion.publicaciones_t1)) + ' publicaciones de nivel 1 y ' + str(len(evaluacion.publicaciones_t2)) + ' publicaciones de nivel 2.'
