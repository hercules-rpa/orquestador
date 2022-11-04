


"""
Clase para modelar los Ajustes Globales de la aplicación
"""
class GlobalSettings():
    def __init__(self, edma_host_sparql,edma_host_servicios,edma_port_sparql,sgi_user,sgi_password,sgi_ip,sgi_port,datbase_ip,database_port,ftp_user,ftp_password,ftp_port):
        self.edma_host_sparql = edma_host_sparql
        self.edma_host_servicios = edma_host_servicios
        self.edma_port_sparql = edma_port_sparql
        self.sgi_user = sgi_user
        self.sgi_password = sgi_password
        self.sgi_ip = sgi_ip
        self.sgi_port = sgi_port
        self.database_ip = datbase_ip
        self.database_port = database_port
        self.ftp_user = ftp_user
        self.ftp_password = ftp_password
        self.ftp_port = ftp_port
