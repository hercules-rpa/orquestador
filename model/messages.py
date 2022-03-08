#RUTAS
ROUTE_MODULE_PROCESS    = "model.process."
ROUTE_ORCHESTRATOR      = "rpa.orchestrator"
ROUTE_ROBOT             = "rpa.robot."

#TYPE MESSAGES
INIT                    = "INIT"
KEEP_ALIVE              = "KEEP_ALIVE"
START_ORCH              = "START_ORCH"
LOG                     = "LOG"
ERROR                   = "ERROR"
NOTIFY                  = "NOTIFY"   
REQUEST_EXEC_PROCESS    = "EXEC_PROCESS"
EXEC_PROCESS            = "EXECUTING_PROCESS"
REQUEST_FEATURES        = "FEATURES"
PENDING_PROCESS         = "PENDING_PROCESS"
REMOVE_PROCESS          = "REMOVE_PROCESS"
UPDATE_INFO             = "UPDATE_INFO"
PAUSE_ROBOT             = "PAUSE_ROBOT"
RESUME_ROBOT            = "RESUME_ROBOT"
RESUME_PROCESS          = "RESUME_PROCESS"
KILL_PROCESS            = "KILL_PROCESS" 
CREATE_PROCESS          = "CREATE_PROCESS"     


MSG_INIT_ROBOT          = {"TYPE_MSG": INIT, "DESCRIPTION": "HELLO ORCHESTRATOR"}
MSG_INIT_ORC            = {"TYPE_MSG": INIT, "DESCRIPTION": "HELLO ROBOT"}
MSG_KEEP_ALIVE          = {"TYPE_MSG": KEEP_ALIVE, "DESCRIPTION": "KEEP ALIVE"}
MSG_START_ORCH          = {"TYPE_MSG": START_ORCH, "DESCRIPTION":"ORCHESTRATOR RESTART"}
MSG_LOG                 = {"TYPE_MSG": LOG, "DESCRIPTION": "LOG"}
MSG_ERROR               = {"TYPE_MSG": ERROR, "DESCRIPTION": "ERROR"}
MSG_REQUEST_PROCESS     = {"TYPE_MSG": REQUEST_EXEC_PROCESS, "DESCRIPTION": "REQUEST EXEC PROCESS"}
MSG_EXEC_PROCESS        = {"TYPE_MSG": EXEC_PROCESS, "DESCRIPTION": "EXECUTING PROCESS"}
MSG_REQUEST_FEATURES    = {"TYPE_MSG": REQUEST_FEATURES, "DESCRIPTION": "FEATURES"}
MSG_PENDING_PROCESS     = {"TYPE_MSG": PENDING_PROCESS, "DESCRIPTION": "PENDING"}
MSG_REMOVE_PROCESS      = {"TYPE_MSG": REMOVE_PROCESS, "DESCRIPTION": "REMOVE"}
MSG_RESUME_PROCESS      = {"TYPE_MSG": RESUME_PROCESS, "DESCRIPTION": "RESUME PROCESS"}
MSG_UPDATE_INFO         = {"TYPE_MSG": UPDATE_INFO, "DESCRIPTION": "UPDATE INFO"}
MSG_PAUSE_ROBOT         = {"TYPE_MSG": PAUSE_ROBOT, "DESCRIPTION": "PAUSE ROBOT"}
MSG_RESUME_ROBOT        = {"TYPE_MSG": RESUME_ROBOT, "DESCRIPTION": "RESUME ROBOT"}
MSG_KILL_PROCESS        = {"TYPE_MSG": KILL_PROCESS, "DESCRIPTION": "KILL PROCESS"}


#TODO. Permitir que los robots sean capaces de mandar ejecuciones
MSG_CREATE_PROCESS      = {"TYPE_MSG": CREATE_PROCESS, "DESCRIPTION": "CREATE PROCESS", "PROCESS": None, "FROM": None}



