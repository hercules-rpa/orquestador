import json
import rpa_orchestrator.lib.statistics        as stbi
import rpa_orchestrator.orchestrator      as Orch
import rpa_orchestrator.lib.statistics as stbi
from rpa_orchestrator.lib.persistence.dbcon import ControllerDBPersistence

orch = Orch.Orchestrator()
db = ControllerDBPersistence()


def get_main_stats() -> json :
    execution_day_week = stbi.get_executions_day_by_week(orch.id, orch.name, orch.company)
    execution_day_month = stbi.get_executions_days_by_month(orch.id, orch.name, orch.company)
    exectuion_month_year = stbi.get_executions_mounthly_by_year(orch.id, orch.name, orch.company)
    robots_online = sum(map(lambda x : orch.robot_list[x][0].online, orch.robot_list.keys()))
    process_actives = len(orch.schedule_list)
    process_problems = db.read_logs_problem_count()
    process_completed = stbi.get_number_executions_completed(orch.id, orch.name, orch.company)
    
    json_return = {}
    json_return['execution_day_week'] = execution_day_week
    json_return['execution_day_month'] = execution_day_month
    json_return['execution_month_year'] = exectuion_month_year
    json_return['robots_online'] = robots_online
    json_return['process_actives'] = process_actives
    json_return['process_problems'] = process_problems
    json_return['process_completed'] = process_completed
    return json.dumps(json_return)