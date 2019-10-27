from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager, SyncManager, NamespaceProxy
from threading import Thread
import inspect, time
import DatabaseTools

class PNCAppManager(SyncManager): pass

def registerProxy(name, cls, proxy, manager):
    for attr in dir(cls):
        if inspect.ismethod(getattr(cls, attr)) and not attr.startswith("__"):
            proxy._exposed_ += (attr,)
            setattr(proxy, attr,
                    lambda s: object.__getattribute__(s, '_callmethod')(attr))
    manager.register(name, cls, proxy)

class DatabaseInterfaceProxy(NamespaceProxy):
    _exposed_ = ('__getattribute__', '__setattr__', '__delattr__')

class SynchronizerProxy(NamespaceProxy):
    _exposed_ = ('__getattribute__', '__setattr__', '__delattr__')

class TankControllerManager(SyncManager):
    def __init__(self):
        super(TankControllerManager, self).__init__()
        #self.command_queue = Queue()
        #self.db_connection, self.db_cursor = DatabaseTools.ConnectToDB()

class Synchronizer():
    def __init__(self, manager):
        self.command_queue = manager.Queue()

class TankController(Process):
    def __init__(self, synchronizer, hardware_configuration):
        super(TankController, self).__init__()
        #self.system_manager = manager
        self.synchronizer = synchronizer
        self.hardware_configuration = hardware_configuration

        self.temp1_controller = TemperatureController(sample_rate=1)

        time.clock()

    def run(self):
        pass

class DeviceController(Thread):
    def __init__(self, sample_rate=1):
        super(DeviceController, self).__init__()
        self.run_thread = True
        self.sample_rate = sample_rate

        self.current_sensor_value = None

    def run(self):
        while self.run_thread:
            begin_time = time.clock()

            self.read()
            self.control()
            self.store_data()

            update_length = time.clock() - begin_time
            if update_length < self.sample_rate:
                time.sleep(self.sample_rate - update_length)

    def read(self):
        pass

    def control(self):
        pass

    def store_data(self):
        pass

class TemperatureController(DeviceController):
    def __init__(self, sample_rate=1, driver=None):
        super(TemperatureController, self).__init__(sample_rate=sample_rate)

    def run(self):
        pass



