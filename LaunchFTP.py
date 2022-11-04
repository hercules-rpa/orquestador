from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from rpa_orchestrator.lib.persistence.dbcon import ControllerDBPersistence
import os, sys
import json


# The directory the FTP user will have full read/write access to.
FTP_DIRECTORY = os.path.join(os.path.dirname(__file__), 'model')
FILEPATH_CONFIGURATION = "rpa_orchestrator/config/"
filename_configuration = "orchestrator.json"


if len(sys.argv) > 1:
    filename_configuration = sys.argv[1]


dirname = os.path.dirname(__file__)
file_path = os.path.join(dirname, FILEPATH_CONFIGURATION + filename_configuration)

try:
    with open(file_path) as json_orch:
        config = json.load(json_orch)
        json.loads(json.dumps(config['DB-PERSISTENCE']), object_hook=lambda d: ControllerDBPersistence(**d))
        global_setting   = ControllerDBPersistence().get_global_settings_by_id()

except Exception as e:
    print("###############################################################")
    print("###                       ERROR                             ###")
    print("###                     FTP  ERROR                          ###")
    print("###############################################################")
    print(str(e))
    exit()



def main():
    authorizer = DummyAuthorizer()

    # Define a new user having full r/w permissions.
    authorizer.add_user(global_setting.ftp_user, global_setting.ftp_password, FTP_DIRECTORY, perm='elradfmw')

    handler = FTPHandler
    handler.authorizer = authorizer

    handler.banner = "Process repository"
    address = ("0.0.0.0", global_setting.ftp_port)
    server = FTPServer(address, handler)

    server.max_cons = 256
    server.max_cons_per_ip = 16

    server.serve_forever()


if __name__ == '__main__':
    main()
    print("###############################################################")
    print("###                                                         ###")
    print("###                   FTP INICIALIZADO                      ###")
    print("###############################################################")
