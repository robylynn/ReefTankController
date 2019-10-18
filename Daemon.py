import os, json

import Dashboard, Controllers#mysql
from ControllerLibrary import LoadHardwareConfiguration
from multiprocessing import Process, Manager

if __name__ == '__main__':
    #ControllerFrontend = FrontEnd.initialize_frontend()
    #ControllerFrontend.run_server(debug=True)
    #LoadHardwareConfiguration()
    hardware_configuration = LoadHardwareConfiguration()

    SystemController = Controllers.TankController()
    SystemManager = Controllers.TankControllerManager()

    TankControllerFrontEnd, TankControllerSharedMemory = Dashboard.InitializeFrontend(hardware_configuration=hardware_configuration, system_manager=SystemManager)
    TankControllerFrontEnd.run_server(debug=True, port=8080, host='0.0.0.0')