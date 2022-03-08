from model.process.Proceso3.Adaptador_Convocatoria import Adaptador_Convocatoria
from model.process.Proceso3.CaixaWebScrapper import CaixaWebScraper
from model.process.Proceso3.Modelo_Ejecucion import Modelo_Ejecucion

import requests
import json

class Adaptador_Caixa(Adaptador_Convocatoria):
    def __init__(self):
        self.webscraper = CaixaWebScraper()
        self.array = []

    def buscar(self, *args):
        conv_dict = {}
        refs = self.webscraper.get_refs()
        titles, links = self.webscraper.get_titles_links(refs)
        for link, title in zip(links, titles):
            try:
                content = self.webscraper.get_content(link)
                date = self.webscraper.get_date(content)
                if date is not None:
                    self.webscraper.get_base_pdf()
                    filename = self.webscraper.get_download()

                    conv_dict[title] = {
                        'date': date, 
                        'filename': filename}
                    insert = {}
                    insert['titulo'] = title
                    insert['_from'] = 'CAIXA'
                    insert['url'] = link
                    insert['entidad_gestora'] = 'CAIXA'
                    insert['entidad_convocante'] = 'CAIXA'
                    insert['unidad_gestion'] = 'CAIXA'
                    if 'ayuda' in str(insert['titulo']).lower() or 'subvencion' in str(insert['titulo']).lower():
                        insert['modelo_ejecucion'] = Modelo_Ejecucion.SUBVENCION.value
                    elif 'prestamo' in str(insert['titulo']).lower():
                        insert['modelo_ejecucion'] = Modelo_Ejecucion.PRESTAMO.value
                    elif 'presentacion factura' in str(insert['titulo']).lower() or 'facturación' in str(insert['titulo']).lower():
                        insert['modelo_ejecucion'] = Modelo_Ejecucion.FACTURACION.value
                    insert['notificada'] = False
                    self.array.append(insert)
            except Exception as e:
                print(e)     
        self.webscraper.quit_browser()

    def buscar_fecha(self, fecha_desde, fecha_hasta, *args):
        self.buscar()

    def notify(self):
        headers = {
        'Content-Type': 'application/json'
        }
        payload = json.dumps(self.array)
        bbdd_url = "http://10.208.99.12:5000/api/orchestrator/register/convocatorias"
        response = requests.post(bbdd_url, headers=headers, data=payload)
        return "Se han inyectado en la base de datos. " + str(response.status_code) + " --- " + str(response.text)