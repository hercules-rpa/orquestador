import time
import os
from model.process.ProcessCommand import ProcessCommand, ProcessID, Pstatus
from module_cognitive_treelogic.ExtractXML import ExtractXml

NAME            = "Extract XML"
DESCRIPTION     = "Proceso para extraer información de un fichero xml."
REQUIREMENTS    = []
ID              = ProcessID.EXTRACT_XML.value

class ProcessExtractXml(ProcessCommand):
     
    def __init__(self, id_schedule, id_log, id_robot, priority, log_file_path, parameters=None):
        ProcessCommand.__init__(self, ID, NAME, REQUIREMENTS, DESCRIPTION,
                                id_schedule, id_log, id_robot, priority, log_file_path, parameters)                                        

    def execute(self):
        self.state = Pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        self.notify_update("El proceso de extracción de información de fichero xml ha comenzado.")
        self.log.completed = 0
        url:str = None
        
        try:
            url = self.parameters['url']           
        except:
            self.notify_update('No se ha obtenido el parámetro url.')
                
        filename = self.parameters['filename']
        psm = ExtractXml(self.parameters)
        if url:            
            status_code = psm.get_document(url, filename)
            self.log.completed = 33

            if status_code != 200:
                self.notify_update('No ha sido posible descargar el fichero xml.')
        else:
            self.log.completed = 33

        if os.path.getsize(filename) < 10:
            self.notify_update('ERROR: fichero xml erróneo o incompleto.')
        else:
            self.log.completed = 66
            if 'nodos' in self.parameters:
                self.result =  psm.get_nodes(self.parameters['nodos'], filename)

        #Solo eliminamos el fichero si no se ha pasado como parámetro la url, 
        #ya que si se pasa la url el fichero lo hemos descargado nosotros.
        delete_file = False
        if url:
            delete_file = True

        if delete_file and os.path.exists(filename):
            os.remove(filename)
            
        self.log.completed = 100
        self.notify_update("El proceso de extracción de información del fichero xml ha finalizado.")        
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = Pstatus.FINISHED


    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass