from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionRelevancia import EvaluacionAcreditacionRelevancia, CriterioRelevancia
from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion

class ComisionInformatica(Comision):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
    
    def get_evaluacion_acreditacion(self, produccion_cientifica, acreditacion:Acreditacion):
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return objeto EvaluacionAcreditacionRelevancia con los resultados del criterio de la comisión de las comisiones que tienen como criterio las relevancias de las publicaciones.
        """
        eval:EvaluacionAcreditacionRelevancia = EvaluacionAcreditacionRelevancia(articulos=produccion_cientifica, 
        acreditacion=acreditacion)
        if acreditacion.tipo == TipoAcreditacion.CATEDRA:
            return self.get_evaluacion_catedra(eval)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            return self.get_evaluacion_titularidad(eval)  

    def create_observacion(self, eval:EvaluacionAcreditacionRelevancia, valoracion:str) -> str:
        """
        Método que construye el mensaje que se mostrará si no se cumplen los criterios para
        la valoración indicada como parámetro
        :param EvaluacionAcreditacionRelevancia eval: Evaluación con los resultados obtenidos.
        :param str valoracion: Cadena de texto con la valoracion no alcanzada para generar el mensaje
        :return str: Mensaje generado con los parametros indicados.
        """
        observaciones = 'Es posible que no alcance la valoración ' + valoracion+ ' porque se han obtenido los siguientes resultados: \n' + \
            'Número de publicaciones relevantes necesarias: ' + str(eval.criterio.num_relevantes)
            
        if eval.articulos_relevantes:
            obtenidas = len(eval.articulos_muyrelevantes) + len(eval.articulos_relevantes)
            observaciones += ' obtenidas: ' + str(obtenidas) + '.\n' 
        else:
           observaciones += ' obtenidas: 0. \n'

        eval.observaciones +='Número de publicaciones muy relevantes necesarias: ' + str(eval.criterio.num_muy_relevantes)
        if eval.articulos_muyrelevantes:
            observaciones += ' obtenidas ' + str(len(eval.articulos_muyrelevantes)) + '.\n'
        else:
            observaciones += ' obtenidas: 0. \n'        

        return observaciones  
    
    def get_evaluacion(self, eval:EvaluacionAcreditacionRelevancia, valoracion:str='') -> EvaluacionAcreditacionRelevancia:
        """
        Metodo para la evaluacion de los criterios

        :param EvaluacionAcreditacionRelevancia eval: evaluacion sobre la que se hidratará el criterio.
        :param str valoracion: Cadena de texto con la valoración objetivo de la evaluación.
        :return EvaluacionAcreditacionRelevancia eval: Evalucacion con el resultado de la evaluación.
        """
        if len(eval.produccion_cientifica) >= eval.criterio.num_relevantes:
            arts_relevantes = []
            arts_muy_relevantes = []
            for pc in eval.produccion_cientifica:
                if pc.get_decil() == 1:
                    arts_muy_relevantes.append(pc)
                else: #TODO: revisión
                    arts_relevantes.append(pc)
            
            eval.articulos_muyrelevantes = arts_muy_relevantes
            eval.articulos_relevantes = arts_relevantes

            if len(eval.articulos_muyrelevantes) >= eval.criterio.num_muy_relevantes:
                eval.positiva = True
                eval.valoracion_alcanzada = valoracion
            
            if not eval.positiva:
                eval.observaciones = self.create_observacion(eval)
        return eval

    def get_evaluacion_titularidad(self, produccion_cientifica):
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :return objeto EvaluacionAcreditacionRelevancia con los resultados del criterio de la comisión de las comisiones que tienen como criterio las relevancias de las publicaciones.
        """
        evaluacion:EvaluacionAcreditacionRelevancia = self.get_evaluacion_titularidad_A(produccion_cientifica)
        if not evaluacion.positiva:
            evaluacion = self.get_evaluacion_titularidad_B(produccion_cientifica)
        return evaluacion
    
    def get_evaluacion_catedra(self, produccion_cientifica) -> EvaluacionAcreditacionRelevancia:
        """
        Metodo para la evaluación de la catedra de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :return objeto EvaluacionAcreditacionRelevancia con los resultados del criterio de la comisión de las comisiones que tienen como criterio las relevancias de las publicaciones.
        """
        # suponiendo que prod cientif solo son artículos
        evaluacion:EvaluacionAcreditacionRelevancia = self.get_evaluacion_catedra_A(produccion_cientifica)
        if not evaluacion.positiva:
            evaluacion = self.get_evaluacion_catedra_B(produccion_cientifica)
        return evaluacion

    def set_criterio_evaluacion(self, evaluacion:EvaluacionAcreditacionRelevancia, valoracion:str=''):
        """
        Método que hidrata el criterio a la propiedad criterio de la evaluación.

        :param evaluación sobre la que se hidratará el criterio
        :param valoración valoración que se utilizará para obtener los parámetros 
        """
        if evaluacion:
            conf = self.get_criterio_acreditacion(evaluacion.acreditacion.tipo, valoracion)
            if conf:
                evaluacion.criterio = CriterioRelevancia(conf['n_relevantes'],conf['n_muy_relevantes'])

    def get_evaluacion_titularidad_A(self, evaluacion:EvaluacionAcreditacionRelevancia) -> EvaluacionAcreditacionRelevancia:
        """
        Metodo para la evaluacion con valoracion A de la titularidad de un investigador
        
        :param evaluación sobre la que se hidratará el criterio
        :return objeto EvaluacionAcreditacionRelevancia con los resultados del criterio de la comisión de las comisiones que tienen como criterio las relevancias de las publicaciones.
        """
        self.set_criterio_evaluacion(evaluacion, 'A')
        return self.get_evaluacion(evaluacion, "A")

    def get_evaluacion_titularidad_B(self, evaluacion:EvaluacionAcreditacionRelevancia) -> EvaluacionAcreditacionRelevancia:
        """
        Metodo para la evaluacion con valoracion B de la titularidad de un investigador
        
        :param evaluación sobre la que se hidratará el criterio
        :return objeto EvaluacionAcreditacionRelevancia con los resultados del criterio de la comisión de las comisiones que tienen como criterio las relevancias de las publicaciones.
        """
        self.set_criterio_evaluacion(evaluacion, 'B')
        return self.get_evaluacion(evaluacion, "B")

    def get_evaluacion_catedra_A(self, evaluacion:EvaluacionAcreditacionRelevancia) -> EvaluacionAcreditacionRelevancia:
        """
        Metodo para la evaluacion con valoracion A de la catedra de un investigador
        
        :param evaluación sobre la que se hidratará el criterio
        :return objeto EvaluacionAcreditacionRelevancia con los resultados del criterio de la comisión de las comisiones que tienen como criterio las relevancias de las publicaciones.
        """
        self.set_criterio_evaluacion(evaluacion, 'A')
        return self.get_evaluacion(evaluacion,"A")

    def get_evaluacion_catedra_B(self, evaluacion:EvaluacionAcreditacionRelevancia) -> EvaluacionAcreditacionRelevancia:
        """
        Metodo para la evaluacion con valoracion B de la catedra de un investigador
        
        :param evaluación sobre la que se hidratará el criterio
        :return objeto EvaluacionAcreditacionRelevancia con los resultados del criterio de la comisión de las comisiones que tienen como criterio las relevancias de las publicaciones.
        """
        self.set_criterio_evaluacion(evaluacion, 'B')
        return self.get_evaluacion(evaluacion, "B")

   
        
    

        
