from model.process.Proceso3.Adaptador_Convocatoria import Adaptador_Convocatoria
from model.process.Proceso3.CaixaWebScrapper import CaixaWebScraper
from model.process.Proceso3.Modelo_Ejecucion import Modelo_Ejecucion

import requests
import json


class Adaptador_Caixa(Adaptador_Convocatoria):
    """
    Clase del adaptador para Convocatorias de la CAIXA.
    """
    def __init__(self, server: str="10.208.99.12"):
        self.webscraper = CaixaWebScraper()
        self.array = []
        self.server = server

    def buscar(self, *args: list) -> None:
        """
        Método para buscar por día actual las convocatorias de la BDNS.

        :param args list: Argumento variable con el listado de palabras clave para buscar.
        :return None.
        """
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
                    bbdd_url = "http://" + self.server + ":5000/api/orchestrator/register/convocatorias?url=" + link 
                    response = requests.get(bbdd_url)
                    if response.status_code == 404:
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

    def buscar_fecha(self, fecha_desde: str, fecha_hasta: str, *args: list) -> None:
        """
        Método para buscar por rango de fechas las convocatorias de la BDNS.

        :param fecha_desde str: Fecha en formato string desde dónde se empieza la búsqueda.
        :param fecha_hasta str: Fecha en formato string desde dónde se acaba la búsqueda.
        :param args list: Argumento variable con el listado de palabras clave para buscar.
        :return None.
        """
        self.buscar()

    def notify(self) -> str:
        """
        Método de actualización del proceso.

        :return Devuelve en formato string un log de cómo se ha ejecutado el proceso hasta el momento que se invoca
        """
        headers = {
        'Content-Type': 'application/json'
        }
        payload = json.dumps(self.array)
        bbdd_url = "http://" + self.server + ":5000/api/orchestrator/register/convocatorias"
        response = requests.post(bbdd_url, headers=headers, data=payload)
        return "Se han inyectado en la base de datos. " + str(response.status_code) + " --- " + str(response.text)