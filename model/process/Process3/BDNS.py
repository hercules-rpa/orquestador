from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from model.process.Process3.Execution_Model import Execution_Model
from rpa_robot.ControllerSettings import ControllerSettings
from rpa_robot.ControllerRobot import ControllerRobot
from model.RPA import RPA

import time
import csv
import json
import requests
import os

DOWNLOAD_DIR = "rpa_robot/files/"
cs = ControllerSettings()

class BDNS:

    def __init__(self, server, port):
        if (server == "" and port == ""):
            self.array = []
            self.msg_notify = ""
        else:
            self.array = []
            self.msg_notify = ""
            self.server = server
            self.port = port
            self.conf = cs.get_process_settings(self.server, self.port)
            cr = ControllerRobot()
            self.rpa = RPA(cr.robot.token)

    def search_with_date(self, dD: time, dH: time, *args: str) -> dict:
        """
        Método para buscar, por fecha, convocatorias. Las convocatorias, adicionalmente, se guardan en un archivo CSV.

        :param dD time: Objeto time con la fecha inicial para la búsqueda.
        :param dH time: Objeto time con la fecha final para la búsqueda.
        :param args str: Argumento variable con las palabras clave para la búsqueda.
        :return dict con los datos de las convocatorias que cumplen los criterios de la búsqueda.
        """
        
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(accept_downloads=True)

            page = context.new_page()
            page.goto(
                self.conf['bdns_search'])
            page.click("input[name=\"titulo\"]")
            if len(args) == 1:
                args = args[0].split()
                #page.locator("select[name=\"tipoBusqPalab\"]").select_option("2")
                #page.fill("input[name=\"titulo\"]", args[0])
            else:
                args = ['investigación', 'i+d']
                #page.fill("input[name=\"titulo\"]", "investigacion")
            page.click("input[name=\"fecDesde\"]")
            page.fill("input[name=\"fecDesde\"]", time.strftime('%d/%m/%Y', dD))
            page.click("input[name=\"fecHasta\"]")
            page.fill("input[name=\"fecHasta\"]", time.strftime('%d/%m/%Y', dH))
            page.click("select[name=\"regionalizacion\"]")
            page.press("select[name=\"regionalizacion\"]", "ArrowUp")
            page.press("select[name=\"regionalizacion\"]", "ArrowUp")
            page.click("button:has-text(\"Buscar\")")

            with page.expect_download(timeout=0) as download_info:
                page.click("img[alt=\"icono csv\"]")
            download = download_info.value

            download.save_as("convocatorias.csv")

            context.close()
            browser.close()
        data = {}
        self.array = []
        with open('convocatorias.csv', 'r', encoding='ISO-8859-1') as csvfile:
            lines = csv.DictReader(csvfile, delimiter=',')
            for row in lines:
                bbdd_url = self.server + ":" + self.port +"/api/orchestrator/register/convocatorias?url=" + self.conf['bdns_url'] + "GE/es/convocatoria/" + row['Código BDNS']
                response = self.rpa.get(bbdd_url)
                if self.search_name_csv(row['Título de la convocatoria'].lower(), args) and response.status_code == 404:
                    key = row['Código BDNS']
                    data[key] = row
                    insert = {}
                    insert['fecha_publicacion'] = time.mktime(time.strptime(data[key]['Fecha de registro'],'%d/%m/%Y'))
                    insert['titulo'] = data[key]['Título de la convocatoria']
                    insert['_from'] = 'BDNS'
                    insert['url'] = self.conf['bdns_url'] + '/GE/es/convocatoria/' + data[key]['Código BDNS']
                    if 'transferencia' in str(data[key]['Título de la convocatoria']).lower():
                        insert['unidad_gestion'] = 'OTRI'
                    elif 'investigacion' in str(data[key]['Título de la convocatoria']).lower() or 'desarrollo' in str(data[key]['Título de la convocatoria']).lower():
                        insert['unidad_gestion'] = 'UGI'
                    else:
                        insert['unidad_gestion'] = 'OTRI UGI'
                    if 'ayuda' in str(data[key]['Título de la convocatoria']).lower() or 'subvencion' in str(data[key]['Título de la convocatoria']).lower():
                        insert['modelo_ejecucion'] = Execution_Model.SUBVENCION.value
                    elif 'prestamo' in str(data[key]['Título de la convocatoria']).lower():
                        insert['modelo_ejecucion'] = Execution_Model.PRESTAMO.value
                    elif 'presentacion factura' in str(data[key]['Título de la convocatoria']).lower() or 'facturación' in str(data[key]['Título de la convocatoria']).lower():
                        insert['modelo_ejecucion'] = Execution_Model.FACTURACION.value
                    insert['entidad_gestora'] = data[key]['Departamento']
                    insert['entidad_convocante'] = data[key]['Órgano']
                    insert['notificada'] = False
                    self.array.append(insert)
        with open('convocatorias.json', 'w', encoding='utf-8') as jsonf:
            json.dump(data, jsonf, ensure_ascii=False, indent=4)
        self.insert_database(self.array)
        return data

    def search_numbdns_csv(self, file: str, num_bdns: int) -> str:
        """
        Método que te devuelve a través del número de la BDNS la línea del archivo CSV de convocatorias, si existe.

        :param file str: Path del archivo CSV con las convocatorias de la búsqueda.
        :param num_bdns int: Número de la BDNS.
        :return String con la línea de la convocatoria si existe. Sino te devuelve una cadena vacía.
        """
        with open(file, 'r', encoding='ISO-8859-1') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for row in lines:
                if row[0] == num_bdns:
                    return row
            return ""

    def search_name_csv(self, titulo: str, conjunto: list) -> bool:
        """
        Método que te devuelve si una palabra está en una frase.

        :param titulo str: Título de la convocatoria.
        :param conjunto list: Lista de palabras.
        :return Si la palabra está contenida en el título.
        """
        return any(word in titulo for word in conjunto)

    def search_name_csv_file(self, path: str, conjunto: list) -> bool:
        """
        Método que te devuelve dado un listado de palabras si la convocatoria existe.

        :param path str: Path del archivo CSV con las convocatorias de la búsqueda.
        :param conjunto list: Lista de palabras.
        :return String con la línea de la convocatoria si existe. Sino te devuelve una cadena vacía.
        """
        with open(path, 'r', encoding='ISO-8859-1') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for row in lines:
                if any(word in row[6].lower() for word in conjunto):
                    return True
            return False

    def obtain_resources_bdns(self, num_bdns: int) -> list:
        """
        Método para obtener los recursos de una convocatoria.

        :param num_bdns int: Número de la bdns.
        :return list Lista con los paths de los recursos.
        """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto(
                self.conf['bdns_url'] + "GE/es/convocatorias")
            url = self.conf['bdns_url'] + "busqueda?type=getdocsconv&numcov=" + \
                str(num_bdns)+"&_search=false&nd=" + \
                str(round(time.time()/10))+"&rows=50&page=1&sidx=&sord=asc"
            page.goto(url)
            soup = BeautifulSoup(page.content(), 'html.parser')
            JSON = json.loads(soup.find('pre').text)
            name_resources = []
            if JSON != None and JSON['rows']:
                if not os.path.exists(DOWNLOAD_DIR):
                    os.makedirs(DOWNLOAD_DIR)
                for j in JSON['rows']:
                    url = self.conf['bdns_url'] + "GE/es/convocatoria/" + \
                        str(num_bdns) + "/document/" + str(j[0])
                    response = requests.request("GET", url, verify=False)
                    with open(DOWNLOAD_DIR + str(num_bdns) + '_' + str(j[3]), 'wb') as file:
                        file.write(response.content)
                    name_resources.append(DOWNLOAD_DIR + str(num_bdns) + '_' + str(j[3]))
            context.close()
            browser.close()
            return name_resources

    def obtain_resources_bdns_file(self, JSON: json) -> list:
        """
        Método para obtener el nombre de los ficheros descargados.

        :param JSON json: JSON con la información de una convocatoria. test.
        :return nombre de los recursos en una lista.
        """
        name_resources = []
        if JSON != None and JSON['rows']:
            return JSON['rows']
        return name_resources

    def obtain_data_bdns(self, num_bdns: int) -> dict:
        """
        Método para obtener una ampliación de la información de las convocatorias.

        :param num_bdns int: Número de BDNS.
        :return Diccionario con la información ampliada.
        """
        url = self.conf['bdns_url'] + 'GE/es/convocatoria/' + \
            str(num_bdns)
        response = requests.request('GET', url, verify=False)
        dicc = {}
        soup = BeautifulSoup(response.text, 'html.parser')
        i = 0
        for link in soup.find_all('div'):
            if link.find('h3') != None:
                if link.find('p') != None:
                    dicc[link.find('h3').text] = link.find('p').text
                elif link.find('li') != None:
                    dicc[link.find('h3').text] = ''.join(e.text for e in link.find_all('li'))
        return dicc
        
    def obtain_data_bdns_file(self, path: str) -> dict:
        """
        Método para obtener una ampliación de la información de las convocatorias a través de un fichero.

        :param path str: Path del fichero.
        :return Diccionario con la información ampliada.
        """
        with open(path, 'r', encoding='ISO-8859-1') as file:
            response_text = file.read()
            file.close()
        dicc = {}
        soup = BeautifulSoup(response_text, 'html.parser')
        i = 0
        for link in soup.find_all('div'):
            if link.find('h3') != None:
                if link.find('p') != None:
                    dicc[link.find('h3').text] = link.find('p').text
                elif link.find('li') != None:
                    dicc[link.find('h3').text] = ''.join(e.text for e in link.find_all('li'))
        return dicc

    def insert_database(self, array: list) -> None:
        """
        Método que inserta en la base de datos interna las convocatorias pasadas por parámetro.

        :param array list: Array con las convocatorias a insertar.
        """
        self.msg_notify = ""
        payload = json.dumps(array)
        bbdd_url = self.server + ":" + self.port +"/api/orchestrator/register/convocatorias"
        response = self.rpa.post(bbdd_url, payload)
        self.msg_notify = str(response.status_code) + " --- " + response.text

    def notify(self) -> str:
        """
        Método para devolver un mensaje de log del proceso.

        :return str mensaje de log.
        """
        return self.msg_notify