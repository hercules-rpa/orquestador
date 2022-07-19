import model.process.Proceso4.model.ClassProcess4 as p4
import model.process.Proceso4.SRControlador as SRControlador
import pandas as pd
import numpy as np
import time
from aiohttp import request
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID


NAME = "Sistema de Recomendación Filtro Colaborativo"
DESCRIPTION = "Filtro Colaborativo basado en items"
REQUIREMENTS = ['pandas', 'numpy']
ID = ProcessID.COLLABORATIVE_FILTERING.value


class ProcessFiltroColaborativo(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def execute(self):
        self.log.state = "OK"
        self.state = pstatus.RUNNING
        self.log.start_log(time.time())
        self.update_log(
            "Proceso de recomendación Filtro Colaborativo ha empezado", True)
        self.log.completed = 5
        self.result = None
        # PRIMERA PARTE
        self.update_log("Obtenemos todas las calificaciones", True)
        # para buscar similitudes, podria ser que no esten todos los investigadores
        investigador_all_calificaciones = SRControlador.get_all_calificacion()
        self.update_log(investigador_all_calificaciones.to_string(), True)
        convocatoria = self.parameters['convocatoria']
        investigadores = self.parameters['investigadores']
        self.update_log(
            "Obtenemos las áreas de entrada, excepto el nodo raíz", True)
        inputAreas = self.__get_input_area(convocatoria)
        self.log.completed = 20
        result_recomendacion = self.recomedacion_filtro_colaborativo(
            inputAreas, investigador_all_calificaciones, investigadores)
        self.result = result_recomendacion
        self.update_log("Resultado:", True)
        self.update_log(str(self.result), True)
        self.update_log(
            "Proceso Filtro Colaborativo Finalizado Correctamente", True)
        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED

    def __get_input_area(self, convocatoria: p4.Convocatoria):
        '''Obtenemos un dataframe con las areas tematicas que serán usadas como inputs para el sistema de recomendación'''
        areasTematicas = convocatoria.areaTematica
        #Columnas. idInv, area, calificacion
        inputAreas = pd.DataFrame({"areaId": [], "nombre": []})
        for areaTematica in areasTematicas:
            areaTematica = areaTematica.areaHijo  # Nos quitamos la fuente
            while areaTematica:
                row = [areaTematica.id, areaTematica.nombre]
                inputAreas.loc[len(inputAreas)] = row
                areaTematica = areaTematica.areaHijo
        self.update_log(inputAreas.to_string(), True)
        return inputAreas

    def recomedacion_filtro_colaborativo(self, inputAreas, df_calificaciones, investigadores, threshold_count=25):
        ''' Pivotamos esta tabla para crear una matriz que tiene  una fila por cada usuario  
            una columna por cada area tematica en la celda que se cruzan esta la puntuacion que le dio, 
            si es que la valoró '''
        df_calificaciones_pivot = df_calificaciones.pivot_table(
            index=['invId'], columns=['areaId'], values='rating')
        self.update_log("Calificaciones Investigadores, matriz pivotada", True)
        self.update_log(df_calificaciones_pivot.to_string(), True)
        corrMatrix = df_calificaciones_pivot.corr(
            method='pearson', min_periods=threshold_count)
        self.update_log("Matriz de correlación", True)
        self.update_log(str(corrMatrix), True)
        notificacion_investigador = {}  # key: investigador, value: puntuacion.
        for inv in investigadores:
            notificacion_investigador[inv.id] = []
            for areaId in inputAreas['areaId'].tolist():
                df_calificaciones_group = df_calificaciones['areaId'].value_counts(
                )
                if not areaId in df_calificaciones_group.index or df_calificaciones_group[areaId] < threshold_count:
                    self.update_log(
                        "No hay suficientes puntuaciones para usar el motor de recomendacion con el área "+str(areaId)+". Se procederá por heuristica", True)
                    self.update_log(
                        "Le enviaremos la convocatoria aquellos investigadores que la hayan puntuado con igual o más de un 2.5, y a aquellos que no la han puntuado", True)
                    if not inv.id in df_calificaciones_pivot.index:
                        notificacion_investigador[inv.id].append(1)
                    else:
                        investigador = df_calificaciones_pivot.loc[inv.id]

                        if areaId in investigador.index and (not np.isnan(investigador[areaId])):
                            # print("testing")
                            # print(investigador)
                            # print(inv.id)
                            # print(areaId)
                            # print(investigador.index)
                            # print(investigador[areaId])
                            # print(inputAreas)
                            normalized_value = (investigador[areaId] - 0)/(5)
                            notificacion_investigador[inv.id].append(
                                normalized_value)
                        else:
                            notificacion_investigador[inv.id].append(1)
                else:
                    self.update_log(
                        "Hay suficientes puntuaciones para usar el motor de recomendacion.", True)
                    if not inv.id in df_calificaciones_pivot.index:
                        # Si el investigador no tiene nada le mandamos, nos aseguramos que se envie la convocatoria.
                        notificacion_investigador[inv.id].append(1)
                    else:
                        print(df_calificaciones_pivot.loc[inv.id])
                        investigador = df_calificaciones_pivot.loc[inv.id]
                        areasCandidatas = pd.Series(dtype='float64')
                        # Recorremos las areas valoradas por el usuario
                        for i in range(0, len(investigador.index)):
                            sims = corrMatrix[investigador.index[i]].dropna()
                            sims = sims.map(
                                lambda x: x * investigador[investigador.index[i]])
                            areasCandidatas = pd.concat(
                                [areasCandidatas, sims])
                        areasCandidatas = areasCandidatas.groupby(
                            areasCandidatas.index).sum()
                        areasCandidatas.sort_values(
                            inplace=True, ascending=False)
                        if areaId in areasCandidatas.index:
                            # print("Valor del area candidata")
                            # print("Rating ", areasCandidatas[areaId])
                            # print("Posicion ",areasCandidatas.index.get_loc(areaId), "de", len(areasCandidatas.index))
                            if (areasCandidatas.max() - areasCandidatas.min()) <= 0:
                                normalized_value = 0
                            else:
                                normalized_value = (areasCandidatas[areaId] - areasCandidatas.min())/(
                                    areasCandidatas.max() - areasCandidatas.min())  # Normalizamos entre 0 y 1
                            notificacion_investigador[inv.id].append(
                                normalized_value)
                            # if areasCandidatas[areaId] > areasCandidatas.quantile([0.25,0.5,0.75]).values[1]: #este por encima de la media
                            #     # print("Recomendamos la pelicula porque esta por encima de la media")
                            #     # print("Recomendar ",areaId, " al investigador ",inv.id)
                            #     # notificacion_investigador[str(int(areaId))].append(inv.id)
                            #     print("Area por encima de la media")
                        else:
                            print("No aparece ese area id")
            if len(notificacion_investigador[inv.id]) > 0:
                notificacion_investigador[inv.id] = np.mean(
                    notificacion_investigador[inv.id])

        return notificacion_investigador

    def pause(self):
        pass

    def kill(self):
        pass

    def resume(self):
        pass
