import json
import rpa_orchestrator.lib.statistics        as stbi
import rpa_orchestrator.orchestrator      as  Orch
from rpa_orchestrator.lib.persistence.dbcon import ControllerDBPersistence
from datetime import datetime

orch = Orch.Orchestrator()
db = ControllerDBPersistence()


orch = Orch.Orchestrator()

def get_all_robots() -> json:
    json_robot = []
    for (key, value) in orch.robot_list.items():
        robot = value[0]
        time  = value[1]
        process_dict = {'process_running':None}
        if robot.process_running:
            process_dict = {    'process_running':{
                                'id':robot.process_running['id'],
                                'name':robot.process_running['name'],
                                'id_log': robot.process_running['log'].id
                            }}
        robot_dict = {'robot_name':robot.name,
                        'robot_id':robot.id,
                        'robot_address':robot.ip_address,
                        'online': robot.online,
                        'time_online': 0 if not robot.online else datetime.now().timestamp() - robot.connected,
                        'last_seen':round(time.timestamp())
                    }
        json_robot.append(dict(robot_dict, **process_dict))
    return json.dumps(json_robot)

def get_robot(id_robot) -> json:
    if not (id_robot in orch.robot_list):
        return None
    robot       = orch.robot_list[id_robot][0]
    time        = orch.robot_list[id_robot][1]
    logs        = db.read_logs_byidrobot_last(id_robot, 4)
    logs_error  = db.read_logs_byidrobot_lastproblems(id_robot, 4)
    process_queue   = []
    last_executions = []
    last_problems   = []
    for l in logs:
        l_dict = {
            'execution_id':l.id_schedule,
            'process': l.process_name,
            'success': l.state != "ERROR",
            'log': l.id,
            'ts': l.end_time
        }
        last_executions.append(l_dict)

    for l in logs_error:
        problem = {
            'execution_id': l.id_schedule,
            'log': l.id,
            'msg': l.data,
            'ts': l.end_time
        }
        last_problems.append(problem)

    process_dict = None
    if robot.process_running:
        process_dict = {
                            'id':robot.process_running['id'],
                            'name':robot.process_running['name'],
                            'id_log': robot.process_running['log'].id,
                            'priority': robot.process_running['priority'],
                            'completed': robot.process_running['log'].completed
                        }

    for p in robot.process_list:
        queue = { 
            'id': p['id'],
            'name':p['name'],
            'id_log': p['log'].id,
            'priority':p['priority']
        }
        process_queue.append(queue)

    (cpu, ram, disk) = stbi.get_robot_performance(robot.id, orch.id, orch.name, orch.company)
    stats = {

        'cpu':cpu,'ram':ram,'disk':disk
    }
        
    robot_dict = {  'name':robot.name,
                    'id':robot.id,
                    'ip_address':robot.ip_address,
                    'address':robot.address,
                    'os':robot.os,
                    'registrations':robot.registrations,
                    'mac':robot.mac,
                    'python_version':robot.python_version,
                    'token': robot.token,
                    'online': robot.online,
                    'time_online': 0 if not robot.online or not robot.connected else datetime.now().timestamp() - robot.connected,
                    'last_seen':time.timestamp(),
                    'process_running': process_dict,
                    'process_queue': process_queue,
                    'problems':last_problems,
                    'last_executions': last_executions,
                    'stats': stats
                }
    return json.dumps(robot_dict)

def get_robot_problems(id_robot=False) -> json:
    logs_error = db.read_logs_byidrobot_lastproblems(id_robot,0)
    last_problems=[]
    for l in logs_error:
        problem = {
            'robot_id':l.id_robot,
            'execution_id': l.id_schedule,
            'process_id':l.id_process,
            'process_name':l.process_name,
            'log': l.id,
            'msg': l.data,
            'ts': l.end_time
        }
        last_problems.append(problem)
    return json.dumps(last_problems)

