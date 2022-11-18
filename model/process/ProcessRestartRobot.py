import json
import sys
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
import os
import time
import wget
import zipfile
import tempfile
import shutil
import cp
from rpa_robot.ControllerSettings import ControllerSettings

NAME            = "Restart Robot"
DESCRIPTION     = "Proceso que reinicia el robot en el que se ejecuta"
REQUIREMENTS    = []
ID              = ProcessID.RESTART_ROBOT.value


class ProcessRestartRobot(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api):
        ProcessCommand.__init__(self, ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log, id_robot, priority, log_file_path, parameters, ip_api, port_api)

    def execute(self):
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        if self.parameters['update']:
            self.update_log("Se procede a actualizar el robot",True)
            cs = ControllerSettings()
            settings_response = cs.get_globals_settings(self.ip_api, self.port_api)
            if settings_response:
                settings = json.loads(settings_response)
                if self.update_code(settings['url_release']):
                    self.update_log("Update Process Complete", True)
                else: 
                    self.update_log("Update Process Failed", True)

        self.update_log("Se procede al reinicio del robot y se reinicia",True)
        end_time = time.time()
        self.state = pstatus.FINISHED
        self.log.end_log(end_time)
        os.execv(sys.executable, ['python3'] + sys.argv)

    def update_code(self, url):
        name_file = wget.download(url, out=tempfile.gettempdir())
        if name_file:
            try:
                with zipfile.ZipFile(os.path.join(tempfile.gettempdir(), name_file), 'r') as zip_ref:
                    zip_ref.extractall(tempfile.gettempdir())
            except:
                os.remove(os.path.join(tempfile.gettempdir(), name_file))
                self.update_log("Problemas al descomprimir el archivo en el directorio temporal. Borramos archivos temporales", True)
                return False
            self.update_log("Se ha extraído en: " + os.path.join(tempfile.gettempdir(), name_file), True)
            try:
                currentdir = os.path.dirname(os.path.realpath(__file__))
                cp.cp(os.path.join(os.path.join(tempfile.gettempdir(), name_file.split(".zip")[0]), "model"), os.path.join(os.path.dirname(os.path.dirname(currentdir)), "model"), force=True)
                self.update_log("Copiados los ficheros desde el directorio " + os.path.join(os.path.join(tempfile.gettempdir(), name_file.split(".zip")[0]), "model") + " a " + os.path.join(os.path.dirname(os.path.dirname(currentdir)), "model"), True)
            except:
                os.remove(os.path.join(tempfile.gettempdir(), name_file))
                shutil.rmtree(os.path.join(tempfile.gettempdir(), name_file.split(".zip")[0]))
                self.update_log("Problemas al copiar los archivos descargados en el directorio del proyecto. Borramos archivos temporales",True)
                return False
            os.remove(os.path.join(tempfile.gettempdir(), name_file))
            shutil.rmtree(os.path.join(tempfile.gettempdir(), name_file.split(".zip")[0]))
            self.update_log("Se ha realizado la actualización correctamente. Borramos archivos temporales", True)
            return True
        else:
            self.update_log("Problemas al descargar el archivo en el directorio temporal.",True)
            return False

    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass