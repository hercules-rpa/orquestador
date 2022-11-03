class RO:
    """
    La clase RO viene por Research Object y representa los objetos relacionados con los
    investigadores y contiene sus propiedades.
    """
    def __init__(self, title:str='', doi:str='', publication_type:str = '', 
        publication_date:str = '', wos_cites:str ='',position:str = '', num_magazines:str='',
        magazine:str = '',impact:str='',quartile:str = '', authors:str = '',
        authors_number:int = 0, author_position:int=0):
        
        self.title:str = title
        self.doi:str = doi
        self.publication_type = publication_type
        self.publication_date = publication_date
        self.wos_cites = wos_cites
        self.position:str = position
        self.magazine = magazine
        self.impact = impact
        self.quartile = quartile
        self.num_magazines:str = num_magazines        
        self.num_pages = ''
        self.issn = ''
        self.editorial = ''
        self.volume = ''
        self.number = ''
        self.start_page = ''
        self.end_page = ''
        self.scopus_cites = ''
        self.ss_cites = ''
        self.authors = authors
        if self.authors:
            print('autores: ' + self.authors)
        self.authors_number = authors_number
        self.author_position:int = author_position
        
    def get_year(self) -> str:
        """
        Método que calcula el año en el que se publicó el RO
        """
        return self.publication_date.split("-")[2]

    def get_pages_number(self) -> int:
        """
        Método que calcula el número de páginas de un RO
        """
        if(self.end_page != '' and self.start_page != ''):
            return int(self.end_page) - int(self.start_page)
        return 0

    def get_quartile(self) -> int:
        """
        Método que obtiene el cuartil al que pertenece un RO
        :return int devuelve 0 si la propiedad cuartil no tiene valor
        """
        if self.quartile:
            return int(self.quartile)
        return 0

    def get_decile(self) -> int:
        """
        Método que obtiene el decil al que pertenece el RO
        :return int devuelve 0 si no puede realizar el cálculo.
        """
        decile: int = 0
        if self.position and self.num_magazines:
            result = (int(self.position) * 10) / int(self.num_magazines)
            if result <= 1:
                decile = 1
            elif result > 1:
                decile = round(result)
        return decile

    def get_tertile(self) -> int:
        """
        Método que obtiene el tercil al que pertenece el RO
        :return int devuelve 0 si no puede realizar el cálculo.
        """
        tertile: int = 0
        if self.position and self.num_magazines:
            result = (int(self.position) * 3) / int(self.num_magazines)
            if result <= 1:
                tertile = 1
            elif result > 1:
                tertile = round(result)
        return tertile