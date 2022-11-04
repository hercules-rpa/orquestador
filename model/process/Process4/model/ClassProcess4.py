
class Convocatoria():
    def __init__(self, id = None, titulo = None, areaTematica = None, creation_date = None):
        self.id             = id
        self.titulo         = titulo
        self.areaTematica   = areaTematica
        self.creation_date  = creation_date

class Investigador():
    def __init__(self,id = None, nombre = None, email = None, perfil = False):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.is_config_perfil = perfil
        
class AreaTematica():
    def __init__(self, id = None, areaPadre = None, areaHijo = None, nombre = None, descripcion = None):
        self.id = id
        self.areaPadre = areaPadre #lista
        self.areaHijo  = areaHijo  #lista
        self.nombre = nombre
        self.descripcion = descripcion

class CalificacionConvocatoria():
    def __init__(self, id = None, idInvestigador = None, idArea = None, idSubArea = None, puntuacion = None):
        self.id = id
        self.investigador = None
        self.idArea = None
        self.idSubArea = None
        self.puntuacion = puntuacion