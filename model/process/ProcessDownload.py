from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
import time
import requests
import re
import os

NAME            = "Download Files"
DESCRIPTION     = "Proceso que descarga fichero desde una lista de URLs. La estructura debe ser '{'URL:[]}"
REQUIREMENTS    = []
ID              = ProcessID.DOWNLOAD_FILES.value

DIRECTORY_DOWNLOAD = "rpa_robot/files/"

class ProcessDownload(ProcessCommand):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log,id_robot, priority, log_file_path, parameters)

    def execute(self):
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        list_url = self.parameters['URL']
        print("Empezamos la descarga de ficheros. Número de ficheros a descargar: "+str(len(list_url)))
        self.log.completed = 0
        num_files = 1
        for url in list_url:
            try:
                file = requests.get(url, allow_redirects=True)
                if os.path.exists(DIRECTORY_DOWNLOAD+self.get_filename(file.headers.get('content-disposition'))):
                    os.remove(DIRECTORY_DOWNLOAD+self.get_filename(file.headers.get('content-disposition')))
                open(DIRECTORY_DOWNLOAD+self.get_filename(file.headers.get('content-disposition')), 'wb').write(file.content)
                self.log.completed += 100/len(list_url)
                print("Ficheros: "+str(num_files)+"/"+str(len(list_url)))
                self.update_log("Ficheros: "+str(num_files)+"/"+str(len(list_url))+". "+url, True)
                num_files += 1
            except:
                self.log.state = "ERROR"
                self.update_log("Error descargando el fichero "+url, True)
                print("Error en la descarga de fichero, el fichero ya existe?")

        print("La descarga de fichero ha terminado")
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = pstatus.FINISHED

    def get_filename(self, cd):
        if not cd:
            return None
        fname = re.findall('filename=(.+)', cd)
        if len(fname) == 0:
            return None
        return fname[0]

    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass