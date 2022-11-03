from selenium import webdriver
from selenium.webdriver.common.by import By

import pathlib
import os
import time



# path to download directory
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'downloads_convocatoria')
if not os.path.isdir(DOWNLOAD_DIR): 
    os.mkdir(DOWNLOAD_DIR)

class CaixaWebScraper():
    """Clase para obtener convocatorias abiertas de FundacionCaixa"""
    def __init__(self) -> None:
        self.path = pathlib.Path(__file__).parent.resolve()
        self.opciones = self.set_options()
        self.driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", options=self.opciones)
        #self.driver = webdriver.Chrome(executable_path="C:/Users/jesus/git/rpa-plataform/hercules-rpa/webdriver/chromedriver.exe", options=self.opciones)
    def set_options(self):
        """"
        Establecer opciones para Chrome driver
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        #options.add_argument('--headless') # sin cabecera
        options.add_argument('--no-sandbox')# not important
        options.add_argument('--allow-running-insecure-content')
        options.add_experimental_option('prefs', {
                "download.default_directory": DOWNLOAD_DIR, #Change default directory for downloads
                "download.prompt_for_download": False, #To auto download the file
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
                })

        return options

    def get_refs(self):
        """
        Obtener elementos de cada convocatoria
        """

        self.driver.get('https://fundacionlacaixa.org/es/convocatorias-caixaresearch-investigacion-innovacion')

        # cuando se ejectuta en modo no headless hay que aceptar cookies
        try:
            cookies = self.driver.find_element(By.ID, 'onetrust-accept-btn-handler')
            cookies.click()
        except Exception as e:
            print(e)

        # buscar el elemento main que contiene referencias a las convocatorias
        a = self.driver.find_element(By.CLASS_NAME, "main")
        # en cada elemento 'a' de main se encuentra una convocatoria
        refs = a.find_elements(By.TAG_NAME, 'a')

        return refs


    def get_titles_links(self, refs):
        """

        """
        links = []
        titles = []
        for _, ref in enumerate(refs):
            title = ref.find_element(By.TAG_NAME, 'span').text
            if title not in ['INFORMACIÓN DE LAS CONVOCATORIAS', 'CONVOCATORIAS FINALIZADAS']:
                link = ref.get_attribute("href")

                links.append(link)
                titles.append(title)

        return titles, links


    def get_content(self, link):
        """
        Obtener el texto de cada convocatoria
        """

        # dict apartado: texto apartado
        texts_dict = {}

        # abrir enlace de la convocatoria
        self.driver.get(link)

        # encontrar elementos de cada apartado
        headers = self.driver.find_elements(By.CLASS_NAME, 'custom-header')
        heads = [head.text for head in headers if head.text != '']

        # cada apartado tiene ul and li elements que son lineas de texto
        content = self.driver.find_element(By.XPATH, '//div[@class="journal-content-article "]/ul')
        lis = content.find_elements(By.TAG_NAME, 'li')

        for _, li in enumerate(lis):
    
            info_head = li.text.splitlines()
            # si apartado empieza con el nombre de apartado
            if info_head[0] in heads:
                texts_dict[info_head[0]] = info_head[1:]

        return texts_dict


    def get_date(self, contenido):
        """
        Obtener fecha de una convocatoria 
        """
        fecha = None

        # fechas de convocatorias estan en el apartado Fechas clave o Calendario
        for f in ['FECHAS CLAVE', 'CALENDARIO']:
            # intentar sacar el texto del apartado
            if contenido.get(f) is not None:
                status = contenido.get(f)[0].lower()

                # convocatoria abierta
                if 'abiert' in status:
                    # obtener segunda linea del apartado (con la fecha)
                    fecha = contenido.get(f)[1].lower()

                    return fecha
                else:
                    return None


    def get_base_pdf(self):
        """
        Obtener pdf llamado Bases de la convocatoria 
        """

        # encontrar element que contiene documentos
        docs = self.driver.find_element(By.CLASS_NAME, 'contenedor_documentos')
        # obtener lista de documentos
        lists  = docs.find_elements(By.TAG_NAME, 'li')
        for l in lists:
            if 'Bases de la convocatoria' in l.text:
                ref = l.find_element(By.TAG_NAME, 'a').get_attribute("href")
                # abrir enlace (descargar)
                self.driver.get(ref)




    def getDownLoadedFileName(self, waitTime):
        """
        Obtener nombre del fichero descargado (en modo no headless)
        """
        # abrir nueva pestaña
        self.driver.execute_script("window.open()")
        # switch to new tab
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # navigate to chrome downloads
        self.driver.get('chrome://downloads')
        # define the endTime
        endTime = time.time()+waitTime
        while True:
            
            try:
                # ibtener nombre
                name = self.driver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")
                if name:
                    # cerrar la pestaña actual
                    self.driver.close()
                    # dirigirse a la pestaña anterior
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    # obtener ruta completa del ficher descargado
                    filename = os.path.join(DOWNLOAD_DIR, name)
                return  filename
            
            except:
                pass
            time.sleep(1)

            if time.time() > endTime:

                break

       
    def quit_browser(self):
        """
        Cerrar navegador
        """

        self.driver.quit()

    
    def get_download(self):
        """
        Obtener nombre del fichero descargado (headless)
        En el modo headless ha sido imposible obtener el nombre de la convocatoria con el metodo getDownLoadedFileName
        por lo cual si se usa modo headless se obtiene el nombre de manera diferente:
        - se obtiene la lista de ficheros en el directorio DOWNLOAD_DIR
        - se ordena por tiempo de modificacion y con el metodo pop() se obtiene el fichero mas reciente
        """

        files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.pdf')]

        files.sort(key=lambda x: os.path.getmtime(x))
        # obtener la convocatoria mas reciente
        conv = files.pop()
        return conv
