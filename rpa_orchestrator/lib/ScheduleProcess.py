import json
import rpa_orchestrator.lib.Schedule     as schedule
import model.messages   as messages
from datetime import datetime

class ScheduleProcess:
    def __init__(self, id = None, id_robot = None, schedule_json = None, function = None):
        self.id             = id
        self.id_robot       = id_robot
        self.schedule_json  = schedule_json
        self.function       = function
        self.next_run       = None
        self.id_robot_temp  = None #id_robot temporal para cuando se ejecuta en modo dios
        self.created        = datetime.now()
        
    def get_route(self):
        if self.id_robot is None:
            return None
        return messages.ROUTE_ROBOT+self.id_robot

    def get_next_run(self):
        try:
            schedule_job = schedule.get_jobs((self.id))[0]
            self.next_run = schedule_job.next_run
            return self.next_run
        except:
            self.next_run = None
            return self.next_run


    def get_forever(self):
        data = json.loads(self.schedule_json)
        if not data['time_schedule']:
            return False
        return data['time_schedule']['forever']

    def get_processid(self):
        data = json.loads(self.schedule_json)
        return data['process']['id_process']

    def get_priority(self):
        data = json.loads(self.schedule_json)
        return data['process']['priority']
        
    def is_active(self):
        try: 
            schedule_job = schedule.get_jobs((self.id))[0]
            if self.get_forever():
                return True
            return datetime.now() <= schedule_job.next_run
        except:
            return False
    
    def set_forever(self, bool):
        data = json.loads(self.schedule_json)
        if data['time_schedule']:
            data['time_schedule']['forever'] = bool
            data = json.dumps(data)
            self.schedule_json = data

    def time_to_schedule(self):
        data = json.loads(self.schedule_json)
        try:
            time_dict = data['time_schedule']
            if time_dict is not None:
                if (time_dict['every'][0] is not None and time_dict['at'] is not None):
                    (getattr(schedule.every(int(time_dict['every'][0])), time_dict['every'][1])).at(time_dict['at']).do( self.function, id_schedule = self.id, process_json = json.dumps(data['process']), forever = time_dict['forever']).tag(time_dict['tag'], self.id)

                elif(time_dict['every'][0] is None and time_dict['at'] is not None):
                    (getattr(schedule.every(), time_dict['every'][1])).at(time_dict['at']).do( self.function, id_schedule = self.id, process_json = json.dumps(data['process']), forever = time_dict['forever']).tag(time_dict['tag'], self.id)

                elif(time_dict['every'][0] is not None and time_dict['at'] is None):
                    (getattr(schedule.every(int(time_dict['every'][0])), time_dict['every'][1])).do( self.function, id_schedule = self.id, process_json = json.dumps(data['process']), forever = time_dict['forever']).tag(time_dict['tag'], self.id)

                elif(time_dict['every'][0] is None and time_dict['at'] is None):
                    (getattr(schedule.every(), time_dict['every'][1])).do( self.function, id_schedule = self.id, process_json = json.dumps(data['process']), forever = time_dict['forever']).tag(time_dict['tag'], self.id)
            else:
                #Aunque no lo queramos planificar le metemos una planificacion instantaneo para que siga el mismo modelo de ejecucion
                schedule.every(5).seconds.do( self.function, id_schedule = self.id, process_json = json.dumps(data['process']), forever = False).tag("Instant", self.id)
            
            
            return self.id

        except:
            print("ERROR FORMING THE PROCESS. MAYBE JSON WRONG? ")
            return None
