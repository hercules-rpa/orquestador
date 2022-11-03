
class RegulatoryBase():

    def __init__(self, id:int=0, id_boe:str = None, title:str = None, url:str = None, 
        section:str = None, departament:str = None, notify:bool = False):
        self.id = id
        self.id_boe = id_boe
        self.title = title
        self.url = url
        self.notify = notify
        self.section = section
        self.departament = departament
    
    def set_properties(self,tagName: str, nodo):
        """Función encargada de hidratar las propiedades de una base reguladora"""
        if tagName == 'titulo':
            self.title = nodo.firstChild.data
        if tagName == 'urlPdf':
            self.url = nodo.firstChild.data
    
    def get_short_title(self):
        if len(self.title) > 500:
                return self.title[:485] + '...'
        return self.title
        
    def get_absolute_url(self):
        url = self.url
        if "www.boe.es" not in self.url:
            url = "www.boe.es" + self.url
        if "https://" not in self.url:
            url = "https://" + url
        
        return url

    def get_short_url(self):
        url = self.url
        if "www.boe.es" not in self.url:
            url = "www.boe.es" + self.url
        return url