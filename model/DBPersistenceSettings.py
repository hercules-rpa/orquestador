

"""
Clase para modelar los Ajustes de la base de datos de Persistencia de la aplicación
"""
class DBPersistenceSettings():
    def __init__(self,username,password,host,port,database ):
        self.user = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
