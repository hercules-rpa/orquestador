import Utils as Utils
import copy
import json
import os
import errno
import time
import asyncio

class Log:
    def __init__(self,id = None, id_schedule = None, id_process = None, id_robot = None, log_file_path = None, process_name = None):
        self.id = id
        self.id_schedule = id_schedule
        self.id_process = id_process
        self.id_robot = id_robot
        self.log_file_path = log_file_path
        
        self.process_name = process_name

        self.data = ""
        self.start_time = None
        self.listener = None
        self.data_listener = None
        self.end_time = None
        self.log_file = None
        self.completed = 0
        self.state = None
        self.finished = False
    
    def update_log(self,new_data):
        if self.log_file is not None:
            self.log_file.write(new_data)
            self.log_file.flush()
        self.data = self.data + new_data
        if self.listener is not None:
            self.listener.notify_log(self)
        if self.data_listener is not None:
            self.data_listener.notify_log_data(self,new_data)

    def write_log(self, path):
        try:
            file = open(path+self.log_file_path, "w")
            file.write(self.data)
            file.flush()
        except:
            print("error al escribir en el log /var/log/orchestrator")

    def add_log_listener(self,listener):
        self.listener = listener

    def add_data_listener(self,data_listener):
        self.data_listener = data_listener

    def get_data(self):
        return self.data

    def start_log(self,start_timestamp):
        if (self.log_file_path is not None and self.log_file_path in '/' and not os.path.exists(os.path.dirname(self.log_file_path))):
            try:
                os.makedirs(os.path.dirname(self.log_file_path))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        if (self.log_file is None and self.log_file_path is not None):
            print(self.log_file_path)
            self.log_file = open(self.log_file_path, "a")
        
        self.data = ""
        self.start_time = start_timestamp
        
        self.update_log("["+Utils.time_to_str(time.time())+"]"+" Process"+str(self.id_process)+"@Robot"+self.id_robot+" "+"Empieza el proceso "+self.process_name+"\n")

    def end_log(self,end_timestamp):
        self.finished = True
        self.end_time = end_timestamp
        self.update_log("["+Utils.time_to_str(time.time())+"]"+" Process"+str(self.id_process)+"@Robot"+self.id_robot+" "+"Proceso "+self.process_name+" Finalizado\n")

        if(self.log_file is not None):
            self.log_file.close()

