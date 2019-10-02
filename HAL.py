import smbus

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