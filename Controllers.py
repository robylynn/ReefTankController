from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager, SyncManager, NamespaceProxy
from threading import Thread
import inspect, time, copy
import HAL, Statics
import DatabaseTools

#class PNCAppManager(SyncManager): pass

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
        self.hardware_configuration = copy.deepcopy(hardware_configuration)

        #self.temp1_controller = TemperatureController(sample_rate=1)

        self.build_hardware_tree()
        self.populate_route_pointers()

        self.HEATER_SSR.write(1)
        z = self.HEATER_SSR.read()
        time.clock()

    def run(self):
        pass

    def build_hardware_tree(self):
        for device in self.hardware_configuration['devices']:
            device_name = self.hardware_configuration['devices'][device]['name']
            #device_class = Statics.DEVICE_CLASS_MAP[self.hardware_configuration['devices'][device]['driver']]['class']
            driver_class = self.hardware_configuration['devices'][device]['driver'] + '_driver'
            #device_settings = Statics.DEVICE_CLASS_MAP[self.hardware_configuration['devices'][device]['driver']]['settings']
            device_settings = self.hardware_configuration['devices'][device]
            setattr(self, device_name, getattr(HAL, driver_class)(**device_settings))

    def populate_route_pointers(self):
        for device in self.hardware_configuration['devices']:
            device_name = self.hardware_configuration['devices'][device]['name']
            route_list = []
            for segment in self.hardware_configuration['routes'][device]:
                route_list += [getattr(self, segment)]
            setattr(getattr(self, device_name), 'route', route_list)
                #setattr(getattr(self, device_name), 'route', self.hardware_configuration['routes'][device_name])

    def launch_device_threads(self):
        for device in self.hardware_configuration['devices']:
            setattr(self, device + '_control_thread', DeviceController(device_object=getattr(self, device)))
        #pass


#class

class DeviceController(Thread):
    def __init__(self, device_object=None, route=[]):
        super(DeviceController, self).__init__()
        self.run_thread = True
        self.device_object = device_object
        self.route = route

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
        for device in self.route:
            getattr(self, device).open_upstream()

        pass

    def control(self):
        pass

    def store_data(self):
        pass

    def read_device(self):
        pass

    def write_device(self):
        pass

    def open_upstream(self):
        pass

class TemperatureController(DeviceController):
    def __init__(self, sample_rate=1, driver=None):
        super(TemperatureController, self).__init__(sample_rate=sample_rate)
        self.driver = driver

    # def run(self):
    #     pass

    def read(self):
        value = self.driver.read()

