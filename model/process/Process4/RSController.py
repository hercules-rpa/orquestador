from datetime import datetime
from model.RPA import RPA
from rpa_robot.ControllerSettings import ControllerSettings
from rpa_robot.ControllerRobot import ControllerRobot
import json
import model.process.Process4.model.ClassProcess4 as p4
import requests
import pandas as pd

URL_AREA_TEMATICA = "/api/orchestrator/register/areatematica"
URL_NOTIFICACION_INVESTIGADOR  = "/api/orchestrator/register/notificacioninvestigador"
URL_NOTIFICACION_LAST  = "/api/orchestrator/register/notificacioninvestigador/last"
URL_INVESTIGADOR  = "/api/orchestrator/register/investigador"
URL_CALIFICACION_AREA = "/api/orchestrator/register/calificacion/area"
URL_GENERATE_TOKEN = "/api/orchestrator/register/token"

cs = ControllerSettings()
controllerRobot = ControllerRobot()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class RSController(metaclass=Singleton):
    def __init__(self, ip_api = None, port_api = None):
        self.ip = ip_api
        self.port = str(port_api)
        if self.ip and self.port: #Si es Nulo es el orquestador haciendo uso de funciones de aqui para cargar el perfil base solicitado por API
            self.url_api = self.ip+":"+str(self.port)
            self.rpa_controller = None
            if controllerRobot.robot:
                self.rpa_controller = RPA(controllerRobot.robot.token)
        
    def get_all_calificacion(self):
        calificaciones_df = pd.DataFrame({"invId":[],"areaId":[],"rating":[]})
        r = self.rpa_controller.get(self.url_api+URL_CALIFICACION_AREA)
        if r.status_code == 200:
            calificaciones = json.loads(r.text)
            for calificacion in calificaciones:
                row = [calificacion['idinvestigador'], calificacion['idarea'], calificacion['puntuacion']]
                calificaciones_df.loc[len(calificaciones_df)] = row
        return calificaciones_df

    def get_calificacion(self, idinvestigador: int, convocatoria: p4.Convocatoria):
        """
        Método para obtener las calificaciones de los investigadores que han dado a las áreas temáticas
        :param idinvestigador id interno del investigador
        :param convocatoria objeto de la clase convocatoria
        :return dataframe con el id del investigador, área y la puntuación
        """
        calificaciones = pd.DataFrame({"invId":[],"areaId":[],"rating":[]})
        areasTematicas = convocatoria.areaTematica
        if not areasTematicas:
            return calificaciones
        for areaTematica in areasTematicas:
            areaTematica = areaTematica.areaHijo #Nos quitamos la fuente
            #Columnas. idInv, area, calificacion
            while areaTematica:
                try:
                    r = self.rpa_controller.get(self.url_api+URL_CALIFICACION_AREA+"?idinvestigador="+str(idinvestigador)+"&idarea="+str(areaTematica.id))
                except Exception as e:
                    print("No se pudo conectar con ",self.url_api)
                    print(e)
                    return calificaciones

                row = [idinvestigador, areaTematica.id, None]
                if r.status_code == 200:
                    calificacion = json.loads(r.text)[0]
                    row[2] = calificacion['puntuacion']
                areaTematica = areaTematica.areaHijo
        return calificaciones

    def post_areastematicas(self):
        """
        Método para obtener el área temática de las convocatorias e insertarla en BBDD sino tuvieramos esas áreas
        """
        sgi = cs.get_sgi(self.ip, self.port)
        r = sgi.get_areastematicas()
        if r:
            areastematicas_json = json.loads(r)
            for areatematica_json in areastematicas_json:
                at_dict = areatematica_json
                area_tematica = p4.AreaTematica(nombre=at_dict['nombre'], descripcion=at_dict['descripcion'])
                padre = at_dict['padre']
                while padre:
                    at_dict = padre
                    area_tematica_p = p4.AreaTematica(nombre=at_dict['nombre'], descripcion=at_dict['descripcion'])
                    area_tematica.areaPadre = area_tematica_p
                    area_tematica_p.areaHijo = area_tematica
                    area_tematica = area_tematica_p
                    padre = at_dict['padre']
                
                hijo = area_tematica.areaHijo
                fuente = area_tematica.nombre
                at_interno = self.get_areatematica_interno(area_tematica.nombre, fuente)
                if not at_interno:
                    area_tematica.id = self.insert_areatematica_interno(area_tematica, fuente)
                else:
                    area_tematica.id = at_interno.id
                while hijo:
                    at_interno = self.get_areatematica_interno(hijo.nombre, fuente)
                    if not at_interno:
                        hijo.id = self.insert_areatematica_interno(hijo, fuente)
                    else:
                        hijo.id = at_interno.id
                    hijo = hijo.areaHijo

    def generate_token(self, idInvestigador, idrobot, token):
        """
        Método para generar un token para el investigador a partir del id del robot y el token amqp del robot
        :param idInvestigador id interno del investigador para generar el token
        :param idrobot id del robot que ejecuta el proceso
        :param token token del robot amqp
        """
        headers = { 'Content-Type': 'application/json' }
        body_json = {'iduser':idInvestigador, 'idrobot': idrobot, 'token': token}
        r = self.rpa_controller.post(service=self.url_api+URL_GENERATE_TOKEN, data_body = json.dumps(body_json))
        if r.status_code == 200:
            return json.loads(r.text)['access_token']
        return None
                

    def get_areamatica_sgi(self, convocatoria: p4.Convocatoria):
        """
        Método para obtener el area tematica de las convocatorias y añadirla al objeto
        :param convocatoria objeto de la clase convocatoria
        """
        sgi = cs.get_sgi(self.ip, self.port)
        r = sgi.get_subject_area_announcement(convocatoria.id)
        if r:
            areatematica = []
            areastematicas_json = json.loads(r)
            for areatematica_json in areastematicas_json:
                if areatematica_json['areaTematica']:
                    at_dict = areatematica_json['areaTematica']
                    area_tematica = p4.AreaTematica(nombre=at_dict['nombre'], descripcion=at_dict['descripcion'])
                    padre = at_dict['padre']
                    while padre:
                        at_dict = padre
                        area_tematica_p = p4.AreaTematica(nombre=at_dict['nombre'], descripcion=at_dict['descripcion'])
                        area_tematica.areaPadre = area_tematica_p
                        area_tematica_p.areaHijo = area_tematica
                        area_tematica = area_tematica_p
                        padre = at_dict['padre']
                    
                    hijo = area_tematica.areaHijo
                    fuente = area_tematica.nombre
                    at_interno = self.get_areatematica_interno(area_tematica.nombre, fuente)
                    area_tematica.id = at_interno.id
                    while hijo:
                        at_interno = self.get_areatematica_interno(hijo.nombre, fuente)
                        hijo.id = at_interno.id
                        hijo = hijo.areaHijo
                    areatematica.append(area_tematica)
                else:
                    print("La convocatoria no tiene area tematica.")
                    
            convocatoria.areaTematica = areatematica

    def cargar_perfil(self, investigador: p4.Investigador):
        """ 
        Método para hacer un perfil base en funcion a las areas tematicas de las convocatorias que el investigador ha solicitado
        :param investigador Objeto de la clase investigador
        """
        try:
            if investigador.is_config_perfil:
                return True #El perfil ya ha sido configurado no hace falta cargarlo de nuevo
            ed = cs.get_edma(self.ip, self.port)
            sgi = cs.get_sgi(self.ip, self.port)
            idref = ed.get_personaref(investigador.email)
            if not idref:
                return False
            r = sgi.get_forms("solicitanteRef=="+str(idref))
            areas = []
            body = {}
            index = {}
            if r and len(r) > 0:
                solicitudes = json.loads(r)
                for solicitud in solicitudes:
                    convocatoria = solicitud['convocatoriaId']
                    if convocatoria:
                        conv = p4.Convocatoria(id=convocatoria, titulo=None)
                        self.get_areamatica_sgi(conv)
                        if conv.areaTematica:
                            areasTematicas = conv.areaTematica
                            for areaTematica in areasTematicas:
                                areaTematica = areaTematica.areaHijo  # Nos quitamos la fuente
                                while areaTematica:
                                    if not str(areaTematica.id) in index:
                                        body['idarea'] = areaTematica.id
                                        body['puntuacion'] = 2.5
                                        areas.append(body)
                                        index[str(areaTematica.id)] = len(areas) - 1
                                    else:
                                        dict_body = areas[index[str(areaTematica.id)]]
                                        dict_body['puntuacion'] += 0.15
                                    areaTematica = areaTematica.areaHijo
                token = self.generate_token(investigador.id, controllerRobot.robot.id, controllerRobot.robot.token)
                x = requests.post(self.url_api+URL_CALIFICACION_AREA, headers={ 'Content-Type': 'application/json', 'Authorization': 'Bearer '+str(token)}, data = json.dumps(areas))
            return True
        except Exception as e:
            print("Error al cargar el perfil "+str(e))
            return False
        


    def get_investigador_interno(self, id=None) -> pd.DataFrame:
        """ 
        Método para obtener los investigadores almacenados en la bbdd interna
        :param id id del investigador, None para obtenerlos todos.
        :return: dataframe de investigador/es
        """
        if id:
            r = self.rpa_controller.get(self.url_api+URL_INVESTIGADOR+"/"+str(id))
            if r.status_code == 200:
                investigador_json = json.loads(r.text)[0]
                inv = p4.Investigador(id=id,nombre=investigador_json['nombre'],email=investigador_json['email'], perfil=investigador_json['perfil'])
                return inv
            return None
        else:
            r = self.rpa_controller.get(self.url_api+URL_INVESTIGADOR)
            if r.status_code == 200:
                investigadores_json = json.loads(r.text)
                df_inv = pd.json_normalize(investigadores_json)
                return df_inv
            return []

    def get_investigadores_ed(self):
        """ 
        Método para obtener los investigadores almacenados en ed
        :return dataframe de investigadores
        """
        ed = cs.get_edma(self.ip, self.port)
        df_investigadores = ed.get_researchers()
        if len(df_investigadores) > 0:
            df_investigadores = df_investigadores.loc[0:len(df_investigadores), ['nombrePersona.value','email.value']] 
            df_investigadores = df_investigadores.rename(columns={'nombrePersona.value': 'nombre', 'email.value': 'email'})
            return df_investigadores
        return pd.DataFrame()
        

    def get_notificacion_interna(self, emailinvestigador:str, convocatoria: p4.Convocatoria) -> p4.Investigador:
        """
        Método para comprobar si la convocatira ya ha sido notificada al investigador
        :param emailinvestigador email del investigador
        :param convocatatoria objeto de la clase convocatoria
        return None en caso de que haya sido notificado y objeto investigador en caso de que no haya sido notificado
        """
        r = self.rpa_controller.get(self.url_api+URL_INVESTIGADOR+"?email="+emailinvestigador)
        if r.status_code == 200:
            investigador = json.loads(r.text)[0]
            investigador = p4.Investigador(id=investigador['id'],nombre=investigador['nombre'], email=investigador['email'], perfil=investigador['perfil'])
            r = self.rpa_controller.get(self.url_api+URL_NOTIFICACION_INVESTIGADOR+"?idinvestigador="+str(investigador.id)+"&idconvocatoriasgi="+str(convocatoria.id))
            if r.status_code == 200:
                return None
            return investigador
        print("Ocurrio algo raro, no sabemos como no se encontro al investigador en la bbdd interna ",emailinvestigador)
        return None

    def get_areatematica_interno_id(self, id: int) -> p4.AreaTematica:
        """ 
        Método que devuelve una área temática de la bbdd interna
        :param id id del área
        :return objeto de la clase AreaTematica
        """
        r = self.rpa_controller.get(self.url_api+URL_AREA_TEMATICA+"/"+str(id))
        if r.status_code == 200:
            areatematica_dict = json.loads(r.text)
            areatematica = p4.AreaTematica(id = areatematica_dict['id'], nombre= areatematica_dict['nombre'], descripcion=areatematica_dict['descripcion'])
            return areatematica
        return None

    def get_areatematica_interno(self, nombre: str, fuente: str) -> p4.AreaTematica:
        """ 
        Método que devuelve una área temática de la bbdd interna
        :param nombre nombre del area
        :param fuente origen del área temática (fuente de extracción)
        :return objeto de la clase AreaTematica
        """
        r = self.rpa_controller.get(self.url_api+URL_AREA_TEMATICA+"?nombre="+nombre+"&fuente="+fuente)
        if r.status_code == 200:
            areatematica_dict = json.loads(r.text)
            areatematica_dict = areatematica_dict[0]
            if areatematica_dict:
                areatematica = p4.AreaTematica(id = areatematica_dict['id'], nombre= areatematica_dict['nombre'], descripcion=areatematica_dict['descripcion'])
                if areatematica_dict['padre']:
                    areatematica_p = self.get_areatematica_interno_id(areatematica_dict['padre'])
                    areatematica.areaPadre = areatematica_p
                return areatematica
        return None

    def insert_investigadores(self, df: pd.DataFrame):
        """ 
        Método para insertar investigadores en la bbdd interna
        :param df dataframe de investigadores a insertar
        """
        investigadores = []
        for index, row in df.iterrows():
            investigadores.append({'nombre':row['nombre'], 'email':row['email'], 'perfil':False})
        x = self.rpa_controller.post(service=self.url_api+URL_INVESTIGADOR, data_body = json.dumps(investigadores))


    def insert_areatematica_interno(self, areatematica:p4.AreaTematica, fuente:str):
        """ 
        Método para insertar áreas temáticas en la bbdd interna
        :param areatematica objeto de la clase areatematica
        :param fuente origen del área temática (fuente de extracción)
        :return el id de inserción
        """
        json_insert = [{
            "id":None,
            "nombre":areatematica.nombre,
            "fuente": fuente,
            "descripcion": areatematica.descripcion,
            "parents":{
                "id": areatematica.areaPadre.id if areatematica.areaPadre else None
            }
        }]
        x = self.rpa_controller.post(service=self.url_api+URL_AREA_TEMATICA, data_body = json.dumps(json_insert))
        if x.status_code == 201:
            return json.loads(x.text)['id']
        return None

    def post_notificacion(self, investigador: p4.Investigador, convocatoria: p4.Convocatoria):
        """ 
        Método para que quede constancia de que un investigador ha sido notificado de una convocatoria, insertando en la bbdd interna
        :param investigador objeto de la clase investigador
        :param convocatoria objeto de la clase convocatoria
        :return true éxito, false error
        """
        data_json = {}
        data_json['fechacreacion'] = datetime.now().isoformat()
        data_json['idconvocatoriasgi'] = convocatoria.id
        data_json['idinvestigador'] = investigador.id
        data_json['feedback'] = False
        x = self.rpa_controller.post(service=self.url_api+URL_NOTIFICACION_INVESTIGADOR, data_body = json.dumps([data_json]))
        if x.status_code == 201:
            return True
        return False


