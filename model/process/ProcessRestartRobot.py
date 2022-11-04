import json
import sys
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
import os
import time
import model.ftpclient as ftpclient
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
        if self.parameters['update'] == True:
            cs = ControllerSettings()
            settings_response = cs.get_globals_settings(self.ip_api, self.port_api)
            if settings_response:
                settings = json.loads(settings_response)
                if not ftpclient.update(self, self.ip_api, settings['ftp_port'], settings['ftp_user'], settings['ftp_password']):
                    self.update_log("Update Process Complete", True)
                    print("Update Process Complete")
                else: 
                    self.update_log("Update Process Failed", True)
                    print("Update Process Failed")

        self.update_log("Se obtiene la lina de comando con la que se ejecutó el robot y se reinicia",True)
        end_time = time.time()
        self.state = pstatus.FINISHED
        self.log.end_log(end_time)
        os.execv(sys.executable, ['python3'] + sys.argv)

    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass