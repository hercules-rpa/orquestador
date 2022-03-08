from sqlalchemy import false


class BaseReguladora():

    def __init__(self, id:int=0, id_boe:str = None, titulo:str = None, url:str = None, notificada:bool = False):
        self.id = id
        self.id_boe = id_boe
        self.titulo = titulo
        self.url = url
        self.notificada = notificada
    
    def get_titulotruncado(self):
        if len(self.titulo) > 500:
                return self.titulo[:485] + '...'
        return self.titulo
        
    def get_url(self):
        if "www.boe.es" in self.url:
            return self.url
        return "www.boe.es" + self.url