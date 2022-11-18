


"""
Clase para modelar los Ajustes Globales de la aplicación
"""
class GlobalSettings():
    def __init__(self, edma_host_sparql,edma_host_servicios,edma_port_sparql,sgi_user,sgi_password,sgi_ip,sgi_port,url_upload_cdn,url_release):
        self.edma_host_sparql = edma_host_sparql
        self.edma_host_servicios = edma_host_servicios
        self.edma_port_sparql = edma_port_sparql
        self.sgi_user = sgi_user
        self.sgi_password = sgi_password
        self.sgi_ip = sgi_ip
        self.sgi_port = sgi_port
        self.url_release = url_release
        self.url_upload_cdn = url_upload_cdn
