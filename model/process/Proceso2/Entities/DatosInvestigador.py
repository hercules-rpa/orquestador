class DatosInvestigador():
    def __init__(self, person: str = None, nombreCompleto: str = None, email: str = None,
                 nombreDepartamento:str = None, nombreUniversidad:str=None):
        self.person = person
        self.nombreCompleto = nombreCompleto
        self.email = email
        self.nombreDepartamento = nombreDepartamento
        self.nombreUniversidad = nombreUniversidad

    def set_properties(self, df):
        aux = df.iloc[0]
        if 'person.value' in df:
                self.person = aux["person.value"]
        if 'nombreCompleto.value' in df:
                self.nombreCompleto = aux["nombreCompleto.value"]
        if 'email.value' in df:
                self.email = aux["email.value"]
        if 'nombreDepartamento.value' in df:
                self.nombreDepartamento= aux["nombreDepartamento.value"]
        if 'nombreUniversidad.value' in df:
                self.nombreUniversidad = aux["nombreUniversidad.value"]

        if self.nombreCompleto:
                print('investigador: ' + self.nombreCompleto )
        if self.email:
                print(' email: ' + self.email)

