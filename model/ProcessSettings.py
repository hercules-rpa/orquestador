

"""
Clase para modelar los Ajustes generales del Orquestador
"""
class ProcessSettings():
    def __init__(self,salaprensa_url,ucc_url,boe_url,bdns_url,bdns_search,europe_url,europe_link):
        self.salaprensa_url = salaprensa_url
        self.ucc_url = ucc_url
        self.boe_url = boe_url
        self.bdns_url = bdns_url
        self.bdns_search = bdns_search
        self.europe_url = europe_url
        self.europe_link = europe_link

