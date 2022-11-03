

"""
Estructura para modelar los ficheros que se van a poder subir al CDN
"""

class File():
    def __init__(self, id = None, name = None,url_cdn = None):
        self.id = id
        self.name = name
        self.url_cdn = url_cdn


    def get_name(self): 
        """
        Método para obtener el nombre del fichero
        :return str nombre del fichero
        """
        return self.name.split(".")[0]

    def get_format(self):
        """
        Método para obtener el formato del fichero
        :return str formato del fichero
        """
        return self.name.split(".")[-1]

    def get_url_cdn(self):
        """
        Método para obtener la url directa del CDN en el que se encuentra para descargar directamente el fichero
        :return str (url CDN)
        """
        return self.url_cdn
