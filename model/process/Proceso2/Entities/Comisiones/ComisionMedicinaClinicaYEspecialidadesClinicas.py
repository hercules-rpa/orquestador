from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion
from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionMedicinaClinicaYEspecialidades import CriterioEvaluacionMedicinaClinicaYespecialidades, EvaluacionAcreditacionMedicinaClinicaYEspecialidades

#comisión 7

"""
La comisión de Medicina Clínica y Especialidades Clínicas se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
"""

class ComisionMedicinaClinicaYespecialidadesClinicas(Comision):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_evaluacion_acreditacion(self, produccion_cientifica, acreditacion: Acreditacion) -> EvaluacionAcreditacionMedicinaClinicaYEspecialidades:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return objeto EvaluacionAcreditacionMedicinaClinicaYEspecialidades con los resultados del criterio de la comisión de Medicina clinica y Especialidades clinicas.
        """
        #TODO: El número de publicaciones, num_t1, num_autoria y num:_autoria_t1 vendrán dados por el archivo de configuración
        evaluacion = EvaluacionAcreditacionMedicinaClinicaYEspecialidades(produccion_cientifica=produccion_cientifica, acreditacion=acreditacion)

        if acreditacion.tipo == TipoAcreditacion.CATEDRA:
            self.set_criterio_evaluacion(evaluacion)
            return self.get_evaluacion_catedra(produccion_cientifica, evaluacion=evaluacion)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            self.set_criterio_evaluacion(evaluacion)
            return self.get_evaluacion_titularidad(produccion_cientifica, evaluacion=evaluacion)
        
    def set_criterio_evaluacion(self, evaluacion:EvaluacionAcreditacionMedicinaClinicaYEspecialidades):
        """
        Método que hidrata el criterio a la propiedad criterio de la evaluación.
        :param evaluación sobre la que se hidratará el criterio
        :param valoración valoración que se utilizará para obtener los parámetros 
        """
        if evaluacion:
            conf = self.get_criterio_acreditacion(evaluacion.acreditacion.tipo)
            if conf:
                evaluacion.criterio = CriterioEvaluacionMedicinaClinicaYespecialidades(conf['min_publicaciones'],conf['t1_publicaciones'],conf['min_autor'],conf['t1_ap_publicaciones'])

    def get_evaluacion_catedra(self, produccion_cientifica, evaluacion:EvaluacionAcreditacionMedicinaClinicaYEspecialidades) -> EvaluacionAcreditacionMedicinaClinicaYEspecialidades:
        """
        Metodo para la evaluación de la catedra de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param EvaluacionAcreditacionMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Medicina clinica y Especialidades clinicas.
        :return objeto EvaluacionAcreditacionMedicinaClinicaYEspecialidades con los resultados del criterio de la comisión de Medicina clinica y Especialidades clinicas.
        """
        eval, articulos_t1, articulos_t2, articulos_autoria, articulos_autoria_t1 = self.criterio1_T1(produccion_cientifica, evaluacion.criterio.minimo_articulos, evaluacion.criterio.num_t1, evaluacion.criterio.num_autoria, evaluacion.criterio.num_autoria_t1)
        evaluacion.positiva = eval
        evaluacion.articulos_t1 = articulos_t1
        evaluacion.articulos_t2 = articulos_t2
        evaluacion.articulos_autoria = articulos_autoria
        evaluacion.articulos_autoria_t1 = articulos_autoria_t1
        if not eval:
            evaluacion.observaciones = self.create_observaciones_catedra(evaluacion, produccion_cientifica, evaluacion.criterio.minimo_articulos, evaluacion.criterio.num_t1, evaluacion.criterio.num_autoria, evaluacion.criterio.num_autoria_t1)
        return evaluacion

    def get_evaluacion_titularidad(self, produccion_cientifica, evaluacion:EvaluacionAcreditacionMedicinaClinicaYEspecialidades) -> EvaluacionAcreditacionMedicinaClinicaYEspecialidades:
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param EvaluacionAcreditacionMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Medicina clinica y Especialidades clinicas.
        :return objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Medicina clinica y Especialidades clinicas.
        """
        eval, articulos_t1, articulos_t2, articulos_autoria, articulos_autoria_t1 = self.criterio1_T1(produccion_cientifica, evaluacion.criterio.minimo_articulos, evaluacion.criterio.num_t1, evaluacion.criterio.num_autoria, evaluacion.criterio.num_autoria_t1)
        
        evaluacion.positiva = eval
        evaluacion.articulos_t1 = articulos_t1
        evaluacion.articulos_t2 = articulos_t2
        evaluacion.articulos_autoria = articulos_autoria
        evaluacion.articulos_autoria_t1 = articulos_autoria_t1
        if not evaluacion.positiva:
            evaluacion.observaciones = self.create_observaciones_titularidad(evaluacion, produccion_cientifica)
        return evaluacion

    def criterio1_T1(self, produccion_cientifica, num_publicaciones, num_t1, num_autoria, num_autoria_t1) -> tuple([bool, [], [], [], []]):
        """
        Método para comprobar cuántos articulos pertenecen al T1 y al T2, de cuantos tiene la autoría preferente y si cumple con el minimo establecido de artículos.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param int num_publicaciones: número de publicaciones necesarias para cumplir el criterio.
        :param int num_t1: número de publicaciones necesarias en el tercil 1.
        :param int num_autoria: numero de publicaciones con autoría preferente necesarias.
        :param int num_autoria_t1: numero de publicaciones con autoria preferente en el tercil 1 necesarias
        :return tupla formada por un booleano si se cumple el criterio, una lista de articulos en el tercil 1, una lista de articulos en tercil 2, una lista de articulos con autoría preferente y una lista de articulos con autoría preferente en tercil 1.
        """
        articulos_t1 = []
        articulos_t2 = []
        articulos_autoria = []
        articulos_autoria_t1 = []
        result = False
        if len(produccion_cientifica) >= num_publicaciones:
            for articulo in produccion_cientifica:
                if articulo.get_tercil() == 1:
                    articulos_t1.append(articulo)
                
                if articulo.get_tercil() == 1:
                    articulos_t2.append(articulo)
                #TODO revisar condicion autoria
            autoria_result, articulos_autoria = self.criterio_autoria_preferente(produccion_cientifica, num_autoria)
            if autoria_result:
                for art_autoria in articulos_autoria:
                    if art_autoria.get_tercil() == 1:
                        articulos_autoria_t1.append(articulo)
        
            if articulos_t1 and articulos_t2 and articulos_autoria and articulos_autoria_t1 and (len(articulos_t1) + len(articulos_t2)) >= num_publicaciones and len(articulos_t1) >= num_t1 and len(articulos_autoria) >= num_autoria and len(articulos_autoria_t1) >= num_autoria_t1:
                result = True
            else:
                 result = False

        return (result, articulos_t1, articulos_t2, articulos_autoria, articulos_autoria_t1)

    def criterio_autoria_preferente(self, produccion_cientifica, num_publicaciones):
        """
        Método que comprueba el criterio de autoria preferente
        (Primer/a firmante, coautoría, ultimo/a firmante y autor/a de correspondencia).
        """
        publicaciones = []
        result: bool = False
        if produccion_cientifica and len(produccion_cientifica) >= num_publicaciones:
            for art in produccion_cientifica:
                if (len(publicaciones) < num_publicaciones) and (art.posicion_autor == 1 or (art.posicion_autor == art.nautores)):
                    publicaciones.append(art)
        
        if publicaciones and len(publicaciones) == num_publicaciones:
            result = True

        return (result, publicaciones)

    def create_observaciones_catedra(self, evaluacion: EvaluacionAcreditacionMedicinaClinicaYEspecialidades, produccion_cientifica: list, num_publicaciones: int, num_t1: int, num_autoria: int, num_autoria_t1: int) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la cátedra.

        :param EvaluacionAcreditacionMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacion de Otras Especialidades Sanitarias donde almacenamos los datos de la evaluación.
        :param list produccion_cientifica: Lista de publicaciones proporcionadas para la evaluación.
        :return String con la evaluación de la comisión de Otras especialidades Sanitarias.
        """
        return "En el resultado de la valoración para el criterio de la cátedra se ha obtenido un resultado negativo con los siguientes resultados: \n  Número de publicaciones necesarias " + str(evaluacion.criterio.minimo_articulos) + ". Obtenidas: " + str(len(produccion_cientifica)) + ". \n Número de publicaciones necesarias en el tercil 1: " + str(evaluacion.criterio.num_t1) + ". Obtenidas: " + str(len(evaluacion.articulos_t1)) + " \n Número de publicaciones con autoria preferente " + str(evaluacion.criterio.num_autoria) + " Obtenidas: " + str(len(evaluacion.articulos_autoria_t1)) + " Número de publicaciones con autoria preferente en tercil 1 " + str(evaluacion.criterio.num_autoria_t1) + " Obtenidas: " + str(len(evaluacion.articulos_autoria_t1)) + "."

    def create_observaciones_titularidad(self, evaluacion: EvaluacionAcreditacionMedicinaClinicaYEspecialidades, produccion_cientifica: list) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la titularidad.

        :param EvaluacionAcreditacionMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacion de Otras Especialidades Sanitarias donde almacenamos los datos de la evaluación.
        :param list produccion_cientifica: Lista de publicaciones proporcionadas para la evaluación.
        :return String con la evaluación de la comisión de Otras Especialidades Sanitarias.
        """
        return "En el resultado de la valoración para el criterio de la titularidad se ha obtenido un resultado negativo con los siguientes resultados: \n  Número de publicaciones necesarias " + str(evaluacion.criterio.minimo_articulos) + ". Obtenidas: " + str(len(produccion_cientifica)) + ". \n Número de publicaciones necesarias en el tercil 1: " + str(evaluacion.criterio.num_t1) + ". Obtenidas: " + str(len(evaluacion.articulos_t1)) + " \n Número de publicaciones con autoria preferente " + str(evaluacion.criterio.num_autoria) + " Obtenidas: " + str(len(evaluacion.articulos_autoria_t1)) + " Número de publicaciones con autoria preferente en tercil 1 " + str(evaluacion.criterio.num_autoria_t1) + " Obtenidas: " + str(len(evaluacion.articulos_autoria_t1)) + "."
