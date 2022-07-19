import json
import pandas as pd
from datetime import datetime, timedelta
from model.EDMA import EDMA
import model.SGI as SGI
from model.process.ProcessCommand import ProcessCommand
import model.process.Proceso4.model.ClassProcess4 as p4
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
import model.process.Proceso4.SRControlador as SRControlador
import time

# El proceso debe devolver. key: investigador, value: [(puntuacion, None)]
NAME = "Sistema de Recomendación Basado en Contenido"
DESCRIPTION = "Basado en Contenido, obtiene las convococatorias del investigador para ver la similitud con la convocatoria a notificar"
REQUIREMENTS = ['pandas', 'numpy', 'sklearn']
ID = ProcessID.BASED_CONTENT.value


class ProcessSRContenido(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)
        self.flag = False

    def execute(self):
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.update_log(
            "Se procede a ejecutar Sistema Recomendación Basado en Contenido", True)
        self.log.completed = 5
        self.result = None

        convocatoria = self.parameters['convocatoria']

        if not self.flag:
            self.update_log(
                "Procesamos la información de los investigadores para hacer la similitud", True)
            investigadores_solicitudes = self.process_investigadores()

        # Procesamos la convocatoria de la forma que nos interesa
        process_convo = self.get_format_convocatoria(convocatoria.id)
        self.update_log(
            "Convocatoria de entrada: "+str(process_convo), True)
        self.log.completed = 50

        investigadores_puntuacion = self.SR_contenido(
            process_convo, investigadores_solicitudes)
        self.result = investigadores_puntuacion
        self.update_log("Resultado:", True)
        self.update_log(str(self.result), True)
        self.update_log(
            "Proceso Sistema de Recomendación Basado en Contenido finalizado correctamente", True)
        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED

    def get_idinvestigador_sgi(self, email):
        ed = EDMA()
        # r = sgi.get_persona_filter("?q=email=="+email)
        r = ed.get_personaref(email)
        return r

    def get_solicitudes_convocatoria(self, idref):
        sgi = SGI.SGI()
        r = sgi.get_solicitudes("solicitanteRef=="+str(idref))
        convocatorias = []
        if r and len(r) > 0:
            solicitudes = json.loads(r)
            for solicitud in solicitudes:
                convocatoria = solicitud['convocatoriaId']
                if convocatoria:
                    convocatorias.append(convocatoria)
        return convocatorias

    def __get_areamaticas(self, areas):
        '''Obtenemos el area tematica de las convocatorias'''
        areas_tematicas = []
        for area in areas:
            if area:
                at_dict = area['areaTematica']
                areas_tematicas.append(at_dict['nombre'])
                padre = at_dict['padre']
                while padre:
                    areas_tematicas.append(padre['nombre'])
                    at_dict = padre
                    padre = at_dict['padre']
        return areas_tematicas

    def get_format_convocatoria(self, id):
        sgi = SGI.SGI()
        convocatoria_base = json.loads(sgi.get_convocatoria(id))
        convocatoria_entidad_convo = sgi.get_entidades_convocantes_convocatoria(
            id)
        convocatoria_entidad_finan = sgi.get_entidades_financiadora_convocatoria(
            id)
        convocatoria_areas = sgi.get_convocatoria_area_tematica(id)
        finalidad = convocatoria_base['finalidad']
        clasificacionCVN = convocatoria_base['clasificacionCVN']

        if convocatoria_entidad_convo and len(convocatoria_entidad_convo) > 0:
            convocatoria_entidad_convo = json.loads(
                convocatoria_entidad_convo)

        if convocatoria_entidad_finan and len(convocatoria_entidad_finan) > 0:
            convocatoria_entidad_finan = json.loads(
                convocatoria_entidad_finan)

        if convocatoria_areas and len(convocatoria_areas) > 0:
            convocatoria_areas = json.loads(convocatoria_areas)

        areastematicas = self.__get_areamaticas(convocatoria_areas)
        entidades_convocante = []
        entidades_finan = []
        modelo_ejecucion = []
        objeto = []

        if finalidad:
            finalidad = finalidad['nombre']
        else:
            finalidad = ""

        if not clasificacionCVN:
            clasificacionCVN = ""

        if convocatoria_entidad_convo:
            for entidad_convocante in convocatoria_entidad_convo:
                if entidad_convocante['programa']:
                    entidades_convocante.append(
                        entidad_convocante['programa']['nombre'])
                    if sgi.get_empresa(entidad_convocante['entidadRef']):
                        empresa_nombre = json.loads(sgi.get_empresa(
                            entidad_convocante['entidadRef']))['nombre']
                    else:
                        empresa_nombre = ""
                    entidades_convocante.append(empresa_nombre)


        if convocatoria_entidad_finan:
            for entidad_finan in convocatoria_entidad_finan:
                if sgi.get_empresa(entidad_finan['entidadRef']):
                    empresa_nombre = json.loads(sgi.get_empresa(
                        entidad_finan['entidadRef']))['nombre']
                else:
                    empresa_nombre = ""
                entidades_finan.append(empresa_nombre)

        if convocatoria_base['modeloEjecucion']:
            modelo_ejecucion.append(
                convocatoria_base['modeloEjecucion']['nombre'])

        if convocatoria_base['objeto']:
            objeto.append(convocatoria_base['objeto'])

        lista_global = []
        lista_global.append(areastematicas)
        lista_global.append([finalidad])
        lista_global.append([clasificacionCVN])
        lista_global.append(entidades_finan)
        lista_global.append(entidad_convocante)
        lista_global.append(modelo_ejecucion)
        lista_global.append(objeto)
        atributos_convocatoria = []
        for l in lista_global:
            if len(l) > 0:
                atributos_convocatoria += l

        return [" ".join(atributos_convocatoria)]

    def SR_contenido(self, process_convo, investigadores_input, threshold_count=5, test=False):
        '''Función que realiza la similitud de las convocatorias (sistema de recomendación basado en contenido)
        espera recibir un diccionario del tipo: "id_investigador (bbdd interno): string words convocatoria"
        return diccionario del tipo: "id_investigador: puntuacion"
        '''
        investigadores = {}
        for key, value in investigadores_input.items():
            process_convocatorias_old = pd.DataFrame({"words": value})

            if len(process_convocatorias_old) <= threshold_count:
                if test:
                    investigadores[key] = 1
                    continue
                convocatoria = self.parameters['convocatoria']
                puntuaciones = SRControlador.get_calificacion(
                    key, convocatoria)
                if len(puntuaciones['rating']) > 0:
                    normalized_value = (
                        np.mean(puntuaciones['rating']) - 0)/(5)
                    investigadores[key] = normalized_value
                else:
                    # Marcamos valor maximo porque no sabemos si le interesa o no. No tenemos informacion suficiente
                    investigadores[key] = 1
                continue
            count = CountVectorizer()

            process_convocatorias_old.loc[len(
                process_convocatorias_old)] = process_convo

            count_matrix = count.fit_transform(
                process_convocatorias_old['words'])
            cosine_sim = cosine_similarity(count_matrix, count_matrix)
            self.update_log(
                "Similaridad del coseno: "+str(cosine_sim), True)
            similitud = cosine_sim[len(cosine_sim)-1]
            # eliminamos el ultimo valor porque es la misma convocatoria de entrada y no nos interesa contarlo
            similitud = similitud[0:len(similitud) - 1]
            # obtenemos los indices del numero de thresholds mas grandes
            ind = np.argpartition(
                similitud, -threshold_count)[-threshold_count:]
            # nos quedamos con los valores mas grandes y el numero del threshold para hacer la comparativa
            similitud = similitud[ind]
            similitud_value = np.mean(similitud)
            investigadores[key] = similitud_value
        return investigadores

    def process_investigadores(self):
        investigadores_solicitudes = {}
        for inv in self.parameters['investigadores']:
            id_ref = self.get_idinvestigador_sgi(inv.email)
            convocatorias_old = []
            if id_ref:
                convocatorias_old = self.get_solicitudes_convocatoria(id_ref)
            process_convocatorias_old = []
            for c_old in convocatorias_old:
                row = self.get_format_convocatoria(c_old)
                if len(row) > 0:
                    process_convocatorias_old.append(row)
                    # print("Investigador id", inv.id)
                    # print(process_convocatorias_old)
            investigadores_solicitudes[inv.id] = process_convocatorias_old
        self.flag = True
        return investigadores_solicitudes

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
