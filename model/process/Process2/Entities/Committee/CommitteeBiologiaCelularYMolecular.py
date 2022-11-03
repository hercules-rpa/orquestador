from model.process.Process2.Entities.RO import RO
from model.process.Process2.Entities.Evaluations.SexenioEvaluation import SexenioEvaluation, ClassificationInfo
from model.process.Process2.Entities.Committee.Committee import Committee


class CommitteeBiologiaCelularYMolecular(Committee):
    """
    Comité encargado de la evaluación de solicitud de sexenios para la comisión de Biología celular y molecular.
    """
    def __init__(self, id, evaluator, is_commission: bool = False):
        super().__init__(id, evaluator, is_commission)

    def get_evaluation_sexenio(self, scientific_production) -> SexenioEvaluation:
        evaluation = SexenioEvaluation(scientific_production=scientific_production, 
            parameters= self.get_criterion())
        clasification = evaluation.get_classification_production()

        tup = self.criterion1(clasification, evaluation.parameters)
        if tup and tup[0] > 0:
            evaluation = self.set_evaluation(tup, evaluation)
        else:
            tup = self.criterion2(clasification, evaluation.parameters)
            if tup and tup[0] > 0:
                evaluation = self.set_evaluation(tup, evaluation)
            else:
                tup = self.criterion3(clasification, evaluation.parameters)                
                if tup and tup[0] > 0:
                    evaluation = self.set_evaluation(tup, evaluation)
                else:
                    tup = self.criterion4(clasification, evaluation.parameters)
                    if tup and tup[0] > 0:
                        evaluation = self.set_evaluation(tup, evaluation)
        return evaluation        
        
    
    def set_evaluation(self, tupl:tuple([int, list]), evaluation:SexenioEvaluation) -> SexenioEvaluation:
        """
        Método que sirve para hidratar las propiedades puntuación y producción principal de las evaluaciones.
        :param tupl tupla que contiene la puntuación y la lista de publicaciones
        :param evaluation evaluación del sexenio
        :return evaluación evaluación resultante
        """
        if tupl and evaluation: 
            evaluation.punctuation = tupl[0]
            evaluation.main_production = tupl[1]
        return evaluation
   
    def get_punctuation(self, element: RO, punctuations:dict) -> int:
        """
        Método que obtiene la puntuación de un RO en base a los criterios establecidos
        por el comité.
        :param RO elemento que se evaluará para asignar la puntuación
        :return int puntuación obtenida
        """
        punctuation = 0
        if element:
            if element.get_decile() == 1:
                if element.author_position == 1:
                    punctuation = punctuations['puntuacion_d1_autoria_destacada']
                elif element.author_position == 2 and element.authors_number <= 6:
                    punctuation = punctuations['puntuacion_d1_autoria_secundaria']
                else:
                    punctuation = punctuations['puntuacion_d1_mas_6_autores']
            else:
                cuartil = element.get_quartile()
                if cuartil == 1:
                    if element.author_position == 1:
                        punctuation = punctuations['puntuacion_q1_autoria_destacada']
                    elif element.author_position == 2 and element.authors_number <= 6:
                        punctuation = punctuations['puntuacion_q1_autoria_secundaria']
                    else:
                        punctuation = punctuations['puntuacion_q1_mas_6_autores']
                elif cuartil == 2:
                    if element.author_position == 1:
                        punctuation = punctuations['puntuacion_q2_autoria_destacada']
                    elif element.author_position == 2 and element.authors_number <= 6:
                        punctuation = punctuations['puntuacion_q2_autoria_secundaria']
                    else:
                        punctuation = punctuations['puntuacion_q2_mas_6_autores']
                elif cuartil == 3:
                    if element.author_position == 1:
                        punctuation = punctuations['puntuacion_q3_autoria_destacada']
                    elif element.author_position == 2 and element.authors_number <= 6:
                        punctuation = punctuations['puntuacion_q3_autoria_secundaria']
                    else:
                        punctuation = punctuations['puntuacion_q3_mas_6_autores']
                elif cuartil == 4:
                    if element.author_position == 1:
                        punctuation = punctuations['puntuacion_q4_autoria_destacada']
                    elif element.author_position == 2 and element.authors_number <= 6:
                        punctuation = punctuations['puntuacion_q4_autoria_secundaria']
                    else:
                        punctuation = punctuations['puntuacion_q4_mas_6_autores']
        return punctuation

    def get_punctuation_total(self, elements:list, punctuations:dict) -> int:
        """
        Método que obtiene la puntuación total de una colección.
        :param list lista de elementos de la que se va a obtener la puntuación.
        :return int puntuación total.
        """
        puntuacion =0
        if elements:
            for element in elements:
                puntuacion += self.get_punctuation(element, punctuations)

        return puntuacion
                
    def criterion1(self, clasification: ClassificationInfo, parameters:dict) -> tuple([int, list]):
        """
        Método que evalúa si se tiene 5 aportaciones en Q1 (firmante en cualquier posición).
        :param ClassificationInfo clasificación de la producción científica del investigador.
        :param parameters parámetros necesarios
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal
        """
        punctuation = 0
        results = []
        criterion = parameters['criterio1']
        if clasification and len(clasification.publications_q1) >= criterion['num_publicaciones_q1']:
            results = clasification.publications_q1[0:criterion['num_publicaciones_q1']]

        if results:
            punctuation = self.get_punctuation_total(results,parameters['puntuaciones'])

        return (punctuation, results)

    def is_featured_signer(self, element: RO) -> bool:
        """
        Método que comprueba si el investigador es un firmante destacado en el artículo,
        para ello, debe ser:
        - primer firmante
        - segundo firmante 
        - segundo firmante pero que no tenga más de seis autores la publicación
        :param RO elemento a analizar
        :return bool true si es firmante destacado.
        """
        if element.author_position == 1:
            return True
        elif element.author_position > 6 and element.author_position == 2:
            return True
        elif element.author_position <= 6 and element.author_position == 2:
            return True
        return False

    def criterion2(self, clasification: ClassificationInfo, parametros:dict) -> tuple([int, list]):
        """
        Método que evalúa si se tiene 5 aportaciones en Q2, 
        de las cuales 3 con firmante destacado.
        :param ClassificationInfo clasificación de la producción científica del investigador.
        :param parameters parámetros necesarios
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal.
        """
        punctuation = 0
        results = []
        criterion = parametros['criterio2']
        if clasification and len(clasification.publications_q2) >= criterion['num_publicaciones_q2']:
            arts_featured_signer = []
            aux = []
            i = 0

            while len(clasification.publications_q2) < i:
                element = arts_featured_signer[i]
                if self.is_featured_signer(element):
                    arts_featured_signer.append(element)
                else:
                    aux.append(element)
                i += 1

            if len(arts_featured_signer) >= criterion['num_publicaciones_q2']:
                results = arts_featured_signer[0:criterion['num_publicaciones_q2']]
            elif len(arts_featured_signer) >= criterion['num_firmante_destacado']:
                results = arts_featured_signer

                if aux:
                    res = criterion['num_publicaciones_q2'] - len(arts_featured_signer)
                    if len(aux) >= res:
                        results += aux[0:res]
                    else:
                        results += aux[0:]

        if len(results) == criterion['num_publicaciones_q2']:
            punctuation += self.get_punctuation_total(results, parametros['puntuaciones'] )

        return (punctuation, results)

    def get_elements_featured_signer(self, elements: list) -> list:
        """
        Método que obtiene la cantidad de elementos que tienen firmante destacado de la lista.
        :param list: lista que contiene los elementos a analizar.
        :return list: lista con los elementos que tienen firmante destacado.
        """
        results = []
        i = 0
        while(len(elements) < i and len(results) < 3):
            element = elements[i]
            if self.is_featured_signer(element):
                results.append(element)
        return results

    def criterion3(self, clasification: ClassificationInfo, parameters:dict) -> tuple([int, list]):
        """
        Método que evalúa si hay menos de 5 Aportaciones:
            - 3 D1 como persona firmante destacada en todas ellas.
            - 4 Q1 con autoría destacada en al menos 2.
        :param ClassificationInfo clasificación de la producción científica del investigador.
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal
        """
        results = []
        punctuation = 0
        criterion = parameters['criterio3']
        if clasification:
            if len(clasification.publications_d1) >= criterion['num_publicaciones_d1']:
                elements = self.get_elements_featured_signer(clasification.publications_d1)
                if len(elements) >= criterion['num_publicaciones_d1']:
                    results = elements[0:criterion['num_publicaciones_d1']]
                    punctuation = self.get_punctuation_total(results, parameters['puntuaciones'])


            if not results and len(clasification.publications_q1) >= criterion['num_publicaciones_q1']:
                elements = self.get_elements_featured_signer(clasification.publications_q1)
                if len(elements) >= criterion['num_firmante_destacado_q1']:
                    results = elements[0:criterion['num_firmante_destacado_q1']]                
                    i=0
                    while(len(results) < 4 and len(clasification.publications_q1) < i):                   
                        art = clasification.publications_q1[i]
                        if art not in results:
                            results.append(art)

                    if len(results) == criterion['num_publicaciones_q1']:
                        punctuation = self.get_punctuation_total(results, parameters['puntuaciones']) 

        return (punctuation, results)

    def criterion4(self, clasification:ClassificationInfo, parameters:dict) -> tuple([int, list]):
        """
        Método que evalúa el críterio: 5 Aportaciones: 5 Q1/Q2 combinadas.
        :param ClassificationInfo clasificación de la producción científica del investigador.
        :return tuple([int, list]) devuelve en una tupla la puntuación y la lista de producción principal
        """
        punctuation = 0
        results = []
        criterion = parameters['criterio4']
        if clasification and clasification.publications_q1 and clasification.publications_q2:
            results = clasification.publications_q1[0:]
            res = criterion['num_publicaciones_q1q2']-len(clasification.publications_q1)

            if len(clasification.publications_q2) >= res:
                results += clasification.publications_q2[0:res]

            if len(results) == criterion['num_publicaciones_q1q2']:
                punctuation = self.get_punctuation_total(results, parameters['puntuaciones'])

        return (punctuation, results)