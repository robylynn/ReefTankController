from collections.__init__ import OrderedDict

DATA_PATH = "C:\\Users\\robyl_000\\Documents\\Projects\\Aquarium\\Software\\ReefTankController\\data\\"

EMPTY_HARDWARE_CONFIGURATION = {'devices': {}, 'routes': {}, 'updates': 0}

PORT_TYPES = sorted(['DO', 'DI', 'AO', 'AI', 'I2C', 'TTL_Serial', 'RS-485', 'PWM', 'HTTP'])

GPIO_PINS = ['GPIO' + str(ndx) for ndx in range(2, 28)]

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
                     'Light Controller': ['name', 'address'],
                     'I2C Multiplexer': ['name', 'address'],
                     'IO Multiplexer': ['name', 'address'],
                     'ADC': ['name', 'address'],
                     'DAC': ['name', 'address'],
                     'PWM Generator': ['name', 'address'],
                     'SSR': ['name', 'address'],
                     'MOSFET': ['name', 'address']}

INSTALLED_DRIVERS = {'Main Controller': ['RPi'],
                     'Sensor': ['generic_analog', 'DS18B20', 'atlas_ph', 'atlas_orp', 'atlas_flow', 'atlas_ec'],
                     'Liquid Valve': ['generic_digital'],
                     'Gas Valve': ['generic_digital'],
                     'Motor Controller': ['teco_L510-101-H1-N'],
                     'Light Controller': ['zetlight_lancia2'],
                     'I2C Multiplexer': ["TCA9548A"],
                     'IO Multiplexer': ["SX1509"],
                     'ADC': ["ADS1115"],
                     'DAC': ["MCP4725"],
                     'PWM Generator': ["PCS9685"],
                     'SSR': ["generic_digital"],
                     'MOSFET': ["generic_digital"]}

SUBSYSTEMS = ['Protein Skimmer',
              'Ozone Reactor',
              'Reactor',
              'Algae Scrubber',
              'Heater',
              'Chiller',
              'Light',
              'RO/DI',
              'Sump',
              'Calcium Reactor',
              'ATO']

MySQL_TYPE_MAP = {'DATETIME': '%s', 'INT': '%s', 'FLOAT': '%s'}

DATABASE_CONFIGURATION = {
    'DATABASE_NAME': 'reef_data',
    'TABLES': {'sensor_data': OrderedDict({'timestamp': 'DATETIME', 'temp1': 'FLOAT', 'temp2': 'FLOAT', 'highside_pressure': 'FLOAT'}),
               'reports': OrderedDict({'health_check': 'INT'}),
               'system_data': OrderedDict({'cpu_usage_pct': 'INT', 'memory_commit_mb': 'INT'})}
}