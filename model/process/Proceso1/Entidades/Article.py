from model.process.Proceso1.Entidades.Author import Author

class Article():
    host_gnoss = 'http://edma.gnoss.com/comunidad/hercules/recurso/'
    def __init__(self, doc: str = None, magazine: str = None, date: str = None, 
        areas: str = None, url: str = None, authors: list = [], id:str=''):
        self.doc = doc
        self.magazine = magazine
        self.date = date
        self.areas = areas
        self.url = url
        self.authors = authors
        self.id = id

    def set_properties(self, properties):        
        """
        Método para añadir las propiedades del articulo
        """
        if not properties.empty:            
            if 's.value' in properties:
                url = properties['s.value']
                if url:
                    self.id = url.replace('http://gnoss/', '')
                    if self.id:
                        self.url = self.host_gnoss + 'art/' + self.id
            if 'nombreArea.value' in properties:
                self.areas = properties['nombreArea.value']
                if self.areas:
                    self.areas = self.areas.replace('|', ', ')

            if 'nombreRevista.value' in properties and properties['nombreRevista.value']:
                self.magazine = str(properties['nombreRevista.value'])
            if 'fecha.value' in properties:
                v = properties['fecha.value']
                self.date = v[6:8] + "/" + v[4:6] + "/" + v[0:4]          
        
            self.authors = []
            self.add_author(properties)

        return self

    def add_author(self, properties):
        """
        Método para añadir un autor a las propiedades
        """
        name = ''
        orcid = ''
        if 'autor.value' in properties:
            name = properties['autor.value']
        if 'ORCID.value' in properties and properties['ORCID.value']:
            orcid = properties['ORCID.value']
        self.authors.append(Author(name=name, orcid=str(orcid)))

    def set_autors(self, authors:list):
        """
        Método para añadir una lista de autores
        """
        self.authors = authors
    
