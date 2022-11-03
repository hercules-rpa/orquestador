
class Robot():

    def __init__(self, id, name, address, registrations, ip_api='localhost', port_api=5000, frontend = None, online=False, connected=datetime.now().timestamp(), features=[pkg.key for pkg in pkg_resources.working_set], state="Iddle", process_running=None, process_list=[]):
        self.id = str(id)
        self.name = str(name)
        self.address = str(address)
        self.registrations = str(registrations)
        self.ip_api = str(ip_api)
        self.port_api = str(port_api)
        self.frontend = frontend
        self.ip_address = None
        # "".join(c + ":" if i % 2 else c for i,c in enumerate(hex(get_mac())[2:].zfill(12)))[:-1]
        self.mac = gma()
        self.token = str(UUID)
        self.python_version = sys.version
        self.online = online
        self.connected = connected
        self.features = features
        self.os = platform.system()
        self.state = state
        self.performance = [psutil.cpu_percent(), psutil.virtual_memory(
        ).percent, psutil.disk_usage('/').percent]  # CPU, RAM, DISK
        self.process_running = process_running
        # Procesos pendientes, cuando se vaya a ejecutar uno lo quitamos de esta lista y lo pasamos a process_running
        self.process_list = process_list
        self.process_pause = []
