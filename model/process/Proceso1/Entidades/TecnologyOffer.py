from model.process.Proceso1.Entidades.Author import Author

class TecnologyOffer():
    def __init__(self, title:str='', description:str='', date:str='', url:str='', researchers:list=[], id:str=''):
        self.title = title
        self.description = description
        self.date = date
        self.researchers = researchers
        self.url = url
        self.id = id

    def set_properties(self, properties):        
        """
        Método para añadir las propiedades del articulo
        """
        if not properties.empty:            
            if 'idOferta.value' in properties:
                url = properties['idOferta.value']
                if url:
                    self.id = url.replace('http://gnoss/', '')
                    if self.id:
                        self.url = 'http://edma.gnoss.com/comunidad/hercules/recurso/otc/' + \
                            self.id
           
            if 'titulo.value' in properties:
                self.title = properties['titulo.value']

            if 'description.value' in properties and properties['description.value']:
                self.description = properties['description.value']

            if 'fecha.value' in properties:
                v = properties['fecha.value']
                self.date = v[6:8] + "/" + v[4:6] + "/" + v[0:4]          
        
            self.researchers = []
            self.add_researcher(properties)

        return self

    def add_researcher(self, properties):
        """
        Método para añadir un investigador a las propiedades
        """
        name = ''
        if 'nombre.value' in properties:
            name = properties['nombre.value']
        self.researchers.append(Author(name=name))

    def set_autors(self, researchers:list):
        """
        Método para añadir una lista de investigadores
        """
        self.researchers = researchers
    