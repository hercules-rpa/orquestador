class RO:
    def __init__(self, titulo:str='', doi:str='', tipo_publicacion:str = '', 
        fecha_publicacion:str = '', wos_cites:str ='',posicion:str = '', n_revistas:str='',
        revista:str = '',impacto:str='',cuartil:str = '', autores:str = '',
        nautores:int = 0, posicion_autor:int=0):
        
        self.titulo:str = titulo
        self.doi:str = doi
        self.tipo_publicacion = tipo_publicacion
        self.fecha_publicacion = fecha_publicacion
        self.wos_cites = wos_cites
        self.posicion:str = posicion
        self.revista = revista
        self.impacto = impacto
        self.cuartil = cuartil
        self.n_revistas:str = n_revistas        
        self.n_paginas = ''
        self.issn = ''
        self.editorial = ''
        self.volumen = ''
        self.numero = ''
        self.pag_inicio = ''
        self.pag_fin = ''
        self.scopus_cites = ''
        self.ss_cites = ''
        self.autores = autores
        if self.autores:
            print('autores: ' + self.autores)
        self.nautores = nautores
        self.posicion_autor:int = posicion_autor
        
    def get_anio(self) -> str:
        return self.fecha_publicacion.split("-")[2]

    def get_npaginas(self) -> int:
        if(self.pag_fin != '' and self.pag_inicio != ''):
            return int(self.pag_fin) - int(self.pag_inicio)
        return 0

    def get_cuartil(self) -> int:
        if self.cuartil:
            return int(self.cuartil)
        return 0

    def get_decil(self) -> int:
        decil: int = 0
        if self.posicion and self.n_revistas:
            result = (int(self.posicion) * 10) / int(self.n_revistas)
            if result <= 1:
                decil = 1
            elif result > 1:
                decil = round(result)
        return decil

    def get_tercil(self) -> int:
        tercil: int = 0
        if self.posicion and self.n_revistas:
            result = (int(self.posicion) * 3) / int(self.n_revistas)
            if result <= 1:
                tercil = 1
            elif result > 1:
                tercil = round(result)
        return tercil