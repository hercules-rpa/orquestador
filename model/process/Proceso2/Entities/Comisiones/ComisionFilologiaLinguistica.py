from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionFilologiaLinguistica import CriterioAcreditacionFilologiaLinguistica, EvaluacionAcreditacionFilologiaLinguistica
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, CategoriaAcreditacion, TipoAcreditacion
# comisión 21

class ComisionFilologiaLinguistica(Comision):
    """
    La comisión de Filología y Lingüistica se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_evaluacion_acreditacion(self, produccion_cientifica: list, acreditacion: Acreditacion) -> EvaluacionAcreditacionFilologiaLinguistica:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando. Encajar la subcategoría "investigación" o "docencia"
        :return El objeto EvaluacionAcreditación que contiene la evaluación de la acreditación solicitada.
        """
        evaluacion = EvaluacionAcreditacionFilologiaLinguistica(produccion_cientifica=produccion_cientifica, acreditacion=acreditacion)
        if acreditacion.tipo == TipoAcreditacion.CATEDRA:        
            criterios = self.get_criterio_acreditacion(acreditacion.tipo)
            if criterios:
                evaluacion.criterio = CriterioAcreditacionFilologiaLinguistica(criterios['B']['min_publicaciones'], criterios['B']['n1_publicaciones'], criterios['min_porcentaje'])
            else:
                evaluacion.criterio = CriterioAcreditacionFilologiaLinguistica(30,5)
            if acreditacion.categoria == CategoriaAcreditacion.DOCENCIA:
                return self.get_evaluacion_catedra_docencia(produccion_cientifica, evaluacion=evaluacion)
            elif acreditacion.categoria == CategoriaAcreditacion.INVESTIGACION: 
                return self.get_evaluacion_catedra_investigacion(produccion_cientifica, evaluacion=evaluacion)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo)
            if criterios:
                evaluacion.criterio = CriterioAcreditacionFilologiaLinguistica(criterios['B']['min_publicaciones'], criterios['B']['n1_publicaciones'], criterios['min_porcentaje'])
            else:
                evaluacion.criterio = CriterioAcreditacionFilologiaLinguistica(15,6)            
            if acreditacion.categoria == CategoriaAcreditacion.DOCENCIA:
                return self.get_evaluacion_titularidad_docencia(produccion_cientifica, evaluacion=evaluacion)
            elif acreditacion.categoria == CategoriaAcreditacion.INVESTIGACION:
                return self.get_evaluacion_titularidad_investigacion(produccion_cientifica, evaluacion=evaluacion)

    def get_evaluacion_catedra_investigacion(self, produccion_cientifica: list, evaluacion: EvaluacionAcreditacionFilologiaLinguistica) -> EvaluacionAcreditacionFilologiaLinguistica:
        """
        Método para la evaluación de la cátedra de investigación de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Filología y Lingüistica.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Filología y Lingüistica.
        """
        #Lo pongo como una suma ya que los criterios obligatorios
        eval, articulos_t1 = self.criterio_investigacion_catedra(produccion_cientifica, evaluacion.criterio.num_articulos, evaluacion.criterio.num_t1, evaluacion.criterio.min_porcentaje)
        if eval:
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_t1
            evaluacion.observaciones = self.observacion_catedra_investigacion(evaluacion)
        return evaluacion

    def get_evaluacion_catedra_docencia(self, produccion_cientifica: list, evaluacion: EvaluacionAcreditacionFilologiaLinguistica) -> EvaluacionAcreditacionFilologiaLinguistica:
        """
        Método para la evaluación de la cátedra de docencia de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Filología y Lingüistica.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Filología y Lingüistica.
        """
        #Lo pongo como una suma ya que los criterios obligatorios
        eval, articulos_t1 = self.criterio_docencia_catedra(produccion_cientifica,  evaluacion.criterio.num_articulos, evaluacion.criterio.num_t1, evaluacion.criterio.min_porcentaje)
        if eval:
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_t1
            evaluacion.observaciones = self.observacion_catedra_investigacion(evaluacion)
        return evaluacion

    def get_evaluacion_titularidad_investigacion(self, produccion_cientifica: list, evaluacion: EvaluacionAcreditacionFilologiaLinguistica) -> EvaluacionAcreditacionFilologiaLinguistica:
        """
        Método para la evaluación de la cátedra de docencia de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Filología y Lingüistica.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Filología y Lingüistica.
        """
        #Lo pongo como una suma ya que los criterios obligatorios
        eval, articulos_t1 = self.criterio_investigacion_titularidad(produccion_cientifica,  evaluacion.criterio.num_articulos, evaluacion.criterio.num_t1, evaluacion.criterio.min_porcentaje)
        if eval:
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_t1
            evaluacion.observaciones = self.observacion_titularidad_investigacion(evaluacion)
        return evaluacion

    def get_evaluacion_titularidad_docencia(self, produccion_cientifica: list, evaluacion: EvaluacionAcreditacionFilologiaLinguistica) -> EvaluacionAcreditacionFilologiaLinguistica:
        """
        Método para la evaluación de la cátedra de docencia de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Filología y Lingüistica.
        :return El objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Filología y Lingüistica.
        """
        #Lo pongo como una suma ya que los criterios obligatorios
        eval, articulos_t1 = self.criterio_docencia_titularidad(produccion_cientifica,  evaluacion.criterio.num_articulos, evaluacion.criterio.num_t1, evaluacion.criterio.min_porcentaje)
        if eval:
            evaluacion.positiva = eval
            evaluacion.publicaciones_n1 = articulos_t1
            evaluacion.observaciones = self.observacion_titularidad_docencia(evaluacion)
        return evaluacion

    def criterio_investigacion_catedra(self, produccion_cientifica: list, num_publicaciones: int, num_n1: int, porcentaje_min: int) -> tuple([bool, []]):
        """
        Método que define el criterio de una cátedra de investigación.

        :param [] produccion_cientifica: Listado de publicaciones de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1: Número de publicaciones de nivel 1 necesarias para cumplir el criterio.
        :param int porcentaje_min: Porcentaje sobre el total necesario para considerar que el critero esté completo.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones de nivel 1.
        """
        result = False
        publicaciones_n1 = []

        if len(produccion_cientifica) >= num_publicaciones*(porcentaje_min/100):
            for articulo in produccion_cientifica:
                if articulo.get_tercil() == 1:
                    publicaciones_n1.append(articulo)
            if len(publicaciones_n1) >= num_n1*(porcentaje_min/100):
                #Opción 1
                result = True
                return result, publicaciones_n1
            elif len(publicaciones_n1) >= (num_n1*(porcentaje_min/100)):
                #Opción 2
                result = True
                return result, publicaciones_n1
        return result, publicaciones_n1

    def criterio_docencia_catedra(self, produccion_cientifica: list, num_publicaciones: int, num_n1: int, porcentaje_min: int) -> tuple([bool, []]):
        """
        Método que define el criterio de una cátedra de docencia.

        :param [] produccion_cientifica: Listado de publicaciones de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1: Número de publicaciones de nivel 1 necesarias para cumplir el criterio.
        :param int porcentaje_min: Porcentaje sobre el total necesario para considerar que el critero esté completo.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones de nivel 1.
        """
        result = False
        publicaciones_n1 = []
        #Los criterios que se piden aquí no se pueden evaluar, piden experiencia.
        return result, publicaciones_n1

    def observacion_catedra_investigacion(self, evaluacion: EvaluacionAcreditacionFilologiaLinguistica) -> str:
        """
        Método que completa el atributo observación del criterio de la cátedra de investigación.

        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la cátedra de la investigación.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la cátedra de investigación ha resultado ' + str(evaluacion.positiva) + '.\n Se han obtenido ' + str(len(evaluacion.publicaciones_n1)) + ' publicaciones de nivel 1. No se están contando las monografías para esta comisión.'

    def observacion_catedra_docencia(self, evaluacion: EvaluacionAcreditacionFilologiaLinguistica) -> str:
        """
        Método que completa el atributo observación del criterio de la cátedra de docencia.

        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la cátedra de la investigación.
        :return str: Un string con las observaciones para este criterio.
        """
        return ''

    def criterio_investigacion_titularidad(self, produccion_cientifica: list, num_publicaciones: int, num_n1: int, porcentaje_min: int) -> tuple([bool, []]):
        """
        Método que define el criterio de una cátedra de titularidad.

        :param [] produccion_cientifica: Listado de publicaciones de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1: Número de publicaciones de nivel 1 necesarias para cumplir el criterio.
        :param int porcentaje_min: Porcentaje sobre el total necesario para considerar que el critero esté completo.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones de nivel 1.
        """
        result = False
        publicaciones_n1 = []

        if len(produccion_cientifica) >= num_publicaciones*(porcentaje_min/100):
            for articulo in produccion_cientifica:
                if articulo.get_tercil() == 1:
                    publicaciones_n1.append(articulo)
            if len(publicaciones_n1) >= num_n1*(porcentaje_min/100):
                result = True
                return result, publicaciones_n1
        return result, publicaciones_n1
    
    def criterio_docencia_titularidad(self, produccion_cientifica: list, num_publicaciones: int, num_n1: int, porcentaje_min: int) -> tuple([bool, [], []]):
        """
        Método que define el criterio de una titularidad de docencia.

        :param [] produccion_cientifica: Listado de publicaciones de un investigador.
        :param int num_publicaciones: Número de publicaciones necesarias para cumplir el criterio.
        :param int num_n1: Número de publicaciones de nivel 1 necesarias para cumplir el criterio.
        :param int porcentaje_min: Porcentaje sobre el total necesario para considerar que el critero esté completo.
        :return Tupla con el booleano del resultado del criterio y las listas de publicaciones de nivel 1.
        """
        result = False
        publicaciones_n1 = []
        #Los criterios que se piden aquí no se pueden evaluar, piden experiencia.
        return result, publicaciones_n1

    def observacion_titularidad_investigacion(self, evaluacion: EvaluacionAcreditacionFilologiaLinguistica) -> str:
        """
        Método que completa el atributo observación del criterio de la titularidad de investigación.

        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la cátedra de la investigación.
        :return str: Un string con las observaciones para este criterio.
        """
        return 'El resultado de la evaluación del criterio de la titularidad de investigación ha resultado ' + str(evaluacion.positiva) + '.\n Se han obtenido ' + str(len(evaluacion.publicaciones_n1)) + ' publicaciones de nivel 1. No se están contando las monografías para esta comisión.'

    def observacion_titularidad_docencia(self, evaluacion: EvaluacionAcreditacionFilologiaLinguistica) -> str:
        """
        Método que completa el atributo observación del criterio de la titularidad de docencia.

        :param EvaluacionAcreditacionFilologiaLinguistica evaluacion: Objeto EvaluacionAcreditacion con la información necesaria de la evaluación del criterio de la cátedra de la investigación.
        :return str: Un string con las observaciones para este criterio.
        """
        return ''