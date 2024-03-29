import json
import rpa_orchestrator.orchestrator  as  Orch


orch = Orch.Orchestrator()

def get_process(id_process, visible) -> json:
    if id_process:
        process_mem = orch.get_process_by_id(id_process)
        if process_mem:
            process = {}
            process['process_id']           = id_process
            process['process_class_name']   = orch.get_process_class_name_by_id(id_process)
            process['process_name']         = orch.get_process_name_by_id(id_process)
            process['process_description']  = orch.get_process_description_by_id(id_process)
            process['required']             = orch.get_process_requirements_by_id(id_process)
            process['capable_robots']       = orch.get_capable_robots(process)
            process['visible']              = orch.get_process_visible_by_id(id_process)
            process['setting']              = orch.get_process_setting_by_id(id_process)
            if visible is not None and visible == process['visible']:
                return json.dumps(process)
            elif visible is None:
                return json.dumps(process)
        return None
    else:
        process = []
        processes = orch.get_all_process()
        for key, value in processes.items():
            process_data = get_process(value['id'], visible)
            if process_data:
                process.append(json.loads(process_data))
        return json.dumps(process)