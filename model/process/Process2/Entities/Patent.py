class Patent():
    """
    La clase Patente contiene la información almacenada en Hércules-ED sobre una patente.
    """
    def __init__(self, title:str = '', date:str='', authors:str='') -> None:
        self.title = title
        self.date= date
        self.authors = authors