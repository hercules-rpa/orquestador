from model.process.Process2.Entities.Commissions.Commission import Commission
from model.process.Process2.Entities.Evaluations.AccreditationEvaluationBiologCelularMolecular import AccreditationEvaluationBiologCelularMolecular,CriterionEvaluationBiologiaCelularMolecular
from model.process.Process2.Entities.Accreditation import Accreditation, AccreditationType

"""
La comisión de Biología Celular y Molecular se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
"""
class CommissionBiologiaCelularYMolecular(Commission):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_accreditation_evaluation(self, scientific_production, accreditation: Accreditation) -> AccreditationEvaluationBiologCelularMolecular:
        """
        Método encargado de evaluar la solicitud de acreditación de la comisión de Biología Celular y Molecular.

        :param [] scientific_production: Lista con las publicaciones del investigador.
        :param Accreditation accreditation: Tipo de acreditación a la que está postulando el investigador.
        :return AccreditationEvaluationBiologCelularMolecular Objeto con el resultado de la evaluación del investigador.
        """
        eval = AccreditationEvaluationBiologCelularMolecular(scientific_production=scientific_production, accreditation = accreditation)        
        if accreditation.type == AccreditationType.CATEDRA:            
            self.set_evaluation_criterion(eval)
            return self.get_catedra_evaluation(scientific_production, eval)
        elif accreditation.type == AccreditationType.TITULARIDAD:
            self.set_evaluation_criterion(eval)
            return self.get_titularidad_evaluation(scientific_production, eval)

    def set_evaluation_criterion(self, evaluation:AccreditationEvaluationBiologCelularMolecular):
        """
        Método que hidrata el criterio a la propiedad criterio de la evaluación.

        :param AccreditationEvaluationBiologCelularMolecular evaluation: Evaluación sobre la que se hidratará el criterio
        """
        if evaluation:
            criterion = self.get_configuration_criterion(evaluation.accreditation.type, '')
            conf100 = criterion['B100']
            conf75 = criterion['B75']
            if conf100 and conf75:
                evaluation.criterion = CriterionEvaluationBiologiaCelularMolecular(conf100['min_publicaciones'],conf100['t1_articulos'],conf100['n_autoria_preferente'],conf75['min_publicaciones'],conf75['t1_articulos'],conf75['n_autoria_preferente'])


    def get_catedra_evaluation(self, scientific_production, eval:AccreditationEvaluationBiologCelularMolecular) -> AccreditationEvaluationBiologCelularMolecular:
        """
        Metodo para la evaluación de la catedra de un investigador

        :param [] scientific_production: listado de articulos de un investigador
        :param EvaluacionAcreditacionBiologiaCelularMolecular eval: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Biologia Celular y Molecular.
        :return AccreditationEvaluationBiologCelularMolecular con los resultados del criterio de la comisión de Biologia Celular y Molecular.
        """
        eval = self.get_catedra_B(scientific_production,eval)
        if not eval.positive:
            eval = self.get_catedra_C(scientific_production, eval)
            if not eval.positive:
                eval = self.get_catedra_D(scientific_production, eval)

        return eval

    def get_titularidad_evaluation(self, scientific_production, eval:AccreditationEvaluationBiologCelularMolecular) -> AccreditationEvaluationBiologCelularMolecular:
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param [] scientific_production: listado de articulos de un investigador
        :param EvaluacionAcreditacionBiologiaCelularMolecular eval: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Biologia Celular y Molecular.
        :return objeto AccreditationEvaluationBiologCelularMolecular con los resltados del criterio de la comisión de Biologia Celular y Molecular.
        """
        eval = self.get_titularidad_B(scientific_production, eval)
        if not eval.positive:
            eval = self.get_titularidad_C(scientific_production, eval)
            if not eval.positive:
                eval = self.get_titularidad_D(scientific_production, eval)
        return eval

    def criterion_num_publications(self, scientific_production, num_publications) -> bool:
        """
        Método encargado de comprobar si se cumple que la producción científica tenga el número de publicaciones pasado por parámetro.

        :param [] scientific_production: Producción científica del investigador.
        :param int num_publications: Número de publicaciones necesarias para el criterio.
        :return booleano si se cumple con el criterio dado.
        """
        return len(scientific_production) >= num_publications

    def criterion_T1(self, scientific_production, num_publications):
        """
        Método que comprueba los artículos que pertenecen al tercil 1,
        devuelve una tupla donde el primer valor es un booleano que nos dice si se cumple el criterio
        y el segundo la lista de publicaciones obtenidas.

        :param [] scientific_production: Producción científica del investigador.
        :param int num_publications: Número de publicaciones necesarias para el criterio.
        :return Una tupla con un booleano representando si cumple con el criterio y un array con las publicaciones que se han sacado.
        """
        publications = []
        result: bool = False
        if scientific_production:
            for art in scientific_production:
                if art.get_tertile() == 1:
                    publications.append(art)

            if len(publications) >= num_publications:
                result = True
        return (result, publications)

    def criterion_authorship(self, scientific_production, num_publications: int):
        """
        Método que comprueba el criterio de autoria preferente (Primer/a firmante, coautoría, ultimo/a firmante y autor/a de correspondencia).

        :param [] scientific_production: Producción científica del investigador.
        :param int num_publications: Número de publicaciones necesarias para el criterio.
        :return Una tupla con el booleano representando si cumple con el criterio y un array con las publicaciones que se han sacado.
        """
        publications = []
        result: bool = False
        if scientific_production:
            for art in scientific_production:
                if (len(publications) < num_publications) and (art.author_position == 1 or (art.author_position == art.authors_number)):
                    publications.append(art)
        
        if publications and len(publications) == num_publications:
            result = True

        return (result, publications)
    
    def create_observation_B(self, eval: AccreditationEvaluationBiologCelularMolecular) -> str:
        """
        Método que construye el mensaje que se mostrará si no se cumplen los criterios para
        la valoración B

        :param AccreditationEvaluationBiologCelularMolecular eval: Objeto AccreditationEvaluationBiologCelularMolecular con la observación del criterio.
        :return Cadena con el resultado de la observación realizada.
        """
        observation = 'La valoración B podría ser ' + ("positiva" if eval.positive else "negativa") + ' porque se han obtenido los siguientes resultados: \n' + \
                'Número de publicaciones obtenidas necesarias: ' + str(eval.criterion.min_art_100) + ' obtenidas: ' + str(len(eval.scientific_production)) + '\n' + \
                'T1, necesarias: ' + str(eval.criterion.num_t1_100) + ' obtenidas: '        
        if eval.publications_t1:
            observation += str(len(eval.publications_t1)) + '\n'
        else:
            observation += '0 \n'
        observation += 'Autoría preferente, necesarias: ' + \
            str(eval.criterion.num_authorship_100) + ' obtenidas: '
        if eval.publications_authorship:
            observation += str(len(eval.publications_authorship)) + '\n'
        else:
            observation += '0 \n'

        return observation

    def create_observation_C(self, eval: AccreditationEvaluationBiologCelularMolecular) -> str:
        """
        Método que construye el mensaje que se mostrará si no se cumplen los criterios para
        la valoración C

        :param AccreditationEvaluationBiologCelularMolecular eval: Objeto AccreditationEvaluationBiologCelularMolecular con la observación del criterio.
        :return Cadena con el resultado de la observación realizada.
        """
        observation = 'La valoración ' + str(eval.assessment) + ' podría ser: ' + ("positiva" if eval.positive else "negativa") + ' porque se han obtenido los siguientes resultados: \n' + \
            'Número de publicaciones obtenidas necesarias: ' + str(eval.criterion.min_art_100) + \
            '-' + str(eval.criterion.min_art_75) + ', obtenidas: ' + \
            str(len(eval.scientific_production)) + '\n' + \
            'T1, necesarias: ' + str(eval.criterion.num_t1_100) + '-' + \
            str(eval.criterion.num_t1_75) + ', obtenidas: '
        
        if eval.publications_t1:
            observation += str(len(eval.publications_t1)) + '\n'
        else:
            observation += '0 \n'

        observation += 'Autoría preferente, necesarias: ' + \
            str(eval.criterion.num_authorship_100) + '-' + str(eval.criterion.num_authorship_75) + ', obtenidas: '
        if eval.publications_authorship:
            observation += str(len(eval.publications_authorship)) + '\n'
        else:
            observation += '0 \n'

        return observation

    def get_catedra_B(self, scientific_production, eval:AccreditationEvaluationBiologCelularMolecular) -> AccreditationEvaluationBiologCelularMolecular:
        """
        Método que evalúa los criterios de la cátedra con calificación B

        :param [] scientific_production: Producción cientifica del investigador.
        :param AccreditationEvaluationBiologCelularMolecular eval: Objeto de la evaluación de la comisión de Biología Celular y Molecular.
        :return Objeto AccreditationEvaluationBiologCelularMolecular con el resultado de la evaluación para la comisión de Biología Celular y Molecular.
        """
        criteria_number = 0
        if scientific_production: 
            if self.criterion_num_publications(scientific_production, eval.criterion.min_art_100):
                criteria_number += 1
            
            tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_100)
            if tuple_c2:
                eval.publications_t1 = tuple_c2[1]
                if tuple_c2[0]:
                    criteria_number += 1

            tuple_authorship = self.criterion_authorship(
                    scientific_production, eval.criterion.num_authorship_100)
            if tuple_authorship:
                eval.publications_authorship = tuple_authorship[1]
                if tuple_authorship[0]:
                    criteria_number += 1

            if criteria_number == 3:
                eval.positive = True
                eval.assessment = 'B'

        eval.observation += self.create_observation_B(eval)

        return eval

    def get_catedra_C(self, scientific_production,eval:AccreditationEvaluationBiologCelularMolecular) -> AccreditationEvaluationBiologCelularMolecular:
        """
        Método que evalúa los criterios de la cátedra con calificación C

        :param [] scientific_production: Colección con la producción científica del investigador.
        :param AccreditationEvaluationBiologCelularMolecular eval: Objeto de la evaluación de la comisión de Biología Celular y Molecular.
        :return Objeto AccreditationEvaluationBiologCelularMolecular con el resultado de la evaluación para la comisión de Biología Celular y Molecular.
        """
        if scientific_production:
            criteria_number = 0
            criteria_b = 0
            if self.criterion_num_publications(scientific_production, eval.criterion.min_art_100):
                criteria_number += 1
            elif self.criterion_num_publications(scientific_production, eval.criterion.min_art_75):
                criteria_b += 1
            
            tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_100)
            if tuple_c2 and tuple_c2[0]:
                criteria_number += 1                
                eval.publications_t1 = tuple_c2[1]
            else:
                tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_75)
                if tuple_c2[0]:
                    criteria_b += 1                
                    eval.publications_t1 = tuple_c2[1]

            if criteria_number != 2:
                tuple_authorship = self.criterion_authorship(
                        scientific_production,eval.criterion.num_authorship_100)
                if tuple_authorship:
                    if tuple_authorship[0]:
                        criteria_number += 1
                    eval.publications_authorship = tuple_authorship[1]
            
            elif criteria_b != 1:
                tuple_authorship = self.criterion_authorship(
                        scientific_production,eval.criterion.num_authorship_75)
                if tuple_authorship:
                    if tuple_authorship[0]:
                        criteria_b += 1
                    eval.publications_authorship = tuple_authorship[1]

            if criteria_number >= 2 and criteria_b >= 1:
                eval.positive = True
                eval.assessment = 'C'

        eval.observation += self.create_observation_C(eval)
        
        return eval

    def get_catedra_D(self, scientific_production, eval:AccreditationEvaluationBiologCelularMolecular) -> AccreditationEvaluationBiologCelularMolecular:
        """
        Método que evalúa los criterios de la cátedra con calificación D

        :param [] scientific_production: Colección con la producción científica del investigador.
        :param AccreditationEvaluationBiologCelularMolecular eval: Objeto de la evaluación de la comisión de Biología Celular y Molecular.
        :return Objeto AccreditationEvaluationBiologCelularMolecular con el resultado de la evaluación para la comisión de Biología Celular y Molecular.
        """
        if scientific_production:
            criteria_number = 0
            criteria_b = 0
            if self.criterion_num_publications(scientific_production, eval.criterion.min_art_100):
                criteria_number += 1
            elif self.criterion_num_publications(scientific_production, eval.criterion.num_authorship_75):
                criteria_b += 1
            
            if criteria_number == 1:
                tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_75)
                if tuple_c2:
                    if tuple_c2[0]:
                        criteria_b += 1                
                    eval.publications_t1 = tuple_c2[1] 

                tuple_authorship = self.criterion_authorship(
                        scientific_production,eval.criterion.num_authorship_75)
                if tuple_authorship:
                    if tuple_authorship[0]:
                        criteria_b += 1
                    eval.publications_authorship = tuple_authorship[1]               

            else: 
                tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_100)
                if tuple_c2:
                    if tuple_c2[0]:
                        criteria_number += 1                
                    eval.publications_t1 = tuple_c2[1]
                else:
                    tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_75)
                    if tuple_c2:
                        if tuple_c2[0]:
                            criteria_b += 1                
                        eval.publications_t1 = tuple_c2[1]
                
                tuple_authorship = self.criterion_authorship(
                        scientific_production,eval.criterion.num_authorship_75)
                if tuple_authorship:
                    if tuple_authorship[0]:
                        criteria_b += 1
                    eval.publications_authorship = tuple_authorship[1]  

            if criteria_number >= 1 and criteria_b >= 2:
                eval.positive = True
                eval.assessment = 'D'

        eval.observation += self.create_observation_C(eval)
        
        return eval

    def get_titularidad_B(self, scientific_production, eval:AccreditationEvaluationBiologCelularMolecular) -> AccreditationEvaluationBiologCelularMolecular:
        """
        Método que evalúa los criterios de la titularidad con calificación B

        :param [] scientific_production: Colección con la producción científica del investigador.
        :param AccreditationEvaluationBiologCelularMolecular eval: Objeto de la evaluación de la comisión de Biología Celular y Molecular.
        :return Objeto AccreditationEvaluationBiologCelularMolecular con el resultado de la evaluación para la comisión de Biología Celular y Molecular.
        """
        criteria_number = 0
        if scientific_production: 
            if self.criterion_num_publications(scientific_production, eval.criterion.min_art_100):
                criteria_number += 1
            
            tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_100)
            if tuple_c2:
                eval.publications_t1 = tuple_c2[1]
                if tuple_c2[0]:
                    criteria_number += 1

            tuple_authorship = self.criterion_authorship(
                    scientific_production,eval.criterion.num_authorship_100)
            
            if tuple_authorship:
                eval.publications_authorship = tuple_authorship[1]
                if tuple_authorship[0]:
                    criteria_number += 1

            if criteria_number == 3:
                eval.positive = True
                eval.assessment = 'B'

        eval.observation += self.create_observation_B(eval)
        return eval
    
    def get_titularidad_C(self, scientific_production, eval:AccreditationEvaluationBiologCelularMolecular) -> AccreditationEvaluationBiologCelularMolecular:
        """
        Método que evalúa los criterios de la titularidad con calificación C

        :param [] scientific_production: Colección con la producción científica del investigador.
        :param AccreditationEvaluationBiologCelularMolecular eval: Objeto de la evaluación de la comisión de Biología Celular y Molecular.
        :return Objeto AccreditationEvaluationBiologCelularMolecular con el resultado de la evaluación para la comisión de Biología Celular y Molecular.
        """
        if scientific_production:
            criteria_number = 0
            criteria_b = 0
            if self.criterion_num_publications(scientific_production, eval.criterion.min_art_100):
                criteria_number += 1
            elif self.criterion_num_publications(scientific_production, eval.criterion.min_art_75):
                criteria_b += 1
            
            tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_100)
            if tuple_c2 and tuple_c2[0]:
                criteria_number += 1                
                eval.publications_t1 = tuple_c2[1]
            else:
                tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_75)
                if tuple_c2[0]:
                    criteria_b += 1                
                    eval.publications_t1 = tuple_c2[1]

            if criteria_number < 2:
                tuple_authorship = self.criterion_authorship(
                        scientific_production,eval.criterion.num_authorship_100)
                if tuple_authorship:
                    if tuple_authorship[0]:
                        criteria_number += 1
                    eval.publications_authorship = tuple_authorship[1]
            
            elif criteria_b < 1:
                tuple_authorship = self.criterion_authorship(
                        scientific_production,eval.criterion.num_authorship_75)                
                if tuple_authorship: 
                    if tuple_authorship[0]:
                        criteria_b += 1
                    eval.publications_authorship = tuple_authorship[1]

            if criteria_number >= 2 and criteria_b >= 1:
                eval.positive = True
                eval.assessment = 'C'

        eval.observation += self.create_observation_C(eval)
        
        return eval
   
    def get_titularidad_D(self, scientific_production, eval:AccreditationEvaluationBiologCelularMolecular) -> AccreditationEvaluationBiologCelularMolecular:
        """
        Método que evalúa los criterios de la titularidad con calificación D

        :param [] scientific_production: Colección con la producción científica del investigador.
        :param AccreditationEvaluationBiologCelularMolecular eval: Objeto de la evaluación de la comisión de Biología Celular y Molecular.
        :return Objeto AccreditationEvaluationBiologCelularMolecular con el resultado de la evaluación para la comisión de Biología Celular y Molecular.
        """
        if scientific_production:
            criteria_number = 0
            criteria_b = 0
            if self.criterion_num_publications(scientific_production, eval.criterion.min_art_100):
                criteria_number += 1
            elif self.criterion_num_publications(scientific_production, eval.criterion.min_art_75):
                criteria_b += 1
            
            if criteria_number == 1:
                tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_75)
                if tuple_c2:
                    if tuple_c2[0]:
                        criteria_b += 1                
                    eval.publications_t1 = tuple_c2[1] 

                tuple_authorship = self.criterion_authorship(
                        scientific_production,eval.criterion.num_authorship_75)
                if tuple_authorship:
                    if tuple_authorship[0]:
                        criteria_b += 1
                    eval.publications_authorship = tuple_authorship[1]               

            else: 
                tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_100)
                if tuple_c2:
                    if tuple_c2[0]:
                        criteria_number += 1                
                    eval.publications_t1 = tuple_c2[1]
                else:
                    tuple_c2 = self.criterion_T1(scientific_production, eval.criterion.num_t1_75)
                    if tuple_c2:
                        if tuple_c2[0]:
                            criteria_b += 1                
                        eval.publications_t1 = tuple_c2[1]
                
                tuple_authorship = self.criterion_authorship(
                        scientific_production,eval.criterion.num_authorship_75)
                if tuple_authorship:
                    if tuple_authorship[0]:
                        criteria_b += 1
                    eval.publications_authorship = tuple_authorship[1]  

            if criteria_number >= 1 and criteria_b >= 2:
                eval.positive = True
                eval.assessment = 'D'

        eval.observation += self.create_observation_C(eval)        
        return eval