class Congreso():
    """
    Trabajos presentados en congresos nacionales o internacionales
    """
    def __init__(self, titulo:str='', fecha:str='', autores:str='', num_autores:int=0):
        self.titulo = titulo
        self.fecha = fecha
        self.autores = autores
        self.num_autores = num_autores