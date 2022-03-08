import os
import sys
import json
import asyncio
from threading import Thread
from controller.ControllerAMQP       import ControllerAMQP
from rpa_orchestrator.lib.persistence.dbcon import ControllerDBPersistence
from rpa_orchestrator.lib.dbprocess.dbcon import ControllerDBProcess
from rpa_orchestrator.lib.bi.dbcon import ControllerDBBI
from rpa_orchestrator.orchestrator import Orchestrator


loop                = asyncio.get_event_loop()
loop_consumer       = asyncio.get_event_loop()

def robot_persistence():
    Orchestrator().reload_robot()

def schedule_persistence():
    Orchestrator().reload_schedule()

def process_persistence():
    Orchestrator().reload_process()


if __name__ == "__main__":

    FILEPATH_CONFIGURATION = "rpa_orchestrator/config/"
    filename_configuration = "orchestrator.json"


    if len(sys.argv) > 1:
        filename_configuration = sys.argv[1]



    print("###############################################################")
    print("###               INICIALIZANDO ORQUESTADOR                 ###")

    print("###     -Loading configuration JSON                         ###")

    dirname = os.path.dirname(__file__)
    file_path = os.path.join(dirname, FILEPATH_CONFIGURATION + filename_configuration)

    try:
        with open(file_path) as json_orch:
            config = json.load(json_orch)
            json.loads(json.dumps(config['AMQP-SETTING']), object_hook=lambda d: ControllerAMQP(**d))
            print("###     - ControllerAMQP.               OK                  ###")
            json.loads(json.dumps(config['DB-PERSISTENCE']), object_hook=lambda d: ControllerDBPersistence(**d))
            print("###     - DB-PERSISTENCE.               OK                  ###")
            json.loads(json.dumps(config['DB-PROCESS']), object_hook=lambda d: ControllerDBProcess(**d))
            print("###     - DB-PROCESS.                   OK                  ###")
            json.loads(json.dumps(config['DB-BI']), object_hook=lambda d: ControllerDBBI(**d))
            print("###     - DB-BI.                        OK                  ###")
            json.loads(json.dumps(config['ORCHESTRATOR-SETTING']), object_hook=lambda d: Orchestrator(**d))
            print("###     - Orchestrator.                 OK                  ###")
    except Exception as e:
        print("###############################################################")
        print("###                       ERROR                             ###")
        print(str(e))
        print("###                ORQUESTADOR ERROR                        ###")
        print("###############################################################")









    ControllerAMQP().set_listener(Orchestrator())
    print("###     - Add listener to controller.   OK                  ###")
    loop_consumer.run_until_complete(ControllerAMQP().start_consumer(loop))
    #loop_consumer.create_task esto estaba antes
    thread_orchestrator = Thread(target=Orchestrator().run)
    thread_orchestrator.start()





    #INICIALIZAMOS FLASK
    from rpa_orchestrator.app import create_app
    settings_module = os.getenv('APP_SETTINGS_MODULE')
    app = create_app(settings_module)
    p = Thread(target=app.run, kwargs={'host':"0.0.0.0"})
    p.start()
    print("###     - FLASK INITIALIZED             OK                  ###")
    robot_persistence()
    print("###     - Recover robots from BBDD      OK                  ###")
    schedule_persistence()
    print("###     - Recover schedules from BBDD   OK                  ###")
    process_persistence()
    print("###     - Recover process from BBDD     OK                  ###")
    print("###                                                         ###")
    print("###                ORQUESTADOR INICIALIZADO                 ###")
    print("###############################################################")
    loop.run_forever()





