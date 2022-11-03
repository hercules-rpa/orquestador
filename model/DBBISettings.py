


"""
Clase para modelar los Ajustes de la base de datos de Business Intelligence de la aplicación
"""
class DBBISettings():
    def __init__(self,username,password,host,port,keyspace):
        self.user = username
        self.password = password
        self.host = host
        self.port = port
        self.keyspace = keyspace