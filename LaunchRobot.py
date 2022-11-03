import os
import sys
import json
import asyncio
from controller.ControllerAMQP       import ControllerAMQP
from rpa_robot.robot                import Robot
from threading                       import Thread

if __name__ == "__main__":
    FILEPATH_CONFIGURATION = "rpa_robot/config/"
    cfgfile = "robot.json"


    if len(sys.argv) > 1:
        cfgfile = sys.argv[1]


    print("###############################################################")
    print("###               INICIALIZANDO ROBOT                       ###")

    print("###     -Loading configuration JSON                         ###")

    dirname = os.path.dirname(__file__)
    file_path = os.path.join(dirname, FILEPATH_CONFIGURATION + cfgfile)
    robot = None
    try:
        with open(file_path) as json_robot:
            config = json.load(json_robot)
            json.loads(json.dumps(config['AMQP-SETTING']), object_hook=lambda d: ControllerAMQP(**d))
            robot = json.loads(json.dumps(config['ROBOT-SETTING']), object_hook=lambda d: Robot(**d))
            
            
            
            
    except:
        print("Error in instace ControlerAMQP. No such file or directory")
        print("###                ROBOT ERROR                              ###")
        print("###############################################################")


    ControllerAMQP().set_listener(robot)
    
    loop            = asyncio.get_event_loop()
    loop_consumer   = asyncio.get_event_loop()

    print("###          - ControllerAMQP.               OK             ###")
    print("###          - Robot.                        OK             ###")
    print("###     - Add listener to controller.   OK                  ###")
    print("###                                                         ###")
    print("###                ROBOT INICIALIZADO                       ###")
    print("###############################################################")
    loop_consumer.run_until_complete(ControllerAMQP().start_consumer(loop))
    #loop_consumer.create_task(ControllerAMQP().start_consumer(loop))
    thread_robot = Thread(target=robot.run)
    thread_robot.start()
    loop.run_forever()