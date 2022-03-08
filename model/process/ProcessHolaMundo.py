from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.Log import Log
import Utils as Utils
import time
import asyncio

NAME            = "Hola Mundo"
DESCRIPTION     = "Proceso que envía una serie de mensajes a la salida estándar para utilizarlos como prueba"
REQUIREMENTS    = []
ID              = ProcessID.HOLA_MUNDO.value
class ProcessHolaMundo(ProcessCommand):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log,id_robot, priority, log_file_path, parameters)
        
        
    def execute(self):
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        print("Imprimimos hola mundo para debugging")
        self.update_log("Se ha imprimido hola mundo para debugging",True)
        self.log.completed = 33
        time.sleep(3)
        print("Imprimimos tras 3 segundos")
        self.update_log("Se ha imprimido tras 3 segundos de espera",True)
        time.sleep(5)
        print("Ahora imprimimos tras 5 segundos")
        self.log.completed += 33
        self.update_log("El proceso ahora imprime tras 5 segundos de espera",True)
        time.sleep(2)
        print("hemos hecho ultima pausa de 2 segundos e imprimimos")
        self.log.completed += 34
        self.update_log("El proceso finaliza tras 2 segundos e imprimir",True)
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = pstatus.FINISHED

    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass