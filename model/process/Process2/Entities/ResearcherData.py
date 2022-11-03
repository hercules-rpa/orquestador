class ResearcherData():
    """
    La clase ResearcherData almacena las propiedades principales del investigador
    obtenidas utilizando Hércules-ED.
    """

    def __init__(self, name: str = None, email: str = None,
                    departament: str = None, university: str = None):
        self.name = name
        self.email = email
        self.departament = departament
        self.university = university

    def set_properties(self, df):
        """
        Método que hidrata las propiedades de la clase
        param df Dataframe con las propiedades a hidratar
        """   
        aux = df.iloc[0]
        if 'nombreCompleto.value' in df:
            self.name = aux["nombreCompleto.value"]
        if 'email.value' in df:
            self.email = aux["email.value"]
        if 'nombreDepartamento.value' in df:
            self.departament = aux["nombreDepartamento.value"]
        if 'nombreUniversidad.value' in df:
            self.university = aux["nombreUniversidad.value"]

        if self.name:
            print('investigador: ' + self.name)
        if self.email:
            print(' email: ' + self.email)
