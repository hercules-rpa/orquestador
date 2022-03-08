import requests
import json
import time
from datetime import datetime

from model.process.Proceso3.Modelo_Ejecucion import Modelo_Ejecucion



LINK_GRANTS = r'https://ec.europa.eu/info/funding-tenders/opportunities/data/referenceData/grantsTenders.json'
LINK_TOPIC_DETAILS = r'https://ec.europa.eu/info/funding-tenders/opportunities/data/topicDetails/{}.json'
LINK_CALL_FOR_GRANT = r'https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/{}'


class GrantsEuropeExtractor():
    """
    Extractor de la información sobre grants y tenders de la página de ec.europa.eu
    """

    def __init__(self):
        self.msg_notify = ""
        self.result = []

    def get_grants_json(self):
        """
        Obtener json con datos de todas grants y tenders
        """

        response = requests.get(LINK_GRANTS, timeout=10)
        # print response
        print(response)
        if response.status_code == 200:
        
            response_json = response.json()
            print('Numero de convocatorias total', len(response_json['fundingData']['GrantTenderObj']))
            return response_json['fundingData']['GrantTenderObj']
        else:
            return None

    def get_open_grant(self, dict_conv):
        """
        Comprobar si la convocatoria es de tipo 1 - grant  y está abierta
        Devuelve identificador de la convocatoría si cumple los requisitos; en caso contrario devuelce None
        """
        
        # status- Open o Closed
        status = dict_conv['status']['abbreviation']
        # tipo 1 o 0: grant o tender
        typ = dict_conv['type']
        if typ == 1 and status in ['Open', 'Forthcoming']:
            # extrar identificador de la convocatoria: lo utiluizamos para obtener url de call y json con detalles
            identifier = dict_conv['identifier'].lower()
            #print('Identificador: ', identifier)
            return identifier

        # si la convocatoria esta cerrada o es de tipo tender, devolver None        
        else:
            return None

    def get_call_url(self, identifier):
        """
        Obtener enlace de 'Call for grant'
        """
        call_link = LINK_CALL_FOR_GRANT.format(identifier)

        # comprobar si se puede acceder a la pagina utilizando el url
        for i in range(5):
            try:
                resp = requests.get(call_link, timeout=10)
                break
            except Exception as e:
                print('Intento %s error' %i)
                print(e)


        
        if resp.status_code == 200:
            return call_link
        else:
            return None

    def get_details_json(self, identifier):
        """
        Obtener json con detalles de una convocatoria (de momento no se utiliza)
        """

        details_link = LINK_TOPIC_DETAILS.format(identifier)
        for i in range(5):
            try:
                resp = requests.get(details_link, timeout=10)
                break
            except Exception as e:
                print('Intento %s error' %i)
                print(e)


        if resp.status_code == 200:
            #json con detalles sobre la convocatoria
            return resp.json()

        else:
            return None

    def search_europa(self):
        
        count = 0
        dict_call_urls = {}


        start = datetime.now()
        print('Start time: ', start.strftime("%H:%M:%S"))

        extractor = GrantsEuropeExtractor()

        # lista de dicts donde cada dict es grant/tender
        list_grants_json = extractor.get_grants_json()
        if list_grants_json:
            # recorrer el dict
            for idx, dict_conv in enumerate(list_grants_json, 1):
                # print('Idx convoccatoria %s' %idx)
                try:
                    # obtener identificador de la convocatoria
                    identifier = extractor.get_open_grant(dict_conv)
                    if identifier:
                        call_url = extractor.get_call_url(identifier)

                        # PENDIENTE: a veces da error al extraer json, hay que introducir n intentos de hacerlo    
                        # lo comento porque de momento no lo vamos a neceesitar            
                        # details_json = extractor.get_details_json(identifier)

                        # añadir al dict titulo de la convocatoria y url
                        dict_call_urls[dict_conv['title']] = call_url

                        # incrementar el contador de las convocatorias de grants abiertos
                        count += 1
                except Exception as e:
                    print(e)

            print('Número de convocatorias abiertas: %s' %count)
            end = datetime.now()
            print('Tiempo de ejecución: ', (end - start))


            array = []
            # dict_call_urls es un diccionario ´título convocatoria´: ´url call para convocatoria´
            for idx, conv in enumerate(dict_call_urls.items(), 1):
                title, url = conv
                insert = {}
                insert['titulo'] = title
                insert['_from'] = 'EUROPA'
                insert['url'] = url
                insert['entidad_gestora'] = 'EUROPA'
                insert['entidad_convocante'] = 'EUROPA'
                array.append(insert)
                #print(f'{idx}. {title}: url: {url}')

            headers = {
            'Content-Type': 'application/json'
            }
            payload = json.dumps(array)
            bbdd_url = "http://10.208.99.12:5000/api/orchestrator/process/convocatoria"
            response = requests.post(bbdd_url, headers=headers, data=payload)
            print(response.status_code)
            print(response.text)
        
        return dict_call_urls


    def search_europe(self):
        response = requests.get(LINK_GRANTS, timeout=10)
        if response.ok:
            JSON = json.loads(response.content)
            for item in JSON['fundingData']['GrantTenderObj']:
                dict_europe = {}
                if item['type'] == 1 and item['status']['abbreviation'] in ['Open', 'Forthcoming'] and float(item['publicationDateLong'])/1000 >= time.time():
                    dict_europe['titulo'] = item['title']
                    dict_europe['url'] = LINK_CALL_FOR_GRANT.format(item['identifier'].lower())
                    dict_europe['fecha_publicacion'] = time.localtime(float(item['publicationDateLong'])/1000)
                    dict_europe['fecha_creacion'] = time.localtime(float(item['deadlineDatesLong'].pop())/1000)
                    dict_europe['modelo_ejecucion'] = Modelo_Ejecucion.SUBVENCION.value
                    dict_europe['_from'] = "EUROPA2020"
                    dict_europe['notificada'] = False
                    self.result.append(dict_europe)
            self.insert_database(self.result)
            return self.result
        return None

    def search_europe_date(self, fecha_desde, fecha_hasta):
        response = requests.get(LINK_GRANTS)
        if response.ok:
            JSON = json.loads(response.content)
            for item in JSON['fundingData']['GrantTenderObj']:
                dict_europe = {}
                if item['type'] == 1 and item['status']['abbreviation'] in ['Open', 'Forthcoming'] and float(item['publicationDateLong'])/1000 >= time.mktime(time.strptime(fecha_desde, '%d/%m/%Y')):
                    dict_europe['titulo'] = item['title']
                    dict_europe['url'] = LINK_CALL_FOR_GRANT.format(item['identifier'].lower())
                    dict_europe['fecha_publicacion'] = float(item['publicationDateLong'])/1000
                    dict_europe['fecha_creacion'] = float(item['deadlineDatesLong'].pop())/1000
                    dict_europe['modelo_ejecucion'] = Modelo_Ejecucion.SUBVENCION.value
                    dict_europe['_from'] = "EUROPA2020"
                    dict_europe['notificada'] = False
                    self.result.append(dict_europe)
            self.insert_database(self.result)
            return self.result
        return None

    def insert_database(self, array):
        headers = {
        'Content-Type': 'application/json'
        }
        payload = json.dumps(array)
        bbdd_url = "http://10.208.99.12:5000/api/orchestrator/register/convocatorias"
        response = requests.post(bbdd_url, headers=headers, data=payload)
        self.msg_notify = str(response.status_code) + " --- " + response.text

    def cambio_notificadas(self):
        headers = {
        'Content-Type': 'application/json'
        }
        payload = "{ \"notificada\": true }"
        for i in self.result:
            bbdd_url = "http://10.208.99.12:5000/api/orchestrator/register/convocatorias?url=" + i['url']
            response = requests.get(bbdd_url)
            JSON = json.loads(response.content)
            bbdd_url = "http://10.208.99.12:5000/api/orchestrator/register/convocatoria/" + str(JSON[0]['id'])
            patch = requests.patch(bbdd_url,headers=headers,data=payload)