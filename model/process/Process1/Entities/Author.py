class Author():
    def __init__(self, name:str=None, orcid:str=None):
        self.name =name
        if orcid and orcid != 'nan':
            self.orcid = orcid
        else:
            self.orcid = None
