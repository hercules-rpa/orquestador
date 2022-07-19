from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionFisica import EvaluacionAcreditacionFisica
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionQuimica import CriterioEvaluacionQuimica, EvaluacionAcreditacionQuimica

import datetime
# comisión 3

class ComisionQuimica(Comision):
    """
    La comisión de Química se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
    """
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)

    def get_evaluacion_acreditacion(self, produccion_cientifica, acreditacion: Acreditacion) -> EvaluacionAcreditacionQuimica:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return El objeto EvaluacionAcreditación que contiene la evaluación de la acreditación solicitada.
        """
        evaluacion = EvaluacionAcreditacionQuimica(produccion_cientifica=produccion_cientifica, acreditacion=acreditacion)
        if acreditacion.tipo == TipoAcreditacion.CATEDRA:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo, evaluacion)
            if criterios:
                evaluacion.criterio = CriterioEvaluacionQuimica(criterios['min_publicaciones'],criterios['t1_publicaciones'], criterios['t1_ap_publicaciones'], criterios['max_anyo'])
            else:
                evaluacion.criterio = CriterioEvaluacionQuimica(50,25,4,15)
            return self.get_evaluacion_catedra(produccion_cientifica, evaluacion=evaluacion)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            criterios = self.get_criterio_acreditacion(acreditacion.tipo, evaluacion)
            if criterios:
                evaluacion.criterio = CriterioEvaluacionQuimica(criterios['min_publicaciones'],criterios['t1_publicaciones'], criterios['t1_ap_publicaciones'], criterios['max_anyo'])
            else:
                evaluacion.criterio = CriterioEvaluacionQuimica(40,15,4,10)
            return self.get_evaluacion_titularidad(produccion_cientifica, evaluacion)

    def get_evaluacion_catedra(self, produccion_cientifica, evaluacion: EvaluacionAcreditacionQuimica) -> EvaluacionAcreditacionQuimica:
        """
        Método general de evaluación para la cátedra de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionQuimica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Química.
        :return objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Química.
        """
        eval, articulos_t1, articulos_primero = self.criterio(produccion_cientifica, evaluacion.criterio.min_publicaciones, evaluacion.criterio.t1_publicaciones, evaluacion.criterio.t1_ap_publicaciones, evaluacion.criterio.max_anyo)
        evaluacion.positiva = eval
        evaluacion.articulos_t1 = articulos_t1
        evaluacion.articulos_primero = articulos_primero
        evaluacion.observaciones = self.create_observaciones_critero(evaluacion)
        return evaluacion

    def get_evaluacion_titularidad(self, produccion_cientifica, evaluacion: EvaluacionAcreditacionQuimica) -> EvaluacionAcreditacionQuimica:
        """
        Método general de evaluación para la titularidad de un investigador.

        :param [] produccion_científica: listado de artículos de un investigador.
        :param EvaluacionAcreditacionQuimica evaluacion: Objeto EvaluacionAcreditacion que contiene el resultado del criterio de la comisión de Química.
        :return objeto EvaluacionAcreditacion con los resultados del criterio de la comisión de Química.
        """
        eval, articulos_t1, articulos_primero = self.criterio(produccion_cientifica, evaluacion.criterio.min_publicaciones, evaluacion.criterio.t1_publicaciones, evaluacion.criterio.t1_ap_publicaciones, evaluacion.criterio.max_anyo)
        evaluacion.positiva = eval
        evaluacion.articulos_t1 = articulos_t1
        evaluacion.articulos_primero = articulos_primero
        evaluacion.observaciones = self.create_observaciones_critero(evaluacion)
        return evaluacion

    def criterio(self, produccion_cientifica, num_publicaciones, t1_publicaciones, primer_autor, max_anios) -> tuple([bool, [],  []]):
        """
        Método para comprobar cuántos artículos pertenecen al T1 y si cumple con el mínimo establecido de artículos.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param int num_publicaciones: número de publicaciones necesarias para cumplir el criterio.
        :param int t1_publicaciones: número de publicaciones necesarias en el tercil 1.
        :param int primer_autor: número de publicaciones en las que tienes que ser primer autor.
        :param int max_anios: número máximo de años permitidos en las publicaciones.
        :return dupla formada por un booleano si se cumple con el criterio, una lista de artículos seleccionados en el tercil 1 y una lista de artículos en los que el investigador es primer autor.
        """
        articulos_t1 = []
        articulos_primero = []
        result = False
        primer_autor = 0
        if len(produccion_cientifica) >= num_publicaciones:
            for articulo in produccion_cientifica:
                # Ponemos el atributo posición pero no sé realmente si ese determina la posición en el artículo que estamos consultando.
                if articulo.get_tercil() == 1 and (datetime.date.today().year - int(articulo.get_anio())) <= max_anios and articulo.posicion_autor == 1:
                    articulos_primero.append(articulo)
                    primer_autor += 1
                if articulo.get_tercil() == 1 and (datetime.date.today().year - int(articulo.get_anio())) <= max_anios:
                    articulos_t1.append(articulo)

            if articulos_t1 and articulos_primero and len(articulos_t1) >= num_publicaciones and len(articulos_t1) >= t1_publicaciones and len(articulos_primero) >= primer_autor:
                result = True

        return (result, articulos_t1, articulos_primero)

    def create_observaciones_critero(self, evaluacion:EvaluacionAcreditacionQuimica) -> str:
        """
        Método para rellenar el campo observaciones con el resultado de la evaluación del criterio.

        :param EvaluacionAcreditacionQuimica evaluacion: Objeto EvaluacionAcreditacion de Química donde almacenamos los datos de la evaluación.
        :param int num_publicaciones: Número de publicaciones necesarias para el criterio.
        :param int t1_publicaciones: Número de publicaciones necesarias en el tercil 1 para el criterio.
        :param int primer_autor: Número por el cual el investigador debe ser primer autor en la publicación del artículo.
        :param int max_anios: Número máximo de años que debe tener la publicacion del artículo.
        :return String con la evaluación de la comisión de Física
        """
        return 'En el resultado de la evaluación, los resultados del criterio han sido los siguientes: \n' + 'Número de publicaciones totales necesarias: ' + str(evaluacion.criterio.min_publicaciones) + '. Obtenidas: ' + str(len(evaluacion.produccion_cientifica)) + '.\n Número de publicaciones en el tercil 1 en los últimos ' + str(evaluacion.criterio.max_anyo) + ' años: ' + str(evaluacion.criterio.t1_publicaciones) + '. Obtenidos: ' + str(len(evaluacion.articulos_t1)) + ', de los cuales se necesita ser primer autor en ' + str(evaluacion.criterio.t1_ap_publicaciones) + ' de ellos, obtenidos: ' + str(len(evaluacion.articulos_primero)) + '.'