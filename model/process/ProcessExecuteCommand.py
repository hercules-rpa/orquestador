from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import ProcessID
from model.process.ProcessCommand import Pstatus as pstatus
import time
import os

NAME            = "Restart Robot"
DESCRIPTION     = "Proceso que reinicia el robot en el que se ejecuta"
REQUIREMENTS    = []
ID              = ProcessID.EXECUTE_COMMAND.value

class ProcessExecuteCommand(ProcessCommand):
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters):
        ProcessCommand.__init__(self, ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log, id_robot, priority, log_file_path, parameters)

    def execute(self):
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        print("inicio")

        if not self.parameters:
            self.update_log("No se han establecido parámetros", True)
            self.log.state = "ERROR"
            self.log.end_log(time.time())
            self.state = pstatus.FINISHED
            return 

        command = self.parameters['command_to_execute']
        print("Comando")
        print(command)

        try:
            os.system(command)
        except OSError as err:
            self.update_log("Error al ejecutar el comando")

        self.log.completed = 100
        self.log.end_log(time.time())
        self.state = pstatus.FINISHED



    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass