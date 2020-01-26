from threading import Thread
import pickle, base64, json
import HAL
#from collections import OrderedDict

#CONTROLLER_DATA_PATH =
from Statics import DATA_PATH, EMPTY_HARDWARE_CONFIGURATION

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

# class Device():
#     def __init__(self, **kwargs):#name='empty_port', port_type='DO', signal0_pin=None, signal1_pin=None):
#         self.name = None
#         self.port_type = None
#         self.signal0_pin = None
#         self.route = [{'origin': 'NULL', 'destination': 'NULL'}]
#
#         for key in kwargs.keys():
#             setattr(self, key, kwargs[key])
#             #self.key = kwargs[key]
#         # self.attributes
#         # self.name = name
#         # self.port_type = port_type# if port_type != None
#         # self.signal0_pin = signal0_pin
#         # self.attributes = [['Port Name', self.name], ['Port Type', self.port_type], ['Signal 0 Pin', self.signal0_pin]]
#
#     def TextSerialize(self):
#         return base64.b64encode(pickle.dumps(self)).decode()

def InitializeComms():
    HAL.InitializeI2C(1)
    HAL.Initialize1Wire()
    HAL.InitializeUART()

class MainStateMachine():
    def __init__(self):
        pass

def LoadHardwareConfiguration(data_path=DATA_PATH, configuration_file="hardware_configuration.json"):
    try:
        with open(data_path + configuration_file, 'r') as fh:
            return UnpackHardwareConfiguration(json.load(fh))
    except FileNotFoundError:
        return EMPTY_HARDWARE_CONFIGURATION

def SaveHardwareConfiguration(data_path=DATA_PATH, configuration_file="hardware_configuration.json", hardware_configuration={}):
    with open(data_path + configuration_file, 'w') as fh:
        json.dump(hardware_configuration, fh, indent=4)
        #configuration = fh.readlines()

def UnpackHardwareConfiguration(hardware_configuration):
    if type(hardware_configuration) == list:
        return hardware_configuration[0]
    else:
        return hardware_configuration

def clamp_value(value=0, lo_limit=0, hi_limit=0):
    return (value, lo_limit, hi_limit)[int(value < lo_limit) + 2 * int(value > hi_limit)]
    # (self.bus.read_i2c_block_data(self.address, downstream_object.bank_address, 2) and not (
    #             1 << downstream_object.endpoint_pin)) | (data << downstream_object.endpoint_pin)