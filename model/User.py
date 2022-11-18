class User():
    """
    Clase para modelar los Usuarios.
    """
    def __init__(self,username, password, token):
        self.username = username
        self.password = password
        self.token = token