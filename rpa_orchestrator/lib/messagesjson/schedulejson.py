import json
import rpa_orchestrator.orchestrator          as Orch
from rpa_orchestrator.lib.persistence.dbcon import ControllerDBPersistence

orch = Orch.Orchestrator()
db = ControllerDBPersistence()

def __get_schedule_json(schedule) -> json:
    schedule_json = json.loads(schedule.schedule_json)
    schedule_json = schedule_json['time_schedule']
    schedule_dict = {
                        'id':schedule.id,
                        'id_robot':schedule.id_robot,
                        'created':schedule.created.timestamp(),
                        'process_name':orch.get_process_name_by_id(schedule.get_processid()),
                        'id_process':schedule.get_processid(),
                        'priority':schedule.get_priority(),
                        'active':schedule.is_active(),
                        'time_schedule':schedule_json,
                        'logs':json.loads(orch.get_all_logs_by_idschedule(schedule.id))
                    }
    if schedule.get_next_run():
        schedule_dict['next_run'] = schedule.get_next_run().timestamp()
    else:
        schedule_dict['next_run'] = None
    return json.dumps(schedule_dict)


def get_schedule(id_schedule) -> json:
    try:
        process = next(x for x in orch.schedule_list if x.id == int(id_schedule))
        return __get_schedule_json(process)
    except:
        process = db.read_schedule_byid(id_schedule)
        if process:
            process = __get_schedule_json(process)
            return process
        return process

def get_all_schedules(filters) -> json:
    sch = db.read_all_schedules(filters)
    sch_json = []
    for s in sch:
        s_json = json.loads(__get_schedule_json(s))
        del s_json['logs']
        sch_json.append(s_json)
    return json.dumps(sch_json)