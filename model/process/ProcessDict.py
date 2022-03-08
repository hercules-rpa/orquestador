from model.process.ProcessCommand import ProcessClassName, ProcessID
from ast import literal_eval
import json
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ProcessDict(metaclass=Singleton):

    DIRECTORY_PROCESS       = "model/process/"
    DIRECTORY_PROCESS_FORM  = "model/process/forms/"

    def __getVariableFromFile(self, process, variable):
        with open(self.DIRECTORY_PROCESS+process+".py") as f:
            for line in f:
                l = line.replace(" ","")
                if variable in l:
                    return literal_eval(line.split("=")[1].strip())
        return None

    def existsProcess(self, id_process) -> bool:
        try:
            ProcessClassName[ProcessID(id_process).name].value
            return True
        except:
            return False


    def getProcessClassNameById(self, id):
        if(self.existsProcess(id)):
            return ProcessClassName[ProcessID(id).name].value
        return None

    def getProcessNameById(self, id):
        if(self.existsProcess(id)):
            return self.__getVariableFromFile(self.getProcessClassNameById(id),"NAME=")
        return None

    def getRequiredProcessById(self, id):
        if(self.existsProcess(id)):
            return self.__getVariableFromFile(self.getProcessClassNameById(id),"REQUIREMENTS=")
        return None

    def getDescriptionProcessById(self, id):
        if(self.existsProcess(id)):
            return self.__getVariableFromFile(self.getProcessClassNameById(id),"DESCRIPTION=")
        return None
        
    def getAllProcess(self):
        return [e.value for e in ProcessID]

    def getProcessForm(self, id):
        if(self.existsProcess(id)):
            try:
                
                with open(self.DIRECTORY_PROCESS_FORM+self.getProcessClassNameById(id)+".json", "r") as json_file:
                    data = json.load(json_file)
                    return data
            except:
                print("No existe el formulario del proceso solicitado "+str(id)+" se envia vacio")
                return []
        return None

'''
import os
import sys
import json
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../../config/ProcessInfo.json')

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ProcessDict(metaclass=Singleton):
    def __init__(self):
        try:
            with open(filename) as json_file:
                self.processDict = json.load(json_file)
        except:
            print("No such file or directory")
            self.processDict = None

    def getProcessClassNameById(self, id):
        try:
            process_class = next(item.get('process_class_name') for item in self.processDict if item.get('process_id') == id)
        except:
            return None
        return process_class

    def getProcessNameById(self, id):
        try:
            process_class = next(item.get('process_name') for item in self.processDict if item.get('process_id') == id)
        except:
            return None
        return process_class

    def getProcessById(self, id):
        try:
            process_class = next(item for item in self.processDict if item.get('process_id') == id)
        except:
            return None
        return process_class

    def getProcessIdByName(self, name):
        try:
            process_class = next(item.get('process_id') for item in self.processDict if item.get('process_class_name') == name)
        except:
            return None
        return process_class

    def getRequiredProcessById(self, id):
        try:
            process_required = next(item.get('required') for item in self.processDict if item.get('process_id') == id)
        except:
            return None
        return process_required

'''