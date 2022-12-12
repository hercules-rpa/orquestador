import requests
import base64
import datetime
import time


class SGI():
   # host_demo = "https://sgi.demo.treelogic.com"
    oauth_grant_type = "password"
    oauth_client_id = b"front"
    oauth_client_secret = ""
    oauth_scopes = "openid profile"
    oauth_token = ""
    oauth_timestamp = 0.0
    oauth_token_expiresintime = 0.0

    def __init__(self, host:str='', user:str='', password:str=''):
        self.host = host
        self.oauth_username = user
        self.oauth_password = password
        if self.host:
            self.oauth_url = self.host + '/auth/realms/sgi/protocol/openid-connect/token'
            self.host_api = self.host + '/api'

        if not (host and user and password):
            print('ERROR en la iniciación de SGI.')

    def auth(self) -> bool:
        """
        Método de autenticación contra el entorno de desarrollo,
        se debe ejecutar antes de cada llamada.
        """
        result:bool = False
        if self.oauth_url and self.oauth_username:
            try:
                tokenDate = datetime.datetime(2010, 1, 1)
                if self.oauth_token_expiresintime == 0:
                    self.oauth_token_expiresintime = 300000
                if (datetime.datetime.now() - tokenDate).total_seconds() >= self.oauth_token_expiresintime:
                    oauth_auth = "Basic " + \
                        str(base64.b64encode(self.oauth_client_id))[
                            2:-1] + ":" + self.oauth_client_secret
                    header = {
                        'Authorization': oauth_auth,
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json'
                    }
                    body = {
                        'mode': 'urlencoded',
                        'grant_type': self.oauth_grant_type,
                        'scope': self.oauth_scopes,
                        'client_id': self.oauth_client_id,
                        'client_secret': self.oauth_client_secret,
                        'username': self.oauth_username,
                        'password': self.oauth_password
                    }
                    response = requests.post(self.oauth_url, headers=header, data=body)
                    self.oauth_token = response.json()['access_token']
                    self.oauth_timestamp = datetime.datetime.now()
                    if response.json()['expires_in']:
                        self.oauth_token_expiresintime = int(
                            response.json()['expires_in']) * 1000
                    result= True
            except Exception as e:
                print("ERROR: fallo en la autenticación de Hércules-SGI. " + str(e))
            
        return result
                

    def get_calls(self, filters=None) -> str:
        """
        Método para obtener las convocatorias. Se puede filtrar añadiendo un string de filtro como por ejemplo:
            titulo=="Resolución de 3 de febrero de 2022 del Centro de Investigaciones Sociológicas 
            por la que se publica la convocatoria de subvenciones para formación e investigación en 
            materias de interés para el organismo, para el año 2022"
        :param filters filtros de búsqueda
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgicsp/convocatorias"
            if filters != None:
                service = service + '?q=' + filters
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            return response.text
        return None

    def get_call(self, id) -> str:
        """
        Método encargado de obtener una convocatoria en base a un identificador
        :param id identificador de la convocatoria
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgicsp/convocatorias/" + str(id)
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            return response.text
        return None

    def get_areastematicas(self):
        """
        Método encargado de obtener todas las áreas temáticas
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgicsp/areatematicas"
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            return response.text
        return None

    def post_announcement(self, body) -> str:
        """
        Método para insertar una convocatoria en el entorno de pruebas.
        :param body datos de la petición POST
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgicsp/convocatorias"
            response = requests.request(
                "POST", self.host_api + service, headers=header, data=body)
            return response.text
        return None

    def post_convener_announcement(self, body) -> str:
        """
        Método para insertar una entidad convocante a una convocatoria en el entorno de pruebas.
        :param body datos de la petición POST
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgicsp/convocatoriaentidadconvocantes"
            response = requests.request(
                "POST", self.host_api + service, headers=header, data=body)
            return response.text
        return None

    def post_financing_entity_announcement(self, body) -> str:
        """
        Método para insertar una entidad financiadora a una convocatoria en el entorno de pruebas.
        :param body datos de la petición POST
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgicsp/convocatoriaentidadfinanciadoras"
            response = requests.request(
                "POST", self.host_api + service, headers=header, data=body)
            return response.text
        return None

    def get_management_units(self) -> str:
        """
        Método para ver las unidades de gestión que están disponibles
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgiusr/unidades"
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            return response.text
        return None

    def get_management_models(self) -> str:
        """
        Método para ver los modelos de gestión que están disponibles
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgicsp/modelounidades"
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            return response.text
        return None

    def get_subject_area_announcement(self, id: int) -> str:
        """
        Método para ver el área temática de una convocatoria
        :param id identificador de la convocatoria
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgicsp/convocatorias/" + \
                str(id) + "/convocatoriaareatematicas"
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            return response.text
        return None

    def get_forms(self, filters=None) -> str:
        """
        Método para consultar solucitudes
        :param filters filtros de búsqueda
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgicsp/solicitudes"
            if filters != None:
                service = service + '?q=' + filters
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            return response.text
        return None

    def get_projects(self, filters=None) -> str:
        """
        Método para consultar proyectos
        :param filters filtro de búsqueda
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgicsp/proyectos"
            if filters != None:
                service = service + '?q=' + filters
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_conveners_call(self, id) -> str:
        """
        Método encargado de obtener la lista de entidades convocantes de una "convocatoria".
        :param id identificador convocatoria
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            url = self.host_api + '/sgicsp/' + 'convocatorias/' + \
                str(id) + '/convocatoriaentidadconvocantes'
            response = requests.request("GET", url=url, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_conveners_project(self, id) -> str:
        """
        Método encargado de obtener la lista de entidades convocantes de un "proyecto".
        :param id identificador proyecto
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            url = self.host_api + '/sgicsp/proyectos/' + \
                str(id) + '/entidadconvocantes'
            response = requests.request("GET", url=url, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_financing_entity_call(self, id) -> str:
        """
        Método encargado de obtener la lista de entidades financiadoras de una "convocatoria".
        :param id identificador convocatoria
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'X-Page-Size': '5',
                    'X-Page': '0',
                    'Authorization': 'Bearer ' + self.oauth_token}
            url = self.host_api + '/sgicsp/' + 'convocatorias/' + \
                str(id) + '/convocatoriaentidadfinanciadoras'
            response = requests.request("GET", url=url, headers=header)
            return response.text
        return None

    def get_project_team(self, id) -> str:
        """
        Método encargado de obtener la lista de investigadores que forman parte del
        equipo de un proyecto.
        :param id identificador del proyecto
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgicsp/proyectos/' + str(id) + '/equipos'
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_project_budget(self, id) -> str:
        """
        Método encargado de obtener el presupuesto de un proyecto.
        :param id identificador del proyecto
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgicsp/proyectos/' + str(id) + '/presupuesto-totales'
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_inventions(self, filters=None):
        """
        Método encargado de obtener las invenciones.
        :param filters filtros de búsqueda
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgipii/invenciones'
            if filters != None:
                service += '?q=' + filters
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_inventors_invention(self, id):
        """
        Método que obtiene los inventores de una invención, 
        los inventores son considerados como los autores de la invención.
        :param id identificador de la invención
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgipii/invenciones/' + str(id) + '/invencion-inventores'
            response = requests.request(
                "GET",  self.host_api + service, headers=header)

            if response.status_code == 200:
                return response.text
        return None

    def get_imcumbent_invention(self, id):
        """
        Método que obtiene los titulares de una invención, estos titulares son organizaciones
        o empresas.
        :param id identificador de la invención
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'X-Page-Size': '5',
                    'X-Page': '0',
                    'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgipii/periodostitularidad/' + str(id) + '/titulares'
            response = requests.request(
                "GET",  self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_request_invention(self, id, filters: str = None):
        """
        Método encargado de obtener las solicitudes de protección de una invención.
        :param id identificador de la invención
        :param filters filtros de búsqueda
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'X-Page-Size': '5',
                    'X-Page': '0',
                    'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgipii/invenciones/' + str(id) + '/solicitudesproteccion'
            if filters != None:
                service = service + '?q=' + filters
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_thesis(self, filters: str = None):
        """
        Método para consultar las tesis.
        :param filters filtros de búsqueda
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgp/direccion-tesis'
            if filters != None:
                service = service + '?' + filters
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_inventions(self, filters=None):
        """
        Método encargado de obtener las invenciones.
        :param filters filtros de búsqueda
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgipii/invenciones'
            if filters != None:
                service += '?q=' + filters
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_imcumbent_invention(self, id):
        """
        Método que obtiene los titulares de una invención, estos titulares son organizaciones
        o empresas.
        :param id identificador de la invención
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'X-Page-Size': '5',
                    'X-Page': '0',
                    'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgipii/periodostitularidad/' + str(id) + '/titulares'
            response = requests.request(
                "GET",  self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_request_invention(self, id, filters: str = None):
        """
        Método encargado de obtener las solicitudes de protección de una invención.
        :param id identificador de la invención
        :param filters filtros de búsqueda
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'X-Page-Size': '5',
                    'X-Page': '0',
                    'Authorization': 'Bearer ' + self.oauth_token}

            service = '/sgipii/invenciones/' + str(id) + '/solicitudesproteccion'
            if filters != None:
                service = service + '?q=' + filters
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_company(self, id) -> str:
        """
        Método encargado de obtener la información de una empresa utilizando el servicio
        de gestión de empresas de la UM.
        :param id identificador de la empresa
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgemp/empresas/' + str(id)
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code != 200:
                time.sleep(15)
                response = requests.request(
                    "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_person(self, id) -> str:
        """
        Método encargado de obtener la información de una persona utilizando el servicio
        de gestión de personas de la UM.
        :param id identificador de la persona
        :return str respuesta obtenida
        """
        if id and self.auth():
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgp/personas/' + str(id)

            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code != 200:
                time.sleep(15)
                response = requests.request(
                    "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_person_filter(self, filters=None) -> str:
        """
        Método encargado de obtener la información de una persona utilizando el servicio
        de gestión de personas de la UM.
        :param filters filtros de búsqueda
        :return str respuesta obtenida
        """
        if self.auth():
            service = '/sgp/personas/'
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            if filters != None:
                service = service + filters
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code != 200:
                time.sleep(15)
                response = requests.request(
                    "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None

    def get_companies(self, filtros=None) -> str:
        """
        Método para consultar empresas.
        :param filters filtros de búsqueda
        :return str respuesta obtenida
        """
        if self.auth():
            header = {'Accept': 'application/json',
                    'Authorization': 'Bearer ' + self.oauth_token}
            service = "/sgemp/empresas"
            if filtros != None:
                service = service + '?q=' + filtros
            response = requests.request(
                "GET", self.host_api + service, headers=header)
            if response.status_code != 200:
                time.sleep(15)
                response = requests.request(
                    "GET", self.host_api + service, headers=header)
            if response.status_code == 200:
                return response.text
        return None
