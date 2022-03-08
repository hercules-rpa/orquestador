import json
import rpa_orchestrator.orchestrator  as  Orch


orch = Orch.Orchestrator()

def get_process(id_process) -> json:
    if id_process:
        process_mem = orch.get_process_by_id(id_process)
        if process_mem: #comprobamos si existe
            process = {}
            process['process_id']           = id_process
            process['process_class_name']   = orch.get_process_class_name_by_id(id_process)
            process['process_name']         = orch.get_process_name_by_id(id_process)
            process['process_description']  = orch.get_process_description_by_id(id_process)
            process['required']             = orch.get_process_requirements_by_id(id_process)
            process['capable_robots']       = orch.get_capable_robots(process)
            return json.dumps(process)
        return None
    else:
        process = []
        processes = orch.get_all_process()
        for key, value in processes.items():
            process.append(json.loads(get_process(value['id'])))
        return json.dumps(process)