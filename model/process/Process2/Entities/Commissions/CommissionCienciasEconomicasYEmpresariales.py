from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType
from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationCienciasEconomicasYEmpresariales import CriterionEvaluationCienciasEconomicasYEmpresariales, AccreditationEvaluationCienciasEconomicasYEmpresariales


class CommissionCienciasEconomicasYEmpresariales(Commission):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
    
    def get_accreditation_evaluation(self, scientific_production, 
    accreditation: Accreditation)  -> AccreditationEvaluationCienciasEconomicasYEmpresariales:
        """
        Método general de evaluación que decide qué tipo de acreditación se está solicitando para el investigador.

        :param [] scientific_production: listado de artículos de un investigador.
        :param Accreditation accreditation: tipo de acreditación que se está solicitando.
        :return objeto AccreditationEvaluationCienciasEconomicasYEmpresariales con los resultados del criterio de la comisión de Ciencias Economicas y Empresariales.
        """

        eval = AccreditationEvaluationCienciasEconomicasYEmpresariales(scientific_production=scientific_production, 
        accreditation=accreditation)

        if accreditation.type == AccreditationType.CATEDRA:
            self.set_criterion_evaluation(eval)
            return self.get_catedra(scientific_production,eval)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            self.set_criterion_evaluation(eval)
            return self.get_titularidad(scientific_production, eval)
                    
    def set_criterion_evaluation(self, eval:AccreditationEvaluationCienciasEconomicasYEmpresariales):
        """
        Método que hidrata el criterio a la propiedad criterio de la evaluación.
        
        :param evaluación sobre la que se hidratará el criterio
        """
        if eval:
            criterion = self.get_configuration_criterion(eval.accreditation.type)
            conf_A = criterion['A']
            conf_B = criterion['B']
            if conf_A and conf_B:
                eval.criterion = CriterionEvaluationCienciasEconomicasYEmpresariales(conf_A['n1_publicaciones'],conf_A['n2_publicaciones'],conf_B['d1_publicaciones'])


    def get_catedra(self, scientific_production, evaluation: AccreditationEvaluationCienciasEconomicasYEmpresariales) -> AccreditationEvaluationCienciasEconomicasYEmpresariales:
        """
        Metodo para la evaluación de la catedra de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param EvaluacionAcreditacionCienciasEconomicasYEmpresariales evaluacion: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Ciencias Economicas y Empresariales.
        :return objeto EvaluacionAcreditacionCienciasEconomicasYEmpresariales con los resultados del criterio de la comisión de Ciencias Economicas y Empresariales.
        """
        eval, art_Q1_Q2, art_Q3_Q4 = self.criterion_option_1(scientific_production,evaluation.criterion)
        if eval:
            evaluation.positive = eval
            evaluation.art_Q1_Q2 = art_Q1_Q2
            evaluation.art_Q3_Q4 = art_Q3_Q4
        else:
            eval, art_D1 = self.criterion_option_2(scientific_production, evaluation.criterion)
            if evaluation:
                evaluation.positive = eval
                evaluation.art_D1 = art_D1
        evaluation.observation = self.create_observations_catedra(evaluation,scientific_production)
        
        return evaluation

    def get_titularidad(self, scientific_production, evaluation: AccreditationEvaluationCienciasEconomicasYEmpresariales) -> AccreditationEvaluationCienciasEconomicasYEmpresariales:
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param EvaluacionAcreditacionCienciasEconomicasYEmpresariales evaluacion: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Ciencias Economicas y Empresariales.
        :return objeto EvaluacionAcreditacionCienciasEconomicasYEmpresariales con los resultados del criterio de la comisión de Ciencias Economicas y Empresariales.
        """
        eval, articulos_Q1_Q2, articulos_Q3_Q4 = self.criterion_option_1(scientific_production,evaluation.criterion)
        if eval:
            evaluation.positive = eval
            evaluation.art_Q1_Q2 = articulos_Q1_Q2
            evaluation.art_Q3_Q4 = articulos_Q3_Q4
        else:
            eval, articulos_D1 = self.criterion_option_2(scientific_production, evaluation.criterion)
            if eval:
                evaluation.positive = eval
                evaluation.art_D1 = articulos_D1
        
        evaluation.observation = self.create_observations_titularidad(evaluation,scientific_production)
        return evaluation 

    def criterion_option_1(self, scientific_production, 
    criterion: CriterionEvaluationCienciasEconomicasYEmpresariales) -> tuple([bool, [],[]]):
        """
        Método para la evaluacion de los criterios para la opcion 1

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param CriterioEvaluacionCienticiasEconomicasYEmpresariales criterio: Objeto que almacena los numeros que definen el minimo de articulos para cada criterio
        :return Tupla con un booleano del resultado del criterio y las listas de publicaciones en el primer y segundo cuartil y en el tercer y cuarto cuartil
        """
        
        result = False
        art_Q1_Q2 = []
        art_Q3_Q4 = []
        if len(scientific_production)>= criterion.num_Q1_Q2 + criterion.num_Q3_Q4:
            for article in scientific_production:
                if article.get_quartile() == 1 or article.get_quartile() == 2:
                    art_Q1_Q2.append(article)
                elif article.get_quartile() == 3 or article.get_quartile() == 4:
                    art_Q3_Q4.append(article)
        
        if art_Q1_Q2 and art_Q3_Q4 and len(art_Q1_Q2) >= criterion.num_Q1_Q2 and len(art_Q3_Q4) >= criterion.num_Q3_Q4:
            result = True
            
        return result, art_Q1_Q2, art_Q3_Q4

    def criterion_option_2(self, produccion_cientifica, criterio: CriterionEvaluationCienciasEconomicasYEmpresariales) -> tuple([bool, []]):
        """
        Método para la evaluacion de los criterios para la opcion 2

        :param [] produccion_cientifica: listado de articulos de un investigador.
        :param CriterioEvaluacionCienticiasEconomicasYEmpresariales criterio: Objeto que almacena los numeros que definen el minimo de articulos para cada criterio
        :return Tupla con un booleano del resultado del criterio y la listas de publicaciones en el primer decil.
        """
        result = False
        articles_D1 = []
        if len(produccion_cientifica)>= criterio.num_Q1_Q2 + criterio.num_Q3_Q4:
            for article in produccion_cientifica:
                if article.get_decile() == 1:
                    articles_D1.append(article)
        
        if articles_D1 and len(articles_D1) >= criterio.num_D1:
            result = True

        return result, articles_D1

    def create_observations_catedra(self, evaluation: AccreditationEvaluationCienciasEconomicasYEmpresariales, scientific_production: list) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la cátedra.

        :param EvaluacionAcreditacionMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacion de Ciencias Economícas y Empresariales donde almacenamos los datos de la evaluación.
        :param list produccion_cientifica: Lista de publicaciones proporcionadas para la evaluación.
        :return String con la evaluación de la comisión de Ciencias Economícas y Empresariales.
        """
        return "En el resultado de la valoración para el criterio de la cátedra se podría obtener un resultado " +  ("positivo" if evaluation.positive else "negativo") + ". \n  Número de publicaciones necesarias " + \
                str(evaluation.criterion.num_Q1_Q2 + evaluation.criterion.num_Q3_Q4 + evaluation.criterion.num_D1) + ". Obtenidas: " + str(len(scientific_production)) + \
                ". \n Número de publicaciones necesarias en el cuartil 1 y 2: " + str(evaluation.criterion.num_Q1_Q2) + \
                ". Obtenidas: " + str(len(evaluation.art_Q1_Q2)) + \
                " \n Número de publicaciones necesarias en el cuartil 3 y 4: " + str(evaluation.criterion.num_Q3_Q4) + \
                " Obtenidas: " + str(len(evaluation.art_Q3_Q4)) + "\n Número de publicaciones necesarias en el decil 1: " + str(evaluation.criterion.num_D1) + " Obtenidas: " + str(len(evaluation.art_D1)) + ".\n\n"

    def create_observations_titularidad(self, evaluation: AccreditationEvaluationCienciasEconomicasYEmpresariales, 
    scientific_production: list) -> str:
        """
        Método para especificar las observaciones de la calificación de investigacion en la titularidad.

        :param EvaluacionAcreditacionMedicinaClinicaYEspecialidades evaluacion: Objeto EvaluacionAcreditacion de Ciencias Economícas y Empresariales donde almacenamos los datos de la evaluación.
        :param list produccion_cientifica: Lista de publicaciones proporcionadas para la evaluación.
        :return String con la evaluación de la comisión de Ciencias Economícas y Empresariales.
        """
        return "En el resultado de la valoración para el criterio de la titularidad se podría obtener un resultado " +  ("positivo" if evaluation.positive else "negativo") + ". \n  Número de publicaciones necesarias " + str(evaluation.criterion.num_Q3_Q4 + evaluation.criterion.num_Q1_Q2 + evaluation.criterion.num_D1) + ". Obtenidas: " + str(len(scientific_production)) + ". \n Número de publicaciones necesarias en el cuartil 1 y 2: " + str(evaluation.criterion.num_Q1_Q2) + ". Obtenidas: " + str(len(evaluation.art_Q1_Q2)) + " \n Número de publicaciones necesarias en el cuartil 3 y 4: " + str(evaluation.criterion.num_Q3_Q4) + " Obtenidas: " + str(len(evaluation.art_Q3_Q4)) + "\n Número de publicaciones necesarias en el decil 1: " + str(evaluation.criterion.num_D1) + " Obtenidas: " + str(len(evaluation.art_D1)) + ".\n\n"