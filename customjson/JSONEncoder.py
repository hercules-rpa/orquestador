import json
import copy

class JSONEncoder(json.JSONEncoder):


    # overload method default
    def default(self, obj):
        # Match all the types you want to handle in your converter
        from rpa_robot.robot                import Robot
        from model.Log                       import Log
        from model.process.ProcessCommand    import ProcessCommand, Pstatus, ProcessID
        from model.Event                     import Event, MSG_TYPE

        if isinstance(obj, Robot):
            robot_dict = copy.copy(obj.__dict__)
            robot_dict['connected'] = str(robot_dict['connected'])
            return robot_dict
        elif isinstance(obj, ProcessCommand):
            process_dict = copy.copy(obj.__dict__) #En caso de eliminar algún campo es necesario hacer un copy
            #del process_dict['log']
            return process_dict
        elif isinstance(obj, Pstatus):
            return (str(obj).split("."))[1]
        elif isinstance(obj, ProcessID):
            return (str(obj).split("."))[1]
        elif isinstance(obj, Log):
            log_dict = copy.copy(obj.__dict__)
            del log_dict['log_file']
            del log_dict['listener']
            return log_dict
        
        elif isinstance(obj, Event):
            return obj.__dict__
        elif isinstance(obj, MSG_TYPE):
            return str(obj.value)
            

        # Call the default method for other types
        return json.JSONEncoder.default(self, obj)
