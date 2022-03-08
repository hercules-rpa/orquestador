from datetime import datetime
from enum import Enum


class MSG_TYPE(Enum):
    TEXT            = "rpa.text"
    FILE            = "rpa.file"
    CONNECTION      = "rpa.connection"
    ERROR           = "rpa.error"
    PROCESS         = "rpa.process"
    PROCESS_CREATE  = "rpa.process.create"
    PROCESS_EXEC    = "rpa.process.exec"
    PROCESS_REMOVE  = "rpa.process.remove"
    PROCESS_ERROR   = "rpa.process.error"


class Event:
    def __init__(self, id = None, body = None, msgtype = MSG_TYPE.TEXT, sender = 'Orchestrator', read = False):
        self.id      = id
        self.body    = body
        self.msgtype = msgtype
        self.time    = datetime.now().timestamp()
        self.sender  = sender
        self.read    = read


