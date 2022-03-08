import json
import rpa_orchestrator.orchestrator          as Orch
from customjson.JSONEncoder             import JSONEncoder
from rpa_orchestrator.lib.persistence.dbcon import ControllerDBPersistence


orch = Orch.Orchestrator()
db = ControllerDBPersistence()

def get_log(id_log) -> json:
    if(id_log):
        try:
            log = next(x for x in orch.log_list if x.id == id_log)
            return JSONEncoder().encode(log)
        except:
            log = db.read_log_byid(id_log)
            if log:
                log = JSONEncoder().encode(log)
            return log
    else:
        log_json = []
        logs = db.read_all_logs()
        for l in logs:
            if l.start_time:
                l_dict = l.__dict__ #probar a borrar todo los del.
                del l_dict['data']
                del l_dict['listener']
                del l_dict['data_listener']
                del l_dict['log_file']
                log_json.append(l_dict)
        return json.dumps(log_json)

def get_all_logs_by_idrobot(id_robot) -> json:
    logs = db.read_logs_byidrobot(id_robot)
    return JSONEncoder().encode(logs)

def get_all_logs_by_idschedule(id_schedule) -> json:
    logs = db.read_logs_byidschedule(int(id_schedule))
    log_json = []
    for l in logs:
        if l.start_time:
            l_dict = l.__dict__
            del l_dict['data']
            del l_dict['listener']
            del l_dict['data_listener']
            del l_dict['log_file']
            log_json.append(l_dict)
    return json.dumps(log_json)
