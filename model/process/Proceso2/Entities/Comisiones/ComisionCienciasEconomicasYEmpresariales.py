from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion
from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionCienciasEconomicasYEmpresariales import CriterioEvaluacionCienciasEconomicasYEmpresariales, EvaluacionAcreditacionCienciasEconomicasYEmpresariales


class ComisionCienciasEconomicasYEmpresariales(Comision):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
    
    def get_evaluacion_acreditacion(self, produccion_cientifica, acreditacion: Acreditacion)  -> EvaluacionAcreditacionCienciasEconomicasYEmpresariales:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] produccion_cientifica: listado de artículos de un investigador.
        :param Acreditacion acreditacion: tipo de acreditación que se está solicitando.
        :return objeto EvaluacionAcreditacionCienciasEconomicasYEmpresariales con los resultados del criterio de la comisión de Ciencias Economicas y Empresariales.
        """
        #TODO: num_relevantes, num_Q1_Q2, num_Q3_Q4 y num_D1 vendrán dados por el archivo de configuración
        evaluacion = EvaluacionAcreditacionCienciasEconomicasYEmpresariales(produccion_cientifica=produccion_cientifica, 
        acreditacion=acreditacion)

        if acreditacion.tipo == TipoAcreditacion.CATEDRA:
            self.set_criterio_evaluacion(evaluacion)
            return self.get_evaluacion_catedra(produccion_cientifica,evaluacion)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            self.set_criterio_evaluacion(evaluacion)
            return self.get_evaluacion_titularidad(produccion_cientifica, evaluacion)
                    
    def set_criterio_evaluacion(self, evaluacion:EvaluacionAcreditacionCienciasEconomicasYEmpresariales):
        """
        Método que hidrata el criterio a la propiedad criterio de la evaluación.
        :param evaluación sobre la que se hidratará el criterio
        :param valoración valoración que se utilizará para obtener los parámetros 
        """
        if evaluacion:
            criterio = self.get_criterio_acreditacion(evaluacion.acreditacion.tipo)
            conf_A = criterio['A']
            conf_B = criterio['B']
            if conf_A and conf_B:
                evaluacion.criterio = CriterioEvaluacionCienciasEconomicasYEmpresariales(conf_A['n1_publicaciones'],conf_A['n2_publicaciones'],conf_B['d1_publicaciones'])


    def get_evaluacion_catedra(self, produccion_cientifica, evaluacion: EvaluacionAcreditacionCienciasEconomicasYEmpresariales) -> EvaluacionAcreditacionCienciasEconomicasYEmpresariales:
        """
        Metodo para la evaluación de la catedra de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param EvaluacionAcreditacionCienciasEconomicasYEmpresariales evaluacion: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Ciencias Economicas y Empresariales.
        :return objeto EvaluacionAcreditacionCienciasEconomicasYEmpresariales con los resultados del criterio de la comisión de Ciencias Economicas y Empresariales.
        """
        eval, articulos_Q1_Q2, articulos_Q3_Q4 = self.criterio_opcion_1(produccion_cientifica,evaluacion.criterio)
        if eval:
            evaluacion.positiva = eval
            evaluacion.articulos_Q1_Q2 = articulos_Q1_Q2
            evaluacion.articulos_Q3_Q4 = articulos_Q3_Q4
        else:
            eval, articulos_D1 = self.criterio_opcion_2(produccion_cientifica, evaluacion.criterio)
            if eval:
                evaluacion.positiva = eval
                evaluacion.articulos_D1 = articulos_D1
        if not evaluacion.positiva:
            evaluacion.observaciones = self.create_observaciones_catedra(evaluacion,produccion_cientifica)
        
        return eval

    def get_evaluacion_titularidad(self, produccion_cientifica, evaluacion: EvaluacionAcreditacionCienciasEconomicasYEmpresariales) -> EvaluacionAcreditacionCienciasEconomicasYEmpresariales:
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param EvaluacionAcreditacionCienciasEconomicasYEmpresariales evaluacion: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Ciencias Economicas y Empresariales.
        :return objeto EvaluacionAcreditacionCienciasEconomicasYEmpresariales con los resultados del criterio de la comisión de Ciencias Economicas y Empresariales.
        """
        eval, articulos_Q1_Q2, articulos_Q3_Q4 = self.criterio_opcion_1(produccion_cientifica,evaluacion.criterio)
        if eval:
            evaluacion.positiva = eval
            evaluacion.articulos_Q1_Q2 = articulos_Q1_Q2
            evaluacion.articulos_Q3_Q4 = articulos_Q3_Q4
        else:
            eval, articulos_D1 = self.criterio_opcion_2(produccion_cientifica, evaluacion.criterio)
        
            if eval:
                evaluacion.positiva = eval
                evaluacion.articulos_D1 = articulos_D1
        
        if not evaluacion.positiva:
            evaluacion.observaciones = self.create_observaciones_titularidad(evaluacion,produccion_cientifica)
        return eval 

    def criterio_opcion_1(self, produccion_cientifica, criterio: CriterioEvaluacionCienciasEconomicasYEmpresariales) -> tuple([bool, [],[]]):
        """
        Método para la evaluacion de los criterios para la opcion 1

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param CriterioEvaluacionCienticiasEconomicasYEmpresariales criterio: Objeto que almacena los numeros que definen el minimo de articulos para cada criterio
        :return Tupla con un booleano del resultado del criterio y las listas de publicaciones en el primer y segundo cuartil y en el tercer y cuarto cuartil
        """
        
        result = False
        articulos_Q1_Q2 = []
        articulos_Q3_Q4 = []
        if len(produccion_cientifica)>= criterio.num_articulos:
            for articulo in produccion_cientifica:
                if articulo.get_cuartil() == 1 or articulo.get_cuartil() == 2:
                    articulos_Q1_Q2.append(articulo)
                elif articulo.get_cuartil() == 3 or articulo.get_cuartil() == 4:
                    articulos_Q3_Q4.append(articulo)
        
        if articulos_Q1_Q2 and articulos_Q3_Q4 and len(articulos_Q1_Q2) >= criterio.num_Q1_Q2 and len(articulos_Q3_Q4) >= criterio.num_Q3_Q4:
            result = True
            
        return result, articulos_Q1_Q2, articulos_Q3_Q4

    def criterio_opcion_2(self, produccion_cientifica, criterio: CriterioEvaluacionCienciasEconomicasYEmpresariales) -> tuple([bool, []]):
        """
        Método para la evaluacion de los criterios para la opcion 2

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param CriterioEvaluacionCienticiasEconomicasYEmpresariales criterio: Objeto que almacena los numeros que definen el minimo de articulos para cada criterio
        :return Tupla con un booleano del resultado del criterio y la listas de publicaciones en el primer decil.
        """
        result = False
        articulos_D1 = []
        if len(produccion_cientifica)>= criterio.num_articulos:
            for articulo in produccion_cientifica:
                if articulo.get_decil() == 1:
                    articulos_D1.append(articulo)
        
        if articulos_D1 and len(articulos_D1) >= criterio.num_D1:
            result = True

        return result, articulos_D1

    def create_observaciones_catedra(self, evaluacion: EvaluacionAcreditacionCienciasEconomicasYEmpresariales, produccion_cientifica: list, num_publicaciones: int, num_t1: int, num_autoria: int, num_autoria_t1: int) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la cátedra.

        :param EvaluacionAcreditacionMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacion de Ciencias Economícas y Empresariales donde almacenamos los datos de la evaluación.
        :param list produccion_cientifica: Lista de publicaciones proporcionadas para la evaluación.
        :return String con la evaluación de la comisión de Ciencias Economícas y Empresariales.
        """
        return "En el resultado de la valoración para el criterio de la cátedra se ha obtenido un resultado negativo con los siguientes resultados: \n  Número de publicaciones necesarias " + \
            str(evaluacion.criterio.num_articulos) + ". Obtenidas: " + str(len(produccion_cientifica)) + \
            ". \n Número de publicaciones necesarias en el cuartil 1 y 2: " + str(evaluacion.criterio.num_Q1_Q2) + \
            ". Obtenidas: " + str(len(evaluacion.articulos_Q1_Q2)) + \
            " \n Número de publicaciones necesarias en el cuartil 3 y 4: " + str(evaluacion.criterio.num_Q3_Q4) + \
            " Obtenidas: " + str(len(evaluacion.articulos_Q3_Q4)) + "\n Número de publicaciones necesarias en el decil 1: " + str(evaluacion.criterio.num_D1) + " Obtenidas: " + str(len(evaluacion.articulos_D1)) + "."

    def create_observaciones_titularidad(self, evaluacion: EvaluacionAcreditacionCienciasEconomicasYEmpresariales, produccion_cientifica: list) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la titularidad.

        :param EvaluacionAcreditacionMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacion de Ciencias Economícas y Empresariales donde almacenamos los datos de la evaluación.
        :param list produccion_cientifica: Lista de publicaciones proporcionadas para la evaluación.
        :return String con la evaluación de la comisión de Ciencias Economícas y Empresariales.
        """
        return "En el resultado de la valoración para el criterio de la titularidad se ha obtenido un resultado negativo con los siguientes resultados: \n  Número de publicaciones necesarias " + str(evaluacion.criterio.num_articulos) + ". Obtenidas: " + str(len(produccion_cientifica)) + ". \n Número de publicaciones necesarias en el cuartil 1 y 2: " + str(evaluacion.criterio.num_Q1_Q2) + ". Obtenidas: " + str(len(evaluacion.articulos_Q1_Q2)) + " \n Número de publicaciones necesarias en el cuartil 3 y 4: " + str(evaluacion.criterio.num_Q3_Q4) + " Obtenidas: " + str(len(evaluacion.articulos_Q3_Q4)) + "\n Número de publicaciones necesarias en el decil 1: " + str(evaluacion.criterio.num_D1) + " Obtenidas: " + str(len(evaluacion.articulos_D1)) + "."

    