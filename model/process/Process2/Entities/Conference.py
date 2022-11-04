class Conference():
    """
    Trabajos presentados en congresos nacionales o internacionales
    """
    def __init__(self, title:str='', date:str='', authors:str='', num_authors:int=0):
        self.title = title
        self.date = date
        self.authors = authors
        self.num_authors = num_authors