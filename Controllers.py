from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager, SyncManager, NamespaceProxy
from threading import Thread
import inspect, time, copy
import HAL, Statics, ControllerLibrary
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


        #self.HEATER_SSR.write(1)
        #z = self.HEATER_SSR.read()
        self.run_process = True
        time.clock()

    def run(self):
        self.launch_controller_threads()
        while self.run_process:
            pass
        #pass

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

    def launch_controller_threads(self):
        # for device in self.hardware_configuration['devices']:
        #     setattr(self, device + '_control_thread', DeviceController(device_object=getattr(self, device)))
        # for controller in self.hardware_configuration['controllers']:
        #     setattr(self, device + '_control_thread', DeviceController(device_object=getattr(self, device)))
        #pass
        #return
        for controller in self.hardware_configuration['controllers']:
            control_thread_args = {'name': controller,
                                   'synchronizer': self.synchronizer,
                                   'sample_rate:': float(self.hardware_configuration['controllers'][controller]['sample_rate']),
                                   'controller_type': Statics.SUPPORTED_CONTROLLERS[self.hardware_configuration['controllers'][controller]['controller_type']],
                                   'controller_args': self.hardware_configuration['controllers'][controller]['controller_settings'],
                                   'output_conditioner_type': Statics.SUPPORTED_OUTPUT_CONDITIONERS[self.hardware_configuration['controllers'][controller]['output_type']],
                                   'output_conditioner_args': self.hardware_configuration['controllers'][controller]['output_settings'],
                                   'sensor_object': getattr(self, self.hardware_configuration['controllers'][controller]['sensor']),
                                   'actuator_object': getattr(self, self.hardware_configuration['controllers'][controller]['actuator']),
                                   'interlock_object': getattr(self, self.hardware_configuration['controllers'][controller]['interlock'])}
            setattr(self, controller, DeviceController(**control_thread_args))
            getattr(self, controller).start()


#class

class DeviceController(Thread):
    def __init__(self, name='', synchronizer=None, sample_rate=1, controller_type=None, controller_args={}, output_conditioner_type=None,
                 output_conditioner_args={}, sensor_object=None, actuator_object=None, interlock_object=None, **kwargs):
        super(DeviceController, self).__init__()
        self.__dict__.update(kwargs)

        self.name = name
        self.synchronizer = synchronizer
        self.sample_rate = sample_rate
        self.sensor_object = sensor_object
        self.actuator_object = actuator_object
        self.interlock_object = interlock_object
        self.controller = globals()[controller_type](**controller_args)
        self.output_conditioner = globals()[output_conditioner_type](**output_conditioner_args)

        self.current_sensor_value = None
        #self.device_object = device_object
        #self.route = route

        self.run_thread = True

    # def initialize(self):
    #     self.output_conditioner = getattr(self.output_conditioner_type)()

    def run(self):
        while self.run_thread:
            begin_time = time.clock()
            continue

            self.read()
            self.control()
            self.store_data()

            update_length = time.clock() - begin_time
            if update_length < self.sample_rate:
                sleep_time = self.sample_rate - update_length
                print('Thread ' + self.name + ' sleeping for ' + str(sleep_time))
                time.sleep(self.sample_rate - update_length)

    def read(self):
        self.current_sensor_value = self.sensor_object.read()
        # for device in self.route:
        #     getattr(self, device).open_upstream()
        #
        # pass

    def control(self):
        pass

    def store_data(self, sensor_data=None, actuator_data=None):
        pass

    def read_device(self):
        pass

    def write_device(self):
        pass

    def open_upstream(self):
        pass

class Controller():
    def __init__(self):
        pass

    def calculate_output(self):
        pass

class PIDController(Controller):
    def __init__(self, p_gain=0, i_gain=0, d_gain=0, i_limit=0):
        super(PIDController, self).__init__()
        self.p_gain = p_gain
        self.i_gain = i_gain
        self.d_gain = d_gain
        self.i_limit = i_limit

        self.integrated_error = 0
        self.dedt = 0
        self.last_error_value = 0
        self.last_update_time = 0

    def calculate_output(self, setpoint=0, current_PV=0):
        error = setpoint - current_PV
        self.integrated_error = ControllerLibrary.clamp_value(value=self.integrated_error + error, lo_limit=-self.i_limit, hi_limit=self.i_limit)
        self.dedt = (error - self.last_error_value)/(time.clock() - self.last_update_time)
        self.last_update_time = time.clock()

        p_component = self.p_gain * error
        i_component = self.i_gain * self.integrated_error
        d_component = self.d_gain * self.dedt

        return p_component + i_component + d_component

class BangBangController(Controller):
    def __init__(self, hysteresis=0):
        super(BangBangController, self).__init__()
        #self.lo_limit = lo_limit
        #self.hi_limit = hi_limit
        self.hysteresis = hysteresis
        self.state = 0

    def calculate_output(self, setpoint=0, current_PV=0):
        if self.state == 1:
            if (current_PV - setpoint) > self.hysteresis:
                self.state = 0
        else:
            if (setpoint - current_PV) > self.hysteresis:
                self.state = 1
        return self.state
        # if setpoint - current_PV < self.hysteresis:
        #     return 1
        # elif current_PV - setpoint > self.hysteresis:
        #     return 1
        # return 0
        #return (0, 1)[(setpoint-current_PV) < self.hysteresis and (setpoint-current_PV) < self.hysteresis]

class TimeController(Controller):
    pass

class OutputConditioner():
    def __init__(self):
        self.condition_fcn = self.null_condition_fcn

    def condition_output(self, value):
        return self.condition_fcn(value)

    def null_condition_fcn(self, value):
        return value

class PassthroughOutputConditioner(OutputConditioner):
    def __init__(self):
        super(PassthroughOutputConditioner, self).__init__()

class SoftwarePWMGenerator(OutputConditioner):
    def __init__(self, period=10):
        self.period = period
        self.state = 0
        self.condition_fcn = self.run_cycle

        self.begin_time = time.clock()

    def run_cycle(self, duty_cycle):
        if (time.clock() - self.begin_time) > duty_cycle * self.period:
            self.state = 0
        else:
            self.state = 1

        if (time.clock() - self.begin_time) > self.period:
            self.begin_time = time.clock()

        return self.state

class TemperatureController(DeviceController):
    def __init__(self, sample_rate=1, driver=None):
        super(TemperatureController, self).__init__(sample_rate=sample_rate)
        self.driver = driver

    # def run(self):
    #     pass

    def read(self):
        value = self.driver.read()

