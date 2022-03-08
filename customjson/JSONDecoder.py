import json


class JSONDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_class, *args, **kwargs)

    def dict_to_class(self, obj):
        from rpa_robot.robot                import Robot
        from model.Log                       import Log

        if ("id" in obj.keys() and "online" in obj.keys() and "features" in obj.keys()):
            robot =  Robot(id = obj['id'], name = obj['name'], address = obj['address'], registrations = obj['registrations'], online = obj['online'], connected = float(obj['connected']), features = obj['features'], state = obj['state'], process_running = obj['process_running'], process_list = obj['process_list'])
            robot.process_pause = obj['process_pause']
            robot.ip_address    = obj['ip_address']
            robot.mac           = obj['mac']
            robot.os            = obj['os']
            robot.python_version = obj['python_version']
            robot.performance   = obj['performance']
            return robot

        elif ("name" in obj.keys() and "requirements" in obj.keys() and "description" in obj.keys()):
            #Process
            return obj
            
        elif ("id" in obj.keys() and "id_process" in obj.keys() and "id_robot" in obj.keys() and "log_file_path" in obj.keys()):
            log = Log(obj['id'], obj['id_schedule'], obj['id_process'], obj['id_robot'], obj['log_file_path'], obj['process_name'])
            log.data        = obj['data']
            log.start_time  = obj['start_time']
            log.end_time    = obj['end_time']
            log.state       = obj['state']
            log.finished    = obj['finished']
            log.completed   = obj['completed']
            return log


        return obj

