# Clase para encapsular la ejecucion de los procesos
# process -> Proceso a ejecutar
# listener -> Para notificar en caso de error
from model.process.ProcessCommand import ProcessCommand
from model.interfaces.ListenerLog import ListenerLog
import time
import traceback


class ExecProcess():
    def __init__(self, process: ProcessCommand, listener: ListenerLog):
        self.process = process
        self.listener = listener

    def exec(self):
        try:
            print("Se va a ejecutar ", self.process.name)
            self.process.execute()
        except Exception as e:
            self.process.log.state = "ERROR"
            self.process.log.finished = True
            self.process.log.completed = 100
            self.process.update_log("Ocurrió un error inesperado. "+str(traceback.format_exc()), True)
            self.process.update_log("Ocurrió un error inesperado. "+str(e), True)
            end_time = time.time()
            self.process.log.end_log(end_time)
            #Notificamos a nosotros mismo para que mande el mensaje al orquestador
            self.listener.notify_log(self.process.log)
            print("La ejecucion ha terminado con un error inesperado")
            print(traceback.format_exc())
            print(str(e))
