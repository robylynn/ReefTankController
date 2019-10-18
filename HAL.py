#import smbus

#PORT_TYPES = ['Digital Output', 'Digital Input', 'Analog Output', 'Analog Input', 'I2C Port', 'TTL Serial Port', 'RS-485 Port']
PORT_TYPES = sorted(['DO', 'DI', 'AO', 'AI', 'I2C', 'TTL_Serial', 'RS-485', 'PWM', 'HTTP'])
GPIO_PINS = ['GPIO' + str(ndx) for ndx in range(2, 28)]
#SUPPORTED_DEVICES = sorted(['Sensor', 'Liquid Valve', 'Gas Valve', 'Motor Controller', 'Light', 'I2C Multiplexer', 'IO Multiplexer', 'ADC', 'SSR', 'MOSFET'])

#COMMON_DEVICE_ATTRIBUTES = [{'name': 'text'}, {'device_type': 'device_type_dropdown'}]
COMMON_DEVICE_ATTRIBUTES = {'name': 'text', 'device_type': 'device_type_dropdown'}
SUPPORTED_DEVICES = {'Sensor': {}, 'Liquid Valve': {}, 'Gas Valve': {}, 'Motor Controller': {"protocol": "text"}, 'Light': {}, 'I2C Multiplexer': {"input_address": "text"}, 'IO Multiplexer': {'address': 'text'}, 'ADC': {}, 'SSR': {'signel_type': "port_type_dropdown"}, 'MOSFET': {}}
for device_key in SUPPORTED_DEVICES.keys():
    supported_device_attributes = SUPPORTED_DEVICES[device_key]
    #complete_device_attributes = {}
    for common_key in COMMON_DEVICE_ATTRIBUTES.keys():
        if common_key != "device_type":
            #complete_device_attributes[common_key] = COMMON_DEVICE_ATTRIBUTES[common_key]
            supported_device_attributes[common_key] = COMMON_DEVICE_ATTRIBUTES[common_key]
            #SUPPORTED_DEVICES[device_key][common_key] = COMMON_DEVICE_ATTRIBUTES[common_key]
    #[complete_device_attributes[key] = supported_device_attributes[key] for key in supported_device_attributes.keys()]
    #complete_device_attributes.update(supported_device_attributes)
    SUPPORTED_DEVICES[device_key] = supported_device_attributes
#SUPPORTED_DEVICES = [{key: COMMON_DEVICE_ATTRIBUTES + SUPPORTED_DEVICES[key]} for key in SUPPORTED_DEVICES.keys()]


def InitializeI2C(channel=1):
    return smbus.SMBus(channel)

def InitializeUART():
    pass

def Initialize1Wire():
    pass

class I2CDevice():
    def __init__(self, address=0x0, bus=None):
        self.address = address
        self.bus = bus

    def Write(self, data=0x0, register_command=0x0):
        self.bus.write_i2c_block_data(self.address, register_command, data)

class TemperatureSensor(I2CDevice):
    def __init__(self, address=0x0):
        super().__init__(address=address)

    def ReadValue(self):
        self.Write()

class pHSensor(I2CDevice):
    def __init__(self, address=0x0):
        super().__init__(address=address)