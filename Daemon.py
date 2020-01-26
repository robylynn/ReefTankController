import os, json

import Dashboard, Controllers#mysql
from ControllerLibrary import LoadHardwareConfiguration
from DatabaseTools import DatabaseInterface
from multiprocessing import Process, Manager

if __name__ == '__main__':
    #ControllerFrontend = FrontEnd.initialize_frontend()
    #ControllerFrontend.run_server(debug=True)
    #LoadHardwareConfiguration()
    hardware_configuration = LoadHardwareConfiguration()
    Controllers.registerProxy('DBConnection', DatabaseInterface, Controllers.DatabaseInterfaceProxy, Controllers.TankControllerManager)
    # Controllers.registerProxy('Synchronizer', Controllers.Synchronizer, Controllers.SynchronizerProxy,
    #                           Controllers.TankControllerManager)

    SystemManager = Controllers.TankControllerManager()
    SystemManager.start()

    #DatabaseConnector = SystemManager.DBConnection()
    ProcessSynchronizer = Controllers.Synchronizer(SystemManager)
    ProcessSynchronizer.database_connector = SystemManager.DBConnection()

    SystemController = Controllers.TankController(ProcessSynchronizer, hardware_configuration)
    #SystemController.start()

    TankControllerFrontEnd, TankControllerSharedMemory = Dashboard.InitializeFrontend(hardware_configuration=hardware_configuration, system_manager=SystemManager, synchronizer=ProcessSynchronizer)
    TankControllerFrontEnd.run_server(debug=True, port=8080, host='0.0.0.0')