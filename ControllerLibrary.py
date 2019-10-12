from threading import Thread
import pickle, base64
import HAL

#CONTROLLER_DATA_PATH =

class Port():
    def __init__(self, **kwargs):#name='empty_port', port_type='DO', signal0_pin=None, signal1_pin=None):
        self.name = None
        self.port_type = None
        self.signal0_pin = None
        self.route = [{'origin': 'NULL', 'destination': 'NULL'}]

        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            #self.key = kwargs[key]
        # self.attributes
        # self.name = name
        # self.port_type = port_type# if port_type != None
        # self.signal0_pin = signal0_pin
        # self.attributes = [['Port Name', self.name], ['Port Type', self.port_type], ['Signal 0 Pin', self.signal0_pin]]

    def TextSerialize(self):
        return base64.b64encode(pickle.dumps(self)).decode()

class Device():
    def __init__(self, **kwargs):#name='empty_port', port_type='DO', signal0_pin=None, signal1_pin=None):
        self.name = None
        self.port_type = None
        self.signal0_pin = None
        self.route = [{'origin': 'NULL', 'destination': 'NULL'}]

        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            #self.key = kwargs[key]
        # self.attributes
        # self.name = name
        # self.port_type = port_type# if port_type != None
        # self.signal0_pin = signal0_pin
        # self.attributes = [['Port Name', self.name], ['Port Type', self.port_type], ['Signal 0 Pin', self.signal0_pin]]

    def TextSerialize(self):
        return base64.b64encode(pickle.dumps(self)).decode()

class TemperatureController(Thread):
    def __init__(self, sample_rate = 1):
        self.sample_rate = sample_rate

def InitializeComms():
    HAL.InitializeI2C(1)
    HAL.Initialize1Wire()
    HAL.InitializeUART()

class MainStateMachine():
    def __init__(self):
        pass

def LoadHardwareConfiguration():
    pass

def SaveHardwareConfiguration():
    pass