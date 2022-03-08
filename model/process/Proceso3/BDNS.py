from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from model.process.Proceso3.Modelo_Ejecucion import Modelo_Ejecucion

import time
import csv
import json
import requests
import re

DOWNLOAD_DIR = "epic/rpa_orchestrator/files/"

class BDNS:

    def __init__(self):
        self.array = []
        self.msg_notify = ""

    def search(self, *args):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(accept_downloads=True)
            # Open new page
            page = context.new_page()
            page.goto(
                "https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias")
            page.click("input[name=\"titulo\"]")
            if len(args) == 1:
                args = args[0].split()
                #page.locator("select[name=\"tipoBusqPalab\"]").select_option("2")
                #page.fill("input[name=\"titulo\"]", args[0])
            else:
                args = ['investigacion']
                #page.fill("input[name=\"titulo\"]", "investigacion")
            page.click("select[name=\"regionalizacion\"]")
            page.press("select[name=\"regionalizacion\"]", "ArrowUp")
            page.press("select[name=\"regionalizacion\"]", "ArrowUp")
            page.click("button:has-text(\"Buscar\")")

            with page.expect_download() as download_info:
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
                if any(word in row['Título de la convocatoria'].lower() for word in args):
                    key = row['Código BDNS']
                    data[key] = row
                    insert = {}
                    insert['fecha_publicacion'] = time.mktime(time.strptime(data[key]['Fecha de registro'],'%d/%m/%Y'))
                    insert['titulo'] = data[key]['Título de la convocatoria']
                    insert['_from'] = 'BDNS - ' + data[key]['Administración']
                    insert['url'] = 'https://www.pap.hacienda.gob.es/bdnstrans/GE/es/convocatoria/' + data[key]['Código BDNS']
                    if 'transferencia' in str(data[key]['Título de la convocatoria']).lower():
                        insert['unidad_gestion'] = 'OTRI'
                    elif 'investigacion' in str(data[key]['Título de la convocatoria']).lower() or 'desarrollo' in str(data[key]['Título de la convocatoria']).lower():
                        insert['unidad_gestion'] = 'UGI'
                    else:
                        insert['unidad_gestion'] = 'OTRI UGI'
                    if 'ayuda' in str(data[key]['Título de la convocatoria']).lower() or 'subvencion'  in str(data[key]['Título de la convocatoria']).lower():
                        insert['modelo_ejecucion'] = Modelo_Ejecucion.SUBVENCION.value
                    elif 'prestamo' in str(data[key]['Título de la convocatoria']).lower():
                        insert['modelo_ejecucion'] = Modelo_Ejecucion.PRESTAMO.value
                    elif 'presentacion factura' in str(data[key]['Título de la convocatoria']).lower() or 'facturación' in str(data[key]['Título de la convocatoria']).lower():
                        insert['modelo_ejecucion'] = Modelo_Ejecucion.FACTURACION.value
                    insert['entidad_convocante'] = data[key]['Órgano']
                    insert['notificada'] = False
                    self.array.append(insert)
        with open('convocatorias.json', 'w', encoding='utf-8') as jsonf:
            json.dump(data, jsonf, ensure_ascii=False, indent=4)

        self.insert_database(self.array)
        return data

    def search_with_date(self, dD, dH, *args):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(accept_downloads=True)

            page = context.new_page()
            page.goto(
                "https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias")
            page.click("input[name=\"titulo\"]")
            if len(args) == 1:
                print(args)
                args = args[0].split()
                print(args)
                #page.locator("select[name=\"tipoBusqPalab\"]").select_option("2")
                #page.fill("input[name=\"titulo\"]", args[0])
            else:
                args = ['investigación']
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
                if any(word in row['Título de la convocatoria'].lower() for word in args):
                    key = row['Código BDNS']
                    data[key] = row
                    insert = {}
                    insert['fecha_publicacion'] = time.mktime(time.strptime(data[key]['Fecha de registro'],'%d/%m/%Y'))
                    insert['titulo'] = data[key]['Título de la convocatoria']
                    insert['_from'] = 'BDNS - ' + data[key]['Administración']
                    insert['url'] = 'https://www.pap.hacienda.gob.es/bdnstrans/GE/es/convocatoria/' + data[key]['Código BDNS']
                    if 'transferencia' in str(data[key]['Título de la convocatoria']).lower():
                        insert['unidad_gestion'] = 'OTRI'
                    elif 'investigacion' in str(data[key]['Título de la convocatoria']).lower() or 'desarrollo' in str(data[key]['Título de la convocatoria']).lower():
                        insert['unidad_gestion'] = 'UGI'
                    else:
                        insert['unidad_gestion'] = 'OTRI UGI'
                    if 'ayuda' in str(data[key]['Título de la convocatoria']).lower() or 'subvencion' in str(data[key]['Título de la convocatoria']).lower():
                        insert['modelo_ejecucion'] = Modelo_Ejecucion.SUBVENCION.value
                    elif 'prestamo' in str(data[key]['Título de la convocatoria']).lower():
                        insert['modelo_ejecucion'] = Modelo_Ejecucion.PRESTAMO.value
                    elif 'presentacion factura' in str(data[key]['Título de la convocatoria']).lower() or 'facturación' in str(data[key]['Título de la convocatoria']).lower():
                        insert['modelo_ejecucion'] = Modelo_Ejecucion.FACTURACION.value
                    insert['entidad_gestora'] = data[key]['Departamento']
                    insert['entidad_convocante'] = data[key]['Órgano']
                    insert['notificada'] = False
                    self.array.append(insert)
        with open('convocatorias.json', 'w', encoding='utf-8') as jsonf:
            json.dump(data, jsonf, ensure_ascii=False, indent=4)
        self.insert_database(self.array)
        return data

    def search_numbdns_csv(self, num_bdns) -> str:
        with open('convocatorias.csv', 'r', encoding='ISO-8859-1') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for row in lines:
                if row[0] == num_bdns:
                    return row
            return ""

    def search_name_csv(self, keyword):
        response = {}
        i = 0
        with open('convocatorias.csv', 'r', encoding='ISO-8859-1') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for row in lines:
                for string in row:
                    if re.findall(keyword, string):
                        response[i] = row[0]
                        i += 1
            return response

    def obtain_resources_bdns(self, num_bdns):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto(
                "https://www.pap.hacienda.gob.es/bdnstrans/GE/es/convocatorias")
            url = "https://www.pap.hacienda.gob.es/bdnstrans/busqueda?type=getdocsconv&numcov=" + \
                str(num_bdns)+"&_search=false&nd=" + \
                str(round(time.time()/10))+"&rows=50&page=1&sidx=&sord=asc"
            page.goto(url)
            JSON = json.loads(page.content().split("\">")[1].split("</p")[0])
            name_resources = []
            for j in JSON['rows']:
                url = "https://www.pap.hacienda.gob.es/bdnstrans/GE/es/convocatoria/" + \
                    str(num_bdns) + "/document/" + str(j[0])
                response = requests.request("GET", url, verify=False)
                with open(DOWNLOAD_DIR + num_bdns + '_' + str(j[3]), 'wb') as file:
                    file.write(response.content)
                name_resources.append(num_bdns + '_' + str(j[3]))
            context.close()
            browser.close()
            return name_resources

    def obtain_data_bdns(self, num_bdns):
        url = 'https://www.pap.hacienda.gob.es/bdnstrans/GE/es/convocatoria/' + \
            str(num_bdns)
        response = requests.request('GET', url, verify=False)
        dicc = {}
        soup = BeautifulSoup(response.text, 'html.parser')
        i = 0
        for link in soup.find_all('div'):
            if link.find('h3') != None:
                if link.find('p') != None:
                    dicc[str(link.find('h3'))[4:-5]
                         ] = str(link.find_all('p'))[4:-5]
                elif link.find('li') != None:
                    dicc[str(link.find('h3'))[4:-5]
                         ] = str(link.find_all('li'))[5:-6]
        for key in dicc:
            dicc[key] = re.sub(
                "<p>|</p>|<li>|</li>|<a href=|target=\"_blank\">|</a>", "", dicc[key])
        return dicc

    def insert_database(self, array):
        self.msg_notify = ""
        headers = {
        'Content-Type': 'application/json'
        }
        payload = json.dumps(array)
        bbdd_url = "http://10.208.99.12:5000/api/orchestrator/register/convocatorias"
        response = requests.post(bbdd_url, headers=headers, data=payload)
        self.msg_notify = str(response.status_code) + " --- " + response.text

    def notify(self):
        return self.msg_notify