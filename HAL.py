#import smbus

#PORT_TYPES = ['Digital Output', 'Digital Input', 'Analog Output', 'Analog Input', 'I2C Port', 'TTL Serial Port', 'RS-485 Port']
PORT_TYPES = sorted(['DO', 'DI', 'AO', 'AI', 'I2C', 'TTL_Serial', 'RS-485', 'PWM', 'HTTP'])
GPIO_PINS = ['GPIO' + str(ndx) for ndx in range(2, 28)]
#SUPPORTED_DEVICES = sorted(['Sensor', 'Liquid Valve', 'Gas Valve', 'Motor Controller', 'Light', 'I2C Multiplexer', 'IO Multiplexer', 'ADC', 'SSR', 'MOSFET'])

#COMMON_DEVICE_ATTRIBUTES = [{'name': 'text'}, {'device_type': 'device_type_dropdown'}]
DEVICE_ATTRIBUTE_TYPES = {'name': 'text',
                          'device_type': 'device_type_dropdown',
                          'driver': 'driver_type_dropdown',
                          'protocol': 'text',
                          'address': 'text',
                          'input_address': 'text'}
SUPPORTED_DEVICES = {'Main Controller': ['name', 'address'],
                     'Sensor': ['name', 'address'],
                     'Liquid Valve': ['name'],
                     'Gas Valve': ['name'],
                     'Motor Controller': ['name', 'protocol'],
                     'Light': ['name', 'address'],
                     'I2C Multiplexer': ['name', 'address'],
                     'IO Multiplexer': ['name', 'address'],
                     'ADC': ['name', 'address'],
                     'DAC': ['name', 'address'],
                     'PWM Generator': ['name', 'address'],
                     'SSR': ['name', 'address'],
                     'MOSFET': ['name', 'address']}

# for device_key in SUPPORTED_DEVICES.keys():
#     supported_device_attributes = SUPPORTED_DEVICES[device_key]
#     #complete_device_attributes = {}
#     for common_key in DEVICE_ATTRIBUTE_TYPES.keys():
#         # if DEVICE_ATTRIBUTE_TYPES[common_key] == "text":
#         #     #complete_device_attributes[common_key] = COMMON_DEVICE_ATTRIBUTES[common_key]
#         supported_device_attributes[common_key] = DEVICE_ATTRIBUTE_TYPES[common_key]
#             #SUPPORTED_DEVICES[device_key][common_key] = COMMON_DEVICE_ATTRIBUTES[common_key]
#     #[complete_device_attributes[key] = supported_device_attributes[key] for key in supported_device_attributes.keys()]
#     #complete_device_attributes.update(supported_device_attributes)
#     SUPPORTED_DEVICES[device_key] = supported_device_attributes

#SUPPORTED_DEVICES = [{key: COMMON_DEVICE_ATTRIBUTES + SUPPORTED_DEVICES[key]} for key in SUPPORTED_DEVICES.keys()]
INSTALLED_DRIVERS = {'Main Controller': ['RPi'],
                     'Sensor': ['generic_analog', 'DS18B20', 'atlas_ph', 'atlas_orp', 'atlas_flow', 'atlas_ec'],
                     'Liquid Valve': ['generic_digital'],
                     'Gas Valve': ['generic_digital'],
                     'Motor Controller': ['teco_L510-101-H1-N'],
                     'Light': ['zetlight_lancia2'],
                     'I2C Multiplexer': ["TCA9548A"],
                     'IO Multiplexer': {"SX1509"},
                     'ADC': ["ADS1115"],
                     'DAC': ["MCP4725"],
                     'PWM Generator': ["PCS9685"],
                     'SSR': ["generic_digital"],
                     'MOSFET': ["generic_digital"]}

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