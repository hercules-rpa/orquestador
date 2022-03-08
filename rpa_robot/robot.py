from uuid import getnode as get_mac

class Robot():

    def __init__(self, id, name, address, registrations, online=False, connected=datetime.now().timestamp(), features=[pkg.key for pkg in pkg_resources.working_set], state="Iddle", process_running=None, process_list=[]):
        self.id = str(id)
        self.name = str(name)
        self.address = str(address)
        self.registrations = str(registrations)
        self.ip_address = None
        self.mac = ''
        self.python_version = ''
        self.online = online
        self.connected = connected
        self.features = features
        self.os = ''
        self.state = state
        self.performance = ''
        self.process_running = process_running
        # Procesos pendientes, cuando se vaya a ejecutar uno lo quitamos de esta lista y lo pasamos a process_running
        self.process_list = process_list
        self.process_pause = []
        
    