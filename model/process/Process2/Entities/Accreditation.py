from enum import Flag

class AccreditationType(Flag):
    """
    TipoAcreditacion es un flag que identifica el tipo de acreditación al que se desea optar
    en el proceso de solicitud de acreditaciones (P4 - RPA)
    """
    NODEFINIDO = 0
    TITULARIDAD = 1
    CATEDRA = 2
    #PUP = 3
    #PCD = 4
    #PAD = 5

class AccreditationCategory(Flag):
    """
    CategoriaAcreditacion es la categoría a la que pertenece la acreditación seleccionada.
    """
    NODEFINIDO =0
    INVESTIGACION=1
    DOCENCIA=2


class Accreditation():
    """
    Clase que define las propiedades de las acreditaciones
    tipo = catedra, titularidad, ...
    nombre = cadena que se utilizará para el desarrollo del informe
    """
    def __init__(self, id, parameters, category:AccreditationCategory=AccreditationCategory.NODEFINIDO):
        self.type:AccreditationType = AccreditationType(int(id))
        self.name = parameters['name']
        self.category:AccreditationCategory = category
