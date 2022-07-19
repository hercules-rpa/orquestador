from model.process.Proceso2.Entities.Comisiones.Comision import Comision
from model.process.Proceso2.Entities.Evaluaciones.EvaluacionAcreditacionBiologCelularMolecular import EvaluacionAcreditacionBiologCelularMolecular,CriterioEvaluacionBiologiaCelularMolecular
from model.process.Proceso2.Entities.Acreditacion import Acreditacion, TipoAcreditacion

"""
La comisión de Biología Celular y Molecular se encarga de evaluar los requisitos para los investigadores que pertenecen a esta área.
"""
class ComisionBiologiaCelularYMolecular(Comision):
    def __init__(self, id, evaluador, es_comision: bool = True):
        super().__init__(id, evaluador, es_comision)
        
    def get_evaluacion_acreditacion(self, produccion_cientifica, acreditacion: Acreditacion) -> EvaluacionAcreditacionBiologCelularMolecular:
        """
        Método encargado de evaluar la solicitud de acreditación
        """
        eval = EvaluacionAcreditacionBiologCelularMolecular(produccion_cientifica=produccion_cientifica, acreditacion = acreditacion)        
        if acreditacion.tipo == TipoAcreditacion.CATEDRA:            
            self.set_criterio_evaluacion(eval)
            return self.get_evaluacion_catedra(produccion_cientifica, eval)
        elif acreditacion.tipo == TipoAcreditacion.TITULARIDAD:
            self.set_criterio_evaluacion(eval)
            return self.get_evaluacion_titularidad(produccion_cientifica, eval)

    def set_criterio_evaluacion(self, evaluacion:EvaluacionAcreditacionBiologCelularMolecular):
        """
        Método que hidrata el criterio a la propiedad criterio de la evaluación.
        :param evaluación sobre la que se hidratará el criterio
        :param valoración valoración que se utilizará para obtener los parámetros 
        """
        if evaluacion:
            criterio = self.get_criterio_acreditacion(evaluacion.acreditacion.tipo)
            conf100 = criterio['B100']
            conf75 = criterio['B75']
            if conf100 and conf75:
                evaluacion.criterio = CriterioEvaluacionBiologiaCelularMolecular(conf100['min_publicaciones'],conf100['t1_articulos'],conf100['n_autoria_preferente'],conf75['min_publicaciones'],conf75['t1_articulos'],conf75['n_autoria_preferente'])


    def get_evaluacion_catedra(self, produccion_cientifica, eval:EvaluacionAcreditacionBiologCelularMolecular) -> EvaluacionAcreditacionBiologCelularMolecular:
        """
        Metodo para la evaluación de la catedra de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador
        :param EvaluacionAcreditacionBiologiaCelularMolecular eval: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Biologia Celular y Molecular.
        :return objeto EvaluacionAcreditacionBiologiaCelularYMolecular con los resltados del criterio de la comisión de Biologia Celular y Molecular.
        """
        eval = self.get_evaluacion_catedra_B(produccion_cientifica,eval)
        if not eval.positiva:
            eval = self.get_evaluacion_catedra_C(produccion_cientifica, eval)
            if not eval.positiva:
                eval = self.get_evaluacion_catedra_D(produccion_cientifica, eval)

        return eval

    def get_evaluacion_titularidad(self, produccion_cientifica, eval:EvaluacionAcreditacionBiologCelularMolecular) -> EvaluacionAcreditacionBiologCelularMolecular:
        """
        Metodo para la evaluación de la titularidad de un investigador

        :param [] produccion_cientifica: listado de articulos de un investigador
        :param EvaluacionAcreditacionBiologiaCelularMolecular eval: Objeto EvaluacionAcreditacon que contiene el resultado del criterio de la comisión de Biologia Celular y Molecular.
        :return objeto EvaluacionAcreditacionBiologiaCelularYMolecular con los resltados del criterio de la comisión de Biologia Celular y Molecular.
        """
        eval = self.get_evaluacion_titularidad_B(produccion_cientifica, eval)
        if not eval.positiva:
            eval = self.get_evaluacion_titularidad_C(produccion_cientifica, eval)
            if not eval.positiva:
                eval = self.get_evaluacion_titularidad_D(produccion_cientifica, eval)
        return eval

    def criterio_num_publicaciones(self, produccion_cientifica, num_publicaciones) -> bool:
        """
        Método encargado de comprobar si se cumple que la producción científica tenga el número de publicaciones pasado por parámetro.
        """
        return len(produccion_cientifica) >= num_publicaciones

    def criterio_T1(self, produccion_cientifica, num_publicaciones):
        """
        Método que comprueba los artículos que pertenecen al tercil 1,
        devuelve una tupla donde el primer valor es un booleano que nos dice si se cumple el criterio
        y el segundo la lista de publicaciones obtenidas.
        """
        publicaciones = []
        result: bool = False
        if produccion_cientifica:
            for art in produccion_cientifica:
                if art.get_tercil() == 1:
                    publicaciones.append(art)

            if len(publicaciones) >= num_publicaciones:
                result = True
        return (result, publicaciones)

    def criterio_autoria_preferente(self, produccion_cientifica, num_publicaciones):
        """
        Método que comprueba el criterio de autoria preferente
        (Primer/a firmante, coautoría, ultimo/a firmante y autor/a de correspondencia).
        """
        publicaciones = []
        result: bool = False
        if produccion_cientifica:
            for art in produccion_cientifica:
                if (len(publicaciones) < num_publicaciones) and (art.posicion_autor == 1 or (art.posicion_autor == art.nautores)):
                    publicaciones.append(art)
        
        if publicaciones and len(publicaciones) == num_publicaciones:
            result = True

        return (result, publicaciones)
    
    def create_observacion_B(self, eval: EvaluacionAcreditacionBiologCelularMolecular, 
        valoracion:str) -> str:
        """
        Método que construye el mensaje que se mostrará si no se cumplen los criterios para
        la valoración B
        """
        observacion = 'Es posible que no alcance la valoración ' + valoracion+ ' porque se han obtenido los siguientes resultados: \n' + \
            'Número de publicaciones obtenidas necesarias: ' + str(eval.criterio.minimo_articulos_100) + ' obtenidas: ' + str(len(eval.produccion_cientifica)) + '\n' + \
            'T1, necesarias: ' + str(eval.criterio.num_t1_100) + ' obtenidas: '
        if eval.publicaciones_t1:
            observacion += str(len(eval.publicaciones_t1)) + '\n'
        else:
            observacion += '0 \n'
        observacion += 'Autoría preferente, necesarias: ' + \
            str(eval.criterio.num_autoria_100) + ' obtenidas: '
        if eval.publicaciones_autoria_preferente:
            observacion += str(len(eval.publicaciones_autoria_preferente)) + '\n'
        else:
            observacion += '0 \n'

        return observacion

    def create_observacion_C(self, eval: EvaluacionAcreditacionBiologCelularMolecular, valoracion:str) -> str:
        """
        Método que construye el mensaje que se mostrará si no se cumplen los criterios para
        la valoración C
        """
        observacion = 'Es posible que no alcance la valoración ' + valoracion+ ' porque se han obtenido los siguientes resultados: \n' + \
            'Número de publicaciones obtenidas necesarias: ' + str(eval.criterio.minimo_articulos_100) + \
            '-' + str(eval.criterio.num_autoria_75) + ' obtenidas: ' + \
            str(len(eval.produccion_cientifica)) + '\n' + \
            'T1, necesarias: ' + str(eval.criterio.num_t1_100) + '-' + \
            str(eval.criterio.num_t1_75) + ' obtenidas: '
        
        if eval.publicaciones_t1:
            observacion += str(len(eval.publicaciones_t1)) + '\n'
        else:
            observacion += '0 \n'

        observacion += 'Autoría preferente, necesarias: ' + \
            str(eval.criterio.num_autoria_100) + '-' + str(eval.criterio.num_autoria_75) + ' obtenidas: '
        if eval.publicaciones_autoria_preferente:
            observacion += str(len(eval.publicaciones_autoria_preferente)) + '\n'
        else:
            observacion += '0 \n'

        return observacion

    def get_evaluacion_catedra_B(self, produccion_cientifica, eval:EvaluacionAcreditacionBiologCelularMolecular) -> EvaluacionAcreditacionBiologCelularMolecular:
        """
        Método que evalúa los criterios de la cátedra con calificación B
        """
        criterios_completos = 0
        if produccion_cientifica: 
            if self.criterio_num_publicaciones(produccion_cientifica, eval.criterio.minimo_articulos_100):
                criterios_completos += 1
            
            tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_100)
            if tupla_c2:
                eval.publicaciones_t1 = tupla_c2[1]
                if tupla_c2[0]:
                    criterios_completos += 1

            tupla_autoria = self.criterio_autoria_preferente(
                    produccion_cientifica, eval.criterio.num_autoria_100)
            if tupla_autoria:
                eval.publicaciones_autoria_preferente = tupla_autoria[1]
                if tupla_autoria[0]:
                    criterios_completos += 1

            if criterios_completos == 3:
                eval.positiva = True
                eval.valoracion_alcanzada = 'B'

        if not eval.positiva:
            eval.observaciones += self.create_observacion_B(eval, 'B')
        return eval

    def get_evaluacion_catedra_C(self, produccion_cientifica,
         eval:EvaluacionAcreditacionBiologCelularMolecular) -> EvaluacionAcreditacionBiologCelularMolecular:
        """
        Método que evalúa los criterios de la cátedra con calificación C
        """
        if produccion_cientifica:
            criterios_completos = 0
            criterios_b = 0
            if self.criterio_num_publicaciones(produccion_cientifica, eval.criterio.minimo_articulos_100):
                criterios_completos += 1
            elif self.criterio_num_publicaciones(produccion_cientifica, eval.criterio.minimo_articulos_75):
                criterios_b += 1
            
            tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_100)
            if tupla_c2 and tupla_c2[0]:
                criterios_completos += 1                
                eval.publicaciones_t1 = tupla_c2[1]
            else:
                tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_75)
                if tupla_c2[0]:
                    criterios_b += 1                
                    eval.publicaciones_t1 = tupla_c2[1]

            if criterios_completos != 2:
                tupla_autoria = self.criterio_autoria_preferente(
                        produccion_cientifica,eval.criterio.num_autoria_100)
                if tupla_autoria:
                    if tupla_autoria[0]:
                        criterios_completos += 1
                    eval.publicaciones_autoria_preferente = tupla_autoria[1]
            
            elif criterios_b != 1:
                tupla_autoria = self.criterio_autoria_preferente(
                        produccion_cientifica,eval.criterio.num_autoria_75)
                if tupla_autoria:
                    if tupla_autoria[0]:
                        criterios_b += 1
                    eval.publicaciones_autoria_preferente = tupla_autoria[1]

            if criterios_completos >= 2 and criterios_b >= 1:
                eval.positiva = True
                eval.valoracion_alcanzada = 'C'

        if not eval.positiva:
            eval.observaciones += self.create_observacion_C(eval, 'C')
        
        return eval

    def get_evaluacion_catedra_D(self, produccion_cientifica, eval:EvaluacionAcreditacionBiologCelularMolecular) -> EvaluacionAcreditacionBiologCelularMolecular:
        """
        Método que evalúa los criterios de la cátedra con calificación D
        """
        if produccion_cientifica:
            criterios_completos = 0
            criterios_b = 0
            if self.criterio_num_publicaciones(produccion_cientifica, eval.criterio.minimo_articulos_100):
                criterios_completos += 1
            elif self.criterio_num_publicaciones(produccion_cientifica, eval.criterio.num_autoria_75):
                criterios_b += 1
            
            if criterios_completos == 1:
                tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_75)
                if tupla_c2:
                    if tupla_c2[0]:
                        criterios_b += 1                
                    eval.publicaciones_t1 = tupla_c2[1] 

                tupla_autoria = self.criterio_autoria_preferente(
                        produccion_cientifica,eval.criterio.num_autoria_75)
                if tupla_autoria:
                    if tupla_autoria[0]:
                        criterios_b += 1
                    eval.publicaciones_autoria_preferente = tupla_autoria[1]               

            else: 
                tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_100)
                if tupla_c2:
                    if tupla_c2[0]:
                        criterios_completos += 1                
                    eval.publicaciones_t1 = tupla_c2[1]
                else:
                    tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_75)
                    if tupla_c2:
                        if tupla_c2[0]:
                            criterios_b += 1                
                        eval.publicaciones_t1 = tupla_c2[1]
                
                tupla_autoria = self.criterio_autoria_preferente(
                        produccion_cientifica,eval.criterio.num_autoria_75)
                if tupla_autoria:
                    if tupla_autoria[0]:
                        criterios_b += 1
                    eval.publicaciones_autoria_preferente = tupla_autoria[1]  

            if criterios_completos >= 1 and criterios_b >= 2:
                eval.positiva = True
                eval.valoracion_alcanzada = 'D'

        if not eval.positiva:
            eval.observaciones += self.create_observacion_C(eval, 'D')
        
        return eval

    def get_evaluacion_titularidad_B(self, produccion_cientifica, eval:EvaluacionAcreditacionBiologCelularMolecular) -> EvaluacionAcreditacionBiologCelularMolecular:
        """
        Método que evalúa los criterios de la titularidad con calificación B
        """
        criterios_completos = 0
        if produccion_cientifica: 
            if self.criterio_num_publicaciones(produccion_cientifica, eval.criterio.minimo_articulos_100):
                criterios_completos += 1
            
            tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_100)
            if tupla_c2:
                eval.publicaciones_t1 = tupla_c2[1]
                if tupla_c2[0]:
                    criterios_completos += 1

            tupla_autoria = self.criterio_autoria_preferente(
                    produccion_cientifica,eval.criterio.num_autoria_100)
            
            if tupla_autoria:
                eval.publicaciones_autoria_preferente = tupla_autoria[1]
                if tupla_autoria[0]:
                    criterios_completos += 1

            if criterios_completos == 3:
                eval.positiva = True
                eval.valoracion_alcanzada = 'B'

        if not eval.positiva:
            eval.observaciones += self.create_observacion_B(eval, 'B')
        return eval
    
    def get_evaluacion_titularidad_C(self, produccion_cientifica, eval:EvaluacionAcreditacionBiologCelularMolecular) -> EvaluacionAcreditacionBiologCelularMolecular:
        """
        Método que evalúa los criterios de la titularidad con calificación C
        """
        if produccion_cientifica:
            criterios_completos = 0
            criterios_b = 0
            if self.criterio_num_publicaciones(produccion_cientifica, eval.criterio.minimo_articulos_100):
                criterios_completos += 1
            elif self.criterio_num_publicaciones(produccion_cientifica, eval.criterio.minimo_articulos_75):
                criterios_b += 1
            
            tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_100)
            if tupla_c2 and tupla_c2[0]:
                criterios_completos += 1                
                eval.publicaciones_t1 = tupla_c2[1]
            else:
                tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_75)
                if tupla_c2[0]:
                    criterios_b += 1                
                    eval.publicaciones_t1 = tupla_c2[1]

            if criterios_completos < 2:
                tupla_autoria = self.criterio_autoria_preferente(
                        produccion_cientifica,eval.criterio.num_autoria_100)
                if tupla_autoria:
                    if tupla_autoria[0]:
                        criterios_completos += 1
                    eval.publicaciones_autoria_preferente = tupla_autoria[1]
            
            elif criterios_b < 1:
                tupla_autoria = self.criterio_autoria_preferente(
                        produccion_cientifica,eval.criterio.num_autoria_75)                
                if tupla_autoria: 
                    if tupla_autoria[0]:
                        criterios_b += 1
                    eval.publicaciones_autoria_preferente = tupla_autoria[1]

            if criterios_completos >= 2 and criterios_b >= 1:
                eval.positiva = True
                eval.valoracion_alcanzada = 'C'

        if not eval.positiva:
            eval.observaciones += self.create_observacion_C(eval, 'C')
        
        return eval
   
    def get_evaluacion_titularidad_D(self, produccion_cientifica, eval:EvaluacionAcreditacionBiologCelularMolecular) -> EvaluacionAcreditacionBiologCelularMolecular:
        """
        Método que evalúa los criterios de la titularidad con calificación D
        """
        if produccion_cientifica:
            criterios_completos = 0
            criterios_b = 0
            if self.criterio_num_publicaciones(produccion_cientifica, eval.criterio.minimo_articulos_100):
                criterios_completos += 1
            elif self.criterio_num_publicaciones(produccion_cientifica, eval.criterio.minimo_articulos_75):
                criterios_b += 1
            
            if criterios_completos == 1:
                tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_75)
                if tupla_c2:
                    if tupla_c2[0]:
                        criterios_b += 1                
                    eval.publicaciones_t1 = tupla_c2[1] 

                tupla_autoria = self.criterio_autoria_preferente(
                        produccion_cientifica,eval.criterio.num_autoria_75)
                if tupla_autoria:
                    if tupla_autoria[0]:
                        criterios_b += 1
                    eval.publicaciones_autoria_preferente = tupla_autoria[1]               

            else: 
                tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_100)
                if tupla_c2:
                    if tupla_c2[0]:
                        criterios_completos += 1                
                    eval.publicaciones_t1 = tupla_c2[1]
                else:
                    tupla_c2 = self.criterio_T1(produccion_cientifica, eval.criterio.num_t1_75)
                    if tupla_c2:
                        if tupla_c2[0]:
                            criterios_b += 1                
                        eval.publicaciones_t1 = tupla_c2[1]
                
                tupla_autoria = self.criterio_autoria_preferente(
                        produccion_cientifica,eval.criterio.num_autoria_75)
                if tupla_autoria:
                    if tupla_autoria[0]:
                        criterios_b += 1
                    eval.publicaciones_autoria_preferente = tupla_autoria[1]  

            if criterios_completos >= 1 and criterios_b >= 2:
                eval.positiva = True
                eval.valoracion_alcanzada = 'D'

        if not eval.positiva:
            eval.observaciones += self.create_observacion_C(eval, 'D')        
        return eval