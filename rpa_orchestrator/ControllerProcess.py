from dataclasses import dataclass
import rpa_orchestrator.lib.dbprocess.dbcon as dbprocess
import json
import numpy as np
import rpa_orchestrator.lib.dbprocess.models as model
from datetime import datetime
import model.SGI as SGI
import model.process.Process4.RSController as RSController
from model.process.Process4.model.ClassProcess4 import Investigador
import glob

DIRECTORY_PROCESS_CONFIG = 'model/process/Process*'
SUBPATH_PROCESS_CONFIG   = 'Configurations/*.json'
SUBPATH_PROCESS_DEFAULT_CONFIG   = 'static'


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ControllerProcess(metaclass=Singleton):
    def __init__(self):
        self.dbprocess = dbprocess.ControllerDBProcess()

    def get_convocatoria(self, filters=None):
        models_convocatoria = self.dbprocess.read_convocatoria(filters)
        convocatoria_dict = [x.__dict__ for x in models_convocatoria]
        if len(convocatoria_dict) == 0:
            return None
        for x in convocatoria_dict:
            del x['_sa_instance_state']
            x['fecha_creacion'] = datetime.timestamp(x['fecha_creacion'])
            if x['fecha_publicacion']:
                x['fecha_publicacion'] = datetime.timestamp(
                    x['fecha_publicacion'])
        return json.dumps(convocatoria_dict)

    def get_solicitud(self, filters=None):
        models_solicitud = self.dbprocess.read_solicitud(filters)
        solicitud_dict = [x.__dict__ for x in models_solicitud]
        if len(solicitud_dict) == 0:
            return None
        for x in solicitud_dict:
            del x['_sa_instance_state']
            x['fecha_creacion'] = datetime.timestamp(x['fecha_creacion'])
        return json.dumps(solicitud_dict)

    def get_basereguladora(self, filters=None):
        models_basereguladora = self.dbprocess.read_basereguladora(filters)
        basereguladora_dict = [x.__dict__ for x in models_basereguladora]
        if len(basereguladora_dict) == 0:
            return None
        for x in basereguladora_dict:
            del x['_sa_instance_state']
            x['fecha_creacion'] = datetime.timestamp(x['fecha_creacion'])
        return json.dumps(basereguladora_dict)

    def get_ejecucion_boletin(self, filters=None):
        models_notificacion = self.dbprocess.read_ejecucion_notificacion(
            filters)
        notificacion_dict = [x.__dict__ for x in models_notificacion]
        if len(notificacion_dict) == 0:
            return None
        for x in notificacion_dict:
            del x['_sa_instance_state']
            x['fecha_inicio'] = datetime.timestamp(x['fecha_inicio'])
            x['fecha_fin'] = datetime.timestamp(x['fecha_fin'])
            x['fecha_ejecucion'] = datetime.timestamp(x['fecha_ejecucion'])
        return json.dumps(notificacion_dict)

    def get_ejecucion_boletin_ultima(self, filters=None):
        models_notificacion = self.dbprocess.read_ejecucion_notificacion(
            filters)
        notificacion_dict = [x.__dict__ for x in models_notificacion]
        if len(notificacion_dict) == 0:
            return None
        for x in notificacion_dict:
            del x['_sa_instance_state']
            x['fecha_inicio'] = datetime.timestamp(x['fecha_inicio'])
            x['fecha_fin'] = datetime.timestamp(x['fecha_fin'])
            x['fecha_ejecucion'] = datetime.timestamp(x['fecha_ejecucion'])
        return json.dumps(notificacion_dict[-1])

    def get_notificacion(self, filters=None):
        models_notificacion = self.dbprocess.read_notificacion(filters)
        notificacion_dict = [x.__dict__ for x in models_notificacion]
        if len(notificacion_dict) == 0:
            return None
        for x in notificacion_dict:
            del x['_sa_instance_state']
            x['fecha_inicio'] = datetime.timestamp(x['fecha_inicio'])
            x['fecha_fin'] = datetime.timestamp(x['fecha_fin'])
            x['fecha_ejecucion'] = datetime.timestamp(x['fecha_ejecucion'])
        return json.dumps(notificacion_dict)

    def get_areatematica(self, filters=None):
        models_areatematica = self.dbprocess.read_areatematica(filters)
        areatematica_dict = [x.__dict__ for x in models_areatematica]
        areastematicas = []
        if len(areatematica_dict) == 0:
            return None
        for x in areatematica_dict:
            #del x['_sa_instance_state']
            at = self.get_areatematica_id(x['id'])
            if at:
                areastematicas.append(json.loads(at))
        return json.dumps(areastematicas)

    def get_areatematica_pretty(self, idinv):
        area_result = []
        area = {}
        areastematicas = json.loads(self.get_areatematica(None))
        area_fuente = []
        areas_root = {}
        if areastematicas:
            for areatematica in areastematicas:
                if areatematica['nombre'] == areatematica['fuente']:
                    if len(area) != 0:
                        area_result.append(area)
                        area = {}
                    area['fuente'] = True
                    area['nombre'] = areatematica['nombre']
                    if areatematica['descripcion'] == "":
                        area['descripcion'] = areatematica['nombre']
                    else:
                        area['descripcion'] = areatematica['descripcion']
                    area['id'] = areatematica['id']
                    area['puntuacion'] = 0
                    area[areatematica['id']] = []
                    area_fuente.append(areatematica['id'])
                    # Las guardamos en referencia para acceder posteriormente a ellas
                    areas_root[area['id']] = area
                else:
                    area_hijo = {}
                    area_hijo['fuente'] = False
                    area_hijo['nombre'] = areatematica['nombre']
                    if areatematica['descripcion'] == "":
                        area_hijo['descripcion'] = areatematica['nombre']
                    else:
                        area_hijo['descripcion'] = areatematica['descripcion']
                    area_hijo['descripcion'] = areatematica['descripcion']
                    area_hijo['id'] = areatematica['id']
                    filter = {}
                    filter['idinvestigador'] = idinv
                    filter['idarea'] = areatematica['id']
                    puntuacion_area = self.get_calificacionArea(filter)
                    if len(puntuacion_area) > 0:
                        puntuacion_area = json.loads(
                            puntuacion_area)
                        area_hijo['puntuacion'] = puntuacion_area[0]['puntuacion']
                    else:
                        area_hijo['puntuacion'] = 0
                    area_hijo[areatematica['id']] = []

                    if areatematica['hijos']:
                        area_hijo = self._insert_area_dict(
                            areatematica['hijos'], area_hijo, idinv)

                    if areatematica['padre'] in area_fuente:
                        (areas_root[areatematica['padre']])[areatematica['padre']].append(
                            area_hijo)  # similar a area[areatematica['padre']].append(area_hijo)

            area_result.append(area)
            return json.dumps(area_result)

    def _insert_area_dict(self, id_areas, area_dict, idinv):
        for id_area in id_areas:
            area_hijo = {}
            at = json.loads(self.get_areatematica_id(id_area))
            area_hijo['fuente'] = False
            area_hijo['nombre'] = at['nombre']
            if at['descripcion'] == "":
                area_hijo['descripcion'] = at['nombre']
            else:
                area_hijo['descripcion'] = at['descripcion']
            area_hijo['id'] = at['id']
            filter = {}
            filter['idinvestigador'] = idinv
            filter['idarea'] = at['id']
            puntuacion_area = self.get_calificacionArea(filter)
            if len(puntuacion_area) > 0:
                puntuacion_area = json.loads(
                    puntuacion_area)
                area_hijo['puntuacion'] = puntuacion_area[0]['puntuacion']
            else:
                area_hijo['puntuacion'] = 0
            area_hijo[at['id']] = []
            if at['hijos']:
                self._insert_area_dict(at['hijos'], area_hijo, idinv)
            area_dict[at['padre']].append(area_hijo)
        return area_dict

    # Calculamos la puntuacion del nodo padre con la media de los hijos. Necesitaremos dos funciones para la recursividad
    def calcular_puntuaciones_areas(self, areas_puntuaciones: model.Calificacionarea):
        area_calculada = []
        flag_perfil = False
        for area_puntuacion in areas_puntuaciones:
            if not flag_perfil: #Indicamos que ha configurado el perfil de esta forma no le llegaran correos de que debe configurar su perfil
                self.update_investigador(area_puntuacion.idinvestigador, {"perfil": True})
                flag_perfil = True
            area_tematica = json.loads(
                self.get_areatematica_id(area_puntuacion.idarea))
            flag = True
            #Comprobamos si el area solo es la root.
            if not area_tematica['padre']:
                area_tematica_padre = json.loads(self.get_areatematica_id(area_tematica['padre']))
                self.dump([model.Calificacionarea(idinvestigador=area_puntuacion.idinvestigador, idarea=area_tematica_padre['id'], puntuacion=np.mean(puntuaciones))])
                flag = False
            # Obtenemos el nodo padre del todo sin llegar al nodo root y pasamos a la funcion de recursividad
            while flag:
                if area_tematica['padre']:
                    area_tematica_padre = json.loads(
                        self.get_areatematica_id(area_tematica['padre']))
                    if area_tematica_padre['fuente'] != area_tematica_padre['nombre']:
                        area_tematica = area_tematica_padre
                    else:
                        if not area_tematica['id'] in area_calculada:
                            self.__calcular_puntuaciones_areas_rec(
                                area_tematica, area_puntuacion.idinvestigador)
                            area_calculada.append(area_tematica['id'])
                        flag = False
                else:
                    flag = False
                    
        

    # funcion recursiva que obtiene la puntuaciones de los hijos. Si un hijo tiene hijo aplicamos la recursividad para sacar la puntuacion
    def __calcular_puntuaciones_areas_rec(self, area, idinv):
        puntuaciones = []
        if area['hijos']:
            for idhijo in area['hijos']:
                area_tematica_hijo = json.loads(
                    self.get_areatematica_id(idhijo))
                if area_tematica_hijo['hijos']:
                    self.__calcular_puntuaciones_areas_rec(
                        area_tematica_hijo, idinv)
                else:
                    filter = {}
                    filter['idinvestigador'] = idinv
                    filter['idarea'] = idhijo
                    puntuacion_area = self.get_calificacionArea(filter)
                    if len(puntuacion_area) > 0:
                        puntuacion_area = json.loads(puntuacion_area)
                        puntuaciones.append(puntuacion_area[0]['puntuacion'])
                    else:
                        puntuaciones.append(0)
        else:  # No tiene hijos
            filter = {}
            filter['idinvestigador'] = idinv
            filter['idarea'] = area['id']
            puntuacion_area = self.get_calificacionArea(filter)
            if len(puntuacion_area) > 0:
                puntuacion_area = json.loads(puntuacion_area)
                puntuaciones.append(puntuacion_area[0]['puntuacion'])
            else:
                puntuaciones.append(0)
        self.dump([model.Calificacionarea(idinvestigador=idinv,
                  idarea=area['id'], puntuacion=np.mean(puntuaciones))])

    def get_areatematica_id(self, id):
        models_areatematica = self.dbprocess.read_areatematica_id(id)
        if len(models_areatematica) == 0:
            return None
        else:
            import sqlalchemy
            if isinstance(models_areatematica[0], sqlalchemy.engine.row.Row):

                areatematica_dict = models_areatematica[0][0].__dict__
                areatematica_dict['hijos'] = []
                for x in models_areatematica:
                    areatematica_dict['hijos'].append(x[2])
                del areatematica_dict['_sa_instance_state']
            else:
                areatematica_dict = models_areatematica[0].__dict__
                areatematica_dict['hijos'] = None
                del areatematica_dict['_sa_instance_state']
        id_padre = self.dbprocess.read_areatematica_id_padre(id)
        if len(id_padre) > 0:
            id_padre = id_padre[0][0]
        else:
            id_padre = None
        areatematica_dict['padre'] = id_padre
        return json.dumps(areatematica_dict)

    def get_investigador(self, filters=None):
        models_investigador = self.dbprocess.read_investigador(filters)
        investigador_dict = [x.__dict__ for x in models_investigador]
        if not investigador_dict or len(investigador_dict) == 0:
            return []
        for x in investigador_dict:
            del x['_sa_instance_state']
        return json.dumps(investigador_dict)

    def get_calificacionArea(self, filters=None):
        models_calificacion = self.dbprocess.read_calificacionArea(filters)
        calificacion_dict = [x.__dict__ for x in models_calificacion]
        if len(calificacion_dict) == 0:
            return []
        for x in calificacion_dict:
            del x['_sa_instance_state']
        return json.dumps(calificacion_dict)

    def get_calificacionConvocatoria(self, filters=None):
        models_calificacion = self.dbprocess.read_calificacionConvocatoria(
            filters)
        calificacion_dict = [x.__dict__ for x in models_calificacion]
        if len(calificacion_dict) == 0:
            return []
        for x in calificacion_dict:
            del x['_sa_instance_state']
        return json.dumps(calificacion_dict)

    def get_notificacionInvestigador(self, filters=None):
        models_notificacionInv = self.dbprocess.read_notificacionInvestigador(
            filters)
        notificacionInv_dict = [x.__dict__ for x in models_notificacionInv]
        if len(notificacionInv_dict) == 0:
            return []
        for notificacionInv in notificacionInv_dict:
            del notificacionInv['_sa_instance_state']
            notificacionInv['fechacreacion'] = datetime.timestamp(
                notificacionInv['fechacreacion'])
        return json.dumps(notificacionInv_dict)

    def get_notificacion_investigador_last(self):
        model_notificacionInv = self.dbprocess.read_last_notificacionInvestigador()
        if model_notificacionInv:
            notificacionInv_dict = model_notificacionInv.__dict__
            del notificacionInv_dict['_sa_instance_state']
            return json.dumps(notificacionInv_dict)
        return None

    def feedback_convocatoria(self, idconvocatoria, idinvestigador, puntuacion):
        sgi = SGI.SGI()
        convocatoria = sgi.get_call(str(idconvocatoria))
        areas_tematicas = sgi.get_subject_area_announcement(
            str(idconvocatoria))
        if not convocatoria or not areas_tematicas:
            return False

        filter = {}
        filter['idinvestigador'] = idinvestigador
        filter['idconvocatoriasgi'] = idconvocatoria
        notificacion = self.get_notificacionInvestigador(filter)
        if not notificacion:
            print("No se ha encontrado notificacion, por tanto, puede que alguien este poniendo a prueba la seguridad.")
            return False
        else:
            # ya ha sido puntuada por el investigador
            if (json.loads(notificacion)[0])['feedback']:
                print("Feedback. Ya ha sido notificada (intento de duplicidad).")
                return False

        convocatoria = json.loads(convocatoria)
        areas_tematicas = json.loads(areas_tematicas)
        if puntuacion < 0:
            puntuacion_convocatoria = 0
        else:
            puntuacion_convocatoria = 1
        # Informamos al campo calificacionconvocatoria
        calificacion_convocatoria = model.Calificacionconvocatoria(
            idconvocatoriasgi=idconvocatoria, titulo=convocatoria['titulo'], idinvestigador=idinvestigador, puntuacion=puntuacion_convocatoria)
        # Actualizamos la puntuación de la convocatoria
        for area in areas_tematicas:
            at = area['areaTematica']
            at_padre = at['padre']
            
            while at_padre:
                fuente = at_padre['nombre']
                at_padre = at_padre['padre']
            filter = {}
            if at_padre: #No tiene padre, eso quiere decir que es la propia fuente este area, este caso es muy extraño, pero puede darse.
                filter['fuente'] = fuente
            else:
                filter['fuente'] = at['nombre']
            filter['nombre'] = at['nombre']
            filter['descripcion'] = at['descripcion']
            area_id = self.get_areatematica(filter)
            if area_id:
                area_id = (json.loads(area_id)[0])['id']
                print(area_id)
                self.__fedback_calificar(area_id, idinvestigador, puntuacion)

        new_parameters = {}
        new_parameters['feedback'] = True
        notificacion = json.loads(notificacion)[0]
        self.update_notificacionInvestigador(
            notificacion['id'], new_parameters)
        self.dump([calificacion_convocatoria])
        return True

    def __fedback_calificar(self, idareatematica, idinvestigador, puntuacion):
        area_tematica_interna = json.loads(
            self.get_areatematica_id(idareatematica))
        if area_tematica_interna['hijos']:
            for idhijo in area_tematica_interna['hijos']:
                self.__fedback_calificar(idhijo, idinvestigador, puntuacion)
        else:

            filter = {}
            filter['idinvestigador'] = idinvestigador
            filter['idarea'] = idareatematica
            puntuacion_area = self.get_calificacionArea(filter)
            if puntuacion_area:
                puntuacion_area = (json.loads(puntuacion_area)[0])[
                    'puntuacion']

            else:
                puntuacion_area = 0
            puntuacion_area = puntuacion_area + puntuacion
            if puntuacion_area > 5:
                puntuacion_area = 5
            elif puntuacion_area < 1:
                puntuacion_area = 1

            calificarArea = model.Calificacionarea(
                idinvestigador=idinvestigador, idarea=idareatematica, puntuacion=puntuacion_area)
            self.dump([calificarArea])
            self.calcular_puntuaciones_areas([calificarArea])
            
    def cargar_perfil(self, idinv):
        inv = self.get_investigador({'id':int(idinv)})
        if inv:
            inv = json.loads(inv)[0]
            investigador = Investigador(inv['id'], inv['nombre'], inv['email'], inv['perfil'])
            RSController.cargar_perfil(investigador)
            return True
        return False
    
    def get_config_list(self):
        modules_name = glob.glob(DIRECTORY_PROCESS_CONFIG)
        list_configuradores = []
        for folder_parent in modules_name:
            folder_parent_split = folder_parent.split("/")[-1] #Cogemos la carpeta padre del configurador
            folder_parent = folder_parent+"/"+SUBPATH_PROCESS_CONFIG
            process_module_name = glob.glob(folder_parent)
            for folder in process_module_name:
                dict_process = {}
                dict_process['proceso'] = folder_parent_split
                dict_process['path'] = folder
                dict_process['configurador'] = (folder.split("/")[-1]).split(".")[0]
                list_configuradores.append(dict_process)
        return json.dumps(list_configuradores)
    
    def get_config(self, path):
        try:
            with open(path, "r") as json_file:
                data = json.load(json_file)
                print(data)
                return json.dumps(data)
        except:
            print("No existe el configurador solicitado")
            return None

    def patch_config(self, path, data):
        if not self.get_config(path): #Comprobamos primero si existe el fichero
            return False   
        try:
            with open(path, "w") as json_file:
                json_file.write(data)
                return True
        except:
            return False

    def restore_config(self, path):
        file = path.split('/')[-1]
        path_static_file = path.split('/')[0:len(path.split('/'))-1]
        path_static_file = "/".join(path_static_file)
        path_static_file = path_static_file+"/"+SUBPATH_PROCESS_DEFAULT_CONFIG
        data = self.get_config(path_static_file+"/"+file)
        if not data:
            return False
        try:
            with open(path, "w") as json_file:
                json_file.write(data)
                return True
        except:
            return False
        

    def dump(self, object):
        self.dbprocess.dump(object)

    def update_convocatoria(self, id, new_parameters):
        return self.dbprocess.update_convocatoria(id, new_parameters)

    def update_basereguladora(self, id, new_parameters):
        return self.dbprocess.update_basereguladora(id, new_parameters)

    def update_solicitud(self, id, new_parameters):
        return self.dbprocess.update_solicitud(id, new_parameters)

    def update_areatematica(self, id, new_parameters):
        return self.dbprocess.update_areatematica(id, new_parameters)

    def update_investigador(self, id, new_parameters):
        return self.dbprocess.update_investigador(id, new_parameters)

    def update_calificacionArea(self, id, new_parameters):
        return self.dbprocess.update_calificacionarea(id, new_parameters)

    def update_calificacionConvocatoria(self, id, new_parameters):
        return self.dbprocess.update_calificacionConvocatoria(id, new_parameters)

    def update_notificacionInvestigador(self, id, new_parameters):
        return self.dbprocess.update_notificacionInvestigador(id, new_parameters)

    def update_contrato(self, id, new_parameters):
        return self.dbprocess.update_contrato(id, new_parameters)

    def update_ejecucion_notificacion(self, id, new_parameters):
        return self.dbprocess.update_ejecucion_notificacion(id, new_parameters)
    
    def delete_perfil(self, idinv):
        self.update_investigador(int(idinv), {"perfil": False})
        return self.dbprocess.delete_profile(idinv)

