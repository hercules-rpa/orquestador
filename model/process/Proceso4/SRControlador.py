from datetime import datetime, timedelta
from aiohttp import request
import json
import model.process.Proceso4.model.ClassProcess4 as p4
import requests
import model.EDMA as EDMA
import pandas as pd
import model.SGI as SGI
import numpy as np
import time

URL_AREA_TEMATICA = "/api/orchestrator/register/areatematica"
URL_NOTIFICACION_INVESTIGADOR  = "/api/orchestrator/register/notificacioninvestigador"
URL_NOTIFICACION_LAST  = "/api/orchestrator/register/notificacioninvestigador/last"
URL_INVESTIGADOR  = "/api/orchestrator/register/investigador"
URL_CALIFICACION_AREA = "/api/orchestrator/register/calificacion/area"
URL_GENERATE_TOKEN = "/api/orchestrator/register/token"


URL_API = "http://10.208.99.12:5000"




def get_all_calificacion():
    calificaciones_df = pd.DataFrame({"invId":[],"areaId":[],"rating":[]})
    r = requests.get(URL_API+URL_CALIFICACION_AREA)
    if r.status_code == 200:
        calificaciones = json.loads(r.text)
        for calificacion in calificaciones:
            row = [calificacion['idinvestigador'], calificacion['idarea'], calificacion['puntuacion']]
            calificaciones_df.loc[len(calificaciones_df)] = row
    return calificaciones_df

def get_calificacion(idinvestigador: int, convocatoria: p4.Convocatoria):
        calificaciones = pd.DataFrame({"invId":[],"areaId":[],"rating":[]})
        areasTematicas = convocatoria.areaTematica
        if not areasTematicas:
            return calificaciones
        for areaTematica in areasTematicas:
            areaTematica = areaTematica.areaHijo #Nos quitamos la fuente
            #Columnas. idInv, area, calificacion
            while areaTematica:
                try:
                    r = requests.get(URL_API+URL_CALIFICACION_AREA+"?idinvestigador="+str(idinvestigador)+"&idarea="+str(areaTematica.id))
                except Exception as e:
                    print("No se pudo conectar con ",URL_API)
                    print(e)
                    return calificaciones

                row = [idinvestigador, areaTematica.id, None]
                if r.status_code == 200:
                    calificacion = json.loads(r.text)[0]
                    row[2] = calificacion['puntuacion']
                areaTematica = areaTematica.areaHijo
        return calificaciones

def post_areastematicas(): #Insertamos todas las areas en nuestra bbdd
    '''Obtenemos el area tematica de las convocatorias'''
    sgi = SGI.SGI()
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
            at_interno = get_areatematica_interno(area_tematica.nombre, fuente)
            if not at_interno:
                area_tematica.id = insert_areatematica_interno(area_tematica, fuente)
            else:
                area_tematica.id = at_interno.id
            while hijo:
                at_interno = get_areatematica_interno(hijo.nombre, fuente)
                if not at_interno:
                    hijo.id = insert_areatematica_interno(hijo, fuente)
                else:
                    hijo.id = at_interno.id
                hijo = hijo.areaHijo

def generate_token(idInvestigador):
    headers = { 'Content-Type': 'application/json' }
    body_json = {'iduser':idInvestigador, 'password':'qhj!f<F4s@7F{3Y'}
    r = requests.post(URL_API+URL_GENERATE_TOKEN, headers=headers, data = json.dumps(body_json))
    if r.status_code == 200:
        return json.loads(r.text)['access_token']
    return None
            

def get_areamatica_sgi(convocatoria):
    '''Obtenemos el area tematica de las convocatorias'''
    sgi = SGI.SGI()
    r = sgi.get_convocatoria_area_tematica(convocatoria.id)
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
                at_interno = get_areatematica_interno(area_tematica.nombre, fuente)
                area_tematica.id = at_interno.id
                while hijo:
                    at_interno = get_areatematica_interno(hijo.nombre, fuente)
                    hijo.id = at_interno.id
                    hijo = hijo.areaHijo
                areatematica.append(area_tematica)
            else:
                print("La convocatoria no tiene area tematica.")
                
        convocatoria.areaTematica = areatematica
        

def get_ultima_sugerencia():
    '''Obtenemos la fecha de la última convocatoria que notificamos. Devuelve una lista de correos'''
    r = requests.get(URL_API+URL_NOTIFICACION_LAST)
    if r.status_code == 200:
        last_notificacion = json.loads(r.text)
        return datetime.fromtimestamp(last_notificacion['fechaCreacion'])
    return None

def cargar_perfil(investigador: p4.Investigador):
    try:
        if investigador.is_config_perfil:
            return True #El perfil ya ha sido configurado no hace falta cargarlo de nuevo
        ed = EDMA.EDMA()
        sgi = SGI.SGI()
        idref = ed.get_personaref(investigador.email)
        if not idref:
            return False
        sgi = SGI.SGI()
        #Procedemos a hacer un perfil base en funcion a las areas tematicas de las convocatorias
        #Cogemos todas las convocatorias para extraer las areas tematicas
        #Empezamos a contar desde 2.5, cada area adicional se sumará 0.15
        r = sgi.get_solicitudes("solicitanteRef=="+str(idref))
        areas = []
        body = {}
        index = {}
        if r and len(r) > 0:
            solicitudes = json.loads(r)
            for solicitud in solicitudes:
                convocatoria = solicitud['convocatoriaId']
                if convocatoria:
                    conv = p4.Convocatoria(id=convocatoria, titulo=None)
                    get_areamatica_sgi(conv)
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
            token = generate_token(investigador.id)
            x = requests.post(URL_API+URL_CALIFICACION_AREA, headers={ 'Content-Type': 'application/json', 'Authorization': 'Bearer '+str(token)}, data = json.dumps(areas))
        return True
    except Exception as e:
        print("Error al cargar el perfil "+str(e))
        return True
    


def get_investigador_interno(id=None) -> pd.DataFrame:
    '''Obtenemos los investigadores almacenados en la bbdd'''
    if id:
        r = requests.get(URL_API+URL_INVESTIGADOR+"/"+str(id))
        if r.status_code == 200:
            investigador_json = json.loads(r.text)[0]
            inv = p4.Investigador(id=id,nombre=investigador_json['nombre'],email=investigador_json['email'], perfil=investigador_json['perfil'])
            return inv
        return None
    else:
        r = requests.get(URL_API+URL_INVESTIGADOR)
        if r.status_code == 200:
            investigadores_json = json.loads(r.text)
            df_inv = pd.json_normalize(investigadores_json)
            return df_inv
        return []

def get_investigadores_ed():
    '''Obtenemos los investigadores almacenados en edma'''
    ed = EDMA.EDMA()
    df_investigadores = ed.get_investigadores()
    if len(df_investigadores) > 0:
        print(df_investigadores)
        df_investigadores = df_investigadores.loc[0:len(df_investigadores), ['nombrePersona.value','email.value']] 
        df_investigadores = df_investigadores.rename(columns={'nombrePersona.value': 'nombre', 'email.value': 'email'})
        return df_investigadores
    return pd.DataFrame()
    

def get_notificacion_interna(emailinvestigador, convocatoria) -> p4.Investigador:
    '''Comprobamos si ya está notificada la convocatoria a este investigador'''
    r = requests.get(URL_API+URL_INVESTIGADOR+"?email="+emailinvestigador)
    if r.status_code == 200:
        investigador = json.loads(r.text)[0]
        investigador = p4.Investigador(id=investigador['id'],nombre=investigador['nombre'], email=investigador['email'], perfil=investigador['perfil'])
        r = requests.get(URL_API+URL_NOTIFICACION_INVESTIGADOR+"?idinvestigador="+str(investigador.id)+"&idconvocatoriasgi="+str(convocatoria.id))
        if r.status_code == 200:
            return None #ha sido notificado por tanto no debemos tenerlo en cuenta
        return investigador #No ha sido notificado, por tanto, debemos tenerlo en cuenta
    print("Ocurrio algo raro, no sabemos como no se encontro al investigador en la bbdd interna ",emailinvestigador)
    return None

def is_convocatoria_registrada(convocatoria):
    '''Función que comprueba si una convocatoria ya esta registrada'''
    r = requests.get(URL_API+URL_NOTIFICACION_INVESTIGADOR+"?idconvocatoriasgi="+str(convocatoria.id))
    if r.status_code == 200:
        if len(json.loads(r.text)) > 0:
            return True
    return False

def get_areatematica_interno_id(id: int) -> p4.AreaTematica:
    r = requests.get(URL_API+URL_AREA_TEMATICA+"/"+str(id))
    if r.status_code == 200:
        areatematica_dict = json.loads(r.text)
        areatematica_dict = areatematica_dict
        areatematica = p4.AreaTematica(id = areatematica_dict['id'], nombre= areatematica_dict['nombre'], descripcion=areatematica_dict['descripcion'])
        return areatematica
    return None

def get_areatematica_interno(nombre: str, fuente: str) -> p4.AreaTematica:
    r = requests.get(URL_API+URL_AREA_TEMATICA+"?nombre="+nombre+"&fuente="+fuente)
    if r.status_code == 200:
        areatematica_dict = json.loads(r.text)
        areatematica_dict = areatematica_dict[0]
        if areatematica_dict:
            areatematica = p4.AreaTematica(id = areatematica_dict['id'], nombre= areatematica_dict['nombre'], descripcion=areatematica_dict['descripcion'])
            if areatematica_dict['padre']:
                areatematica_p = get_areatematica_interno_id(areatematica_dict['padre'])
                areatematica.areaPadre = areatematica_p
            return areatematica
    return None

def insert_investigadores(df: pd.DataFrame):
    investigadores = []
    for index, row in df.iterrows():
        investigadores.append({'nombre':row['nombre'], 'email':row['email'], 'perfil':False})
    x = requests.post(URL_API+URL_INVESTIGADOR, data = json.dumps(investigadores))
    print("inserccion bbdd ",x.status_code)

def insert_areatematica_interno(areatematica, fuente):
    '''Insertamos el area tematica'''
    json_insert = [{
        "id":None,
        "nombre":areatematica.nombre,
        "fuente": fuente,
        "descripcion": areatematica.descripcion,
        "parents":{
            "id": areatematica.areaPadre.id if areatematica.areaPadre else None
        }
    }]
    x = requests.post(URL_API+URL_AREA_TEMATICA, data = json.dumps(json_insert))
    if x.status_code == 201:
        print(x.text)
        return json.loads(x.text)['id']
    return None

def post_notificacion(investigador: p4.Investigador, convocatoria: p4.Convocatoria):
    data_json = {}
    data_json['fechacreacion'] = datetime.now().isoformat()
    data_json['idconvocatoriasgi'] = convocatoria.id
    data_json['idinvestigador'] = investigador.id
    data_json['feedback'] = False
    x = requests.post(URL_API+URL_NOTIFICACION_INVESTIGADOR, headers={ 'Content-Type': 'application/json' }, data = json.dumps([data_json]))
    print(x.text)
    if x.status_code == 201:
        return True
    return False


