import requests
import base64
import datetime
import time

class SGI():

    host = "https://sgi.demo.treelogic.com"
    host_api = host + "/api"
    host_ic_api = "http://sgi.ic.corp.treelogic.com/api"
    oauth_url = "https://sgi.demo.treelogic.com/auth/realms/sgi/protocol/openid-connect/token"
    oauth_url_ic = "http://sgi.ic.corp.treelogic.com/auth/realms/sgi/protocol/openid-connect/token"
    oauth_grant_type = "password"
    oauth_username = "gestor-rpa"
    oauth_password = "gestor-rpa-2021"
    oauth_client_id = b"front"
    oauth_client_secret = ""
    oauth_scopes = "openid profile"
    oauth_token = ""
    oauth_timestamp = 0.0
    oauth_token_expiresintime = 0.0

    """
        Método de autenticación contra el entorno de desarrollo, se debe ejecutar antes de cada llamada.
    """

    def auth(self) -> None:
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


    def auth_ic(self):
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
                'password': 'gestor-rpa'
            }
            response = requests.post(self.oauth_url_ic, headers=header, data=body)
            self.oauth_token = response.json()['access_token']
            self.oauth_timestamp = datetime.datetime.now()
            if response.json()['expires_in']:
                self.oauth_token_expiresintime = int(
                    response.json()['expires_in']) * 1000

    """
        Método para obtener las convocatorias. Se puede filtrar añadiendo un string de filtro como por ejemplo:
            titulo=="Resolución de 3 de febrero de 2022 del Centro de Investigaciones Sociológicas 
            por la que se publica la convocatoria de subvenciones para formación e investigación en 
            materias de interés para el organismo, para el año 2022"
    """

    def get_convocatorias(self, filtros=None) -> str:
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgicsp/convocatorias"
        if filtros != None:
            service = service + '?q=' + filtros
        response = requests.request("GET", self.host_api + service, headers=header)
        return response.text

    def get_convocatoria(self, id) -> str:
        """
        Método encargado de obtener una convocatoria en base a un identificador
        """
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgicsp/convocatorias/" + str(id)
        response = requests.request("GET", self.host_api + service, headers=header)
        return response.text

    def get_areastematicas(self):
        """
        Método encargado de obtener todas las áreas temáticas
        """
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgicsp/areatematicas"
        response = requests.request("GET", self.host_api + service, headers=header)
        return response.text


    """
        Método para insertar una convocatoria en el entorno de pruebas.
    """

    def post_convocatoria(self, body) -> str:
        self.auth()
        header = {'Content-Type': 'application/json',
                  'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgicsp/convocatorias"
        response = requests.request(
            "POST", self.host_api + service, headers=header, data=body)
        return response.text

    """
        Método para insertar una entidad convocante a una convocatoria en el entorno de pruebas.
    """   
    def post_entidadconvocante_convocatoria(self, body) -> str:
        self.auth()
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgicsp/convocatoriaentidadconvocantes"
        response = requests.request("POST", self.host_api + service, headers=header, data=body)
        return response.text

    """
        Método para insertar una entidad financiadora a una convocatoria en el entorno de pruebas.
    """   
    def post_entidadfinanciadora_convocatoria(self, body) -> str:
        self.auth()
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgicsp/convocatoriaentidadfinanciadoras"
        response = requests.request("POST", self.host_api + service, headers=header, data=body)
        return response.text

    """
        Método para ver las unidades de gestión que están disponibles
    """

    def get_unidades_gestion(self) -> str:
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgiusr/unidades"
        response = requests.request("GET", self.host_api + service, headers=header)
        return response.text

    """
        Método para ver los modelos de gestión que están disponibles
    """

    def get_modelos_gestion(self) -> str:
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgicsp/modelounidades"
        response = requests.request("GET", self.host_api + service, headers=header)
        return response.text

    """
        Método para ver el área temática de una convocatoria
    """

    def get_convocatoria_area_tematica(self, id: int) -> str:
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgicsp/convocatorias/" + str(id) + "/convocatoriaareatematicas"
        response = requests.request("GET", self.host_api + service, headers=header)
        return response.text

    """
        Método para consultar solucitudes
    """

    def get_solicitudes(self, filtros=None) -> str:
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgicsp/solicitudes"
        if filtros != None:
            service = service + '?q=' + filtros
        response = requests.request("GET", self.host_api + service, headers=header)
        return response.text

    def get_proyectos(self, filtros=None) -> str:
        """
        Método para consultar proyectos
        """
        print('get_proyectos')
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgicsp/proyectos"
        if filtros != None:
            service = service + '?q=' + filtros
        response = requests.request("GET", self.host_api + service, headers=header)
        print(response.text)
        if response.status_code == 200:
            return response.text
        return None

    def get_entidades_convocantes_convocatoria(self, id) -> str:
        """
        Método encargado de obtener la lista de entidades convocantes de una "convocatoria".
        """
        self.auth()
        #print('get_entidades_convocantes_convocatoria, id ' + str(id))
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        url = self.host_api + '/sgicsp/' + 'convocatorias/' + \
            str(id) + '/convocatoriaentidadconvocantes'
        response = requests.request("GET", url=url, headers=header)
        if response.status_code == 200:
            return response.text
        return None

    def get_entidades_convocantes_proyecto(self, id) -> str:
        """
        Método encargado de obtener la lista de entidades convocantes de un "proyecto".
        """
        #print('get_entidades_convocantes_proyecto')
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        url = self.host_api + '/sgicsp/proyectos/' + \
            str(id) + '/entidadconvocantes'
        response = requests.request("GET", url=url, headers=header)
        if response.status_code == 200:
            return response.text
        return None



    def get_entidades_financiadora_convocatoria(self, id) -> str:
        """
        Método encargado de obtener la lista de entidades financiadoras de una "convocatoria".
        """
        self.auth()
        header = {'X-Page-Size': '5',
                  'X-Page': '0',
                  'Authorization': 'Bearer ' + self.oauth_token}
        url = self.host_api + '/sgicsp/' + 'convocatorias/' + \
            str(id) + '/convocatoriaentidadfinanciadoras'
        response = requests.request("GET", url=url, headers=header)
        return response.text


    """
        Método para consultar equipos de proyecto.
    """
    def get_equipo_proyecto(self, id) -> str:
        """
        Método encargado de obtener la lista de investigadores que forman parte del
        equipo de un proyecto.
        """
        #print('get_equipo_proyecto')
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgicsp/proyectos/' + str(id) + '/equipos'
        response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code == 200:
            return response.text
        return None

    """
        Método para consultar presupuestos de proyectos.
    """
    def get_presupuesto_proyecto(self, id) -> str:
        """
        Método encargado de obtener el presupuesto de un proyecto.
        """
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgicsp/proyectos/' + str(id) + '/presupuesto-totales'
        response = requests.request("GET", self.host_api + service, headers=header)
        print(response)
        print(response.text)
        if response.status_code == 200:
            return response.text
        return None

    def get_invenciones(self, filtros=None):
        """
        Método encargado de obtener las invenciones.
        """
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgipii/invenciones'
        if filtros != None:
            service += '?q=' + filtros
        response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code == 200:
            return response.text
        return None

    def get_inventores_invencion(self, id):
        """
        Método que obtiene los inventores de una invención, 
        los inventores son considerados como los autores de la invención.
        """
        self.auth()
        #print('get_inventores_invencion  id: ' + str(id))
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgipii/invenciones/' + str(id) + '/invencion-inventores'
        response = requests.request("GET",  self.host_api + service, headers=header)
        
        if response.status_code == 200:
            return response.text
        return None

    def get_titulares_invencion(self, id):
        """
        Método que obtiene los titulares de una invención, estos titulares son organizaciones
        o empresas.
        """
        self.auth()
        #print('get_titulares_invencion, id: ' + str(id))
        header = {'X-Page-Size': '5',
                  'X-Page': '0',
                  'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgipii/periodostitularidad/' + str(id) + '/titulares'
        response = requests.request("GET",  self.host_api + service, headers=header)
        if response.status_code == 200:
            return response.text
        return None

    def get_solicitudes_invencion(self, id, filtros: str = None):
        """
        Método encargado de obtener las solicitudes de protección de una invención.
        """
        self.auth()
        #print('get_solicitudes_invencion, id: ' + str(id))
        header = {'X-Page-Size': '5',
                  'X-Page': '0',
                  'Authorization': 'Bearer ' + self.oauth_token}    

        service = '/sgipii/invenciones/' + str(id) + '/solicitudesproteccion'
        if filtros != None:
            service = service + '?q=' + filtros
        response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code == 200:
            return response.text
        return None

    def get_tesis(self, filtros:str = None):
        """
        Método para consultar las tesis.
        """
        print('get_tesis + ')
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgp/direccion-tesis'
        if filtros != None:
            service = service + '?' + filtros
        print(self.host_api + service)
        response = requests.request("GET", self.host_api + service, headers=header)
        print(response)
        if response.status_code == 200:
            return response.text
        return None

    def get_empresa(self, id) -> str:
        """
        Método encargado de obtener la información de una empresa utilizando el servicio
        de gestión de empresas de la UM.
        """
        #print('get_empresa, id: ' + str(id))
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgipii/empresas/' + str(id)
        response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code == 200:
            return response.text
        return None

    def get_invenciones(self, filtros=None):
        """
        Método encargado de obtener las invenciones.
        """
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgipii/invenciones'
        if filtros != None:
            service += '?q=' + filtros
        response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code == 200:
            return response.text
        return None

    def get_inventores_invencion(self, id):
        """
        Método que obtiene los inventores de una invención, 
        los inventores son considerados como los autores de la invención.
        """
        self.auth()
        #print('get_inventores_invencion  id: ' + str(id))
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgipii/invenciones/' + str(id) + '/invencion-inventores'
        response = requests.request("GET",  self.host_api + service, headers=header)
        
        if response.status_code == 200:
            return response.text
        return None

    def get_titulares_invencion(self, id):
        """
        Método que obtiene los titulares de una invención, estos titulares son organizaciones
        o empresas.
        """
        self.auth()
        #print('get_titulares_invencion, id: ' + str(id))
        header = {'X-Page-Size': '5',
                  'X-Page': '0',
                  'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgipii/periodostitularidad/' + str(id) + '/titulares'
        response = requests.request("GET",  self.host_api + service, headers=header)
        if response.status_code == 200:
            return response.text
        return None

    def get_solicitudes_invencion(self, id, filtros: str = None):
        """
        Método encargado de obtener las solicitudes de protección de una invención.
        """
        self.auth()
        #print('get_solicitudes_invencion, id: ' + str(id))
        header = {'X-Page-Size': '5',
                  'X-Page': '0',
                  'Authorization': 'Bearer ' + self.oauth_token}    

        service = '/sgipii/invenciones/' + str(id) + '/solicitudesproteccion'
        if filtros != None:
            service = service + '?q=' + filtros
        response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code == 200:
            return response.text
        return None

    def get_tesis(self, filtros:str = None):
        """
        Método para consultar las tesis.
        """
        self.auth_ic()
        print('get_tesis')
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgp/direccion-tesis'
        if filtros != None:
            service = service + '?' + filtros
        response = requests.request("GET", self.host_ic_api + service, headers=header)
        print(response)
        if response.status_code == 200:
            return response.text
        return None

    def get_empresa(self, id) -> str:

        """
        Método encargado de obtener la información de una empresa utilizando el servicio
        de gestión de empresas de la UM.
        """
        self.auth()
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        service = '/sgemp/empresas/' + str(id)
        response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code != 200:
            time.sleep(15)
            response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code == 200:
            return response.text
        return None
        

    def get_persona(self, id) -> str:
        """
        Método encargado de obtener la información de una persona utilizando el servicio
        de gestión de personas de la UM.
        """
        #print('get_persona, id: ' + str(id))
        if id:
            self.auth()
            header = {'Authorization': 'Bearer ' + self.oauth_token}
            service = '/sgp/personas/' + str(id)
            
            response = requests.request("GET", self.host_api + service, headers=header)
            if response.status_code != 200:
                time.sleep(15)
                response = requests.request("GET", self.host_api + service, headers=header)
            #print(response)
            if response.status_code == 200:
                return response.text
        return None

    def get_persona_filter(self, filtros=None) -> str:
        """
        Método encargado de obtener la información de una persona utilizando el servicio
        de gestión de personas de la UM.
        """
        self.auth()
        service = '/sgp/personas/'
        header = {'Authorization': 'Bearer ' + self.oauth_token}
        if filtros != None:
            service = service + filtros
        response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code != 200:
            time.sleep(15)
            response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code == 200:
            return response.text
        return None

    """
    Método para consultar empresas.
    """
    def get_empresas(self, filtros=None) -> str:
        self.auth()
        header = {'Accept': 'application/json', 'Authorization': 'Bearer ' + self.oauth_token}
        service = "/sgemp/empresas"
        if filtros != None:
            service = service + '?q=' + filtros
        response = requests.request("GET", self.host_api + service, headers=header)
        if response.status_code != 200:
            time.sleep(15)
            response = requests.request("GET", self.host_api + service, headers=header)
            #print(response)
        if response.status_code == 200:
            return response.text
        return None




if __name__ == "__main__":
    sgi = SGI()
    # print(sgi.get_solicitudes("solicitanteRef=="+str("09371654")))
    # print(sgi.get_proyectos()[0])
    # print(sgi.get_equipo_proyecto(1))
    print(sgi.get_entidades_financiadora_convocatoria(
            1))
    
