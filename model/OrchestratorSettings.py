

"""
Clase para modelar los Ajustes generales del Orquestador
"""
class OrchestratorSettings():
    def __init__(self,id_orch,name,company,pathlog_store, cdn_url):
        self.id = id_orch
        self.name = name
        self.company = company
        self.pathlog_store = pathlog_store
        self.cdn_url = cdn_url


