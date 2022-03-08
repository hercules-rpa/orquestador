

class File():
    def __init__(self, id = None, name = None, absolute_path = None, directory = None, time = None):
        self.id = id
        self.name = name
        self.absolute_path = absolute_path
        self.directory = directory
        self.time = time

    def get_name(self):
        return self.name.split(".")[0]

    def get_format(self):
        return self.name.split(".")[-1]