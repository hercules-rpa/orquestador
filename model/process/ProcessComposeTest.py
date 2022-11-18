from model.interfaces.ListenerLogData import ListenerLogData
from model.process.ProcessHolaMundo import ProcessHolaMundo
from model.process.ProcessSendMail import ProcessSendMail
from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
import json
import time

NAME            = "Compose Proc"
DESCRIPTION     = "Proceso que se va a componer de otros procesos y va a ejecutar a los hijos"
REQUIREMENTS    = []
ID              = ProcessID.COMPOSE_TEST.value

class ProcessComposeTest(ProcessCommand,ListenerLogData):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log,id_robot, priority, log_file_path, parameters)
        

    def execute(self):
        self.state = pstatus.RUNNING
        start = time.time()
        self.log.start_log(start)

        print("Soy el proceso padre e imprimo hola para debugging")
        self.update_log("El proceso padre ha imprimido hola para debugging",True)
        time.sleep(3)
        print("hemos hecho pausa de 3 segundos y procederemos a ejecutar al hijo")
        self.update_log("El proceso padre ha hecho pausa de 3 segundos y procede a ejecutar al hijo",True)
        
        parameters = []
        
        p = ProcessHolaMundo(self.log.id_schedule, self.log.id,self.id_robot, "1", None, parameters)
        p.add_data_listener(self)
        p.execute()
        p.execute()
        p.execute()

        self.update_log("Procedemos a ejecutar proceso de envío de correo",True)

        with open('mailtest.json') as f:
            params_mail = json.load(f)
    
        psm = ProcessSendMail(self.log.id_schedule, self.log.id, self.id_robot, "1", None, params_mail)
        psm.add_data_listener(self)
        psm.execute()

        time.sleep(3)
        print("acabamos de ejecutar al hijo y esperamos 3 segundos para finalizar")
        self.update_log("Termina la ejecución del hijo y hemos esperado 3 segundos, Proceso concluido satisfactoriamente",True)

        end_time = time.time()
        self.log.end_log(end_time)
        self.state = pstatus.FINISHED


    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass