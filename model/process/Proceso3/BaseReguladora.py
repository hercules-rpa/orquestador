
class BaseReguladora():

    def __init__(self, id:int=0, id_boe:str = None, titulo:str = None, url:str = None, 
        seccion:str = None, departamento:str = None, notificada:bool = False):
        self.id = id
        self.id_boe = id_boe
        self.titulo = titulo
        self.url = url
        self.notificada = notificada
        self.seccion = seccion
        self.departamento = departamento
    
    def set_properties(self,tagName: str, nodo):
        """Función encargada de hidratar las propiedades de una base reguladora"""
        if tagName == 'titulo':
            self.titulo = nodo.firstChild.data
        if tagName == 'urlPdf':
            self.url = nodo.firstChild.data
    
    def get_titulotruncado(self):
        if len(self.titulo) > 500:
                return self.titulo[:485] + '...'
        return self.titulo
        
    def get_url_absoluta(self):
        url = self.url
        if "www.boe.es" not in self.url:
            url = "www.boe.es" + self.url
        if "https://" not in self.url:
            url = "https://" + url
        
        return url

    def get_url_acortada(self):
        url = self.url
        if "www.boe.es" not in self.url:
            url = "www.boe.es" + self.url
        return url