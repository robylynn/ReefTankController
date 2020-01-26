try:
    import smbus2
except:
    import math as smbus2

#PORT_TYPES = ['Digital Output', 'Digital Input', 'Analog Output', 'Analog Input', 'I2C Port', 'TTL Serial Port', 'RS-485 Port']

def InitializeI2C(channel=1):
    return smbus2.SMBus(channel)

def InitializeUART():
    pass

def Initialize1Wire():
    pass

def set_bit(byte=None, bit=None, value=None):
    return (byte and not (1 << bit)) | (value << bit)

# class HAL(Process):
#     pass

class MainController():
    def __init__(self, address='127.0.0.1', **kwargs):
        self.address = address
        self.__dict__.update(kwargs)
        # for arg in self._kwargs:
        #     setattr(self, arg, self._kwargs[arg])

class Device():
    def __init__(self):
        pass

    def _open_upstream(self, downstream_object=None, transaction_fcn=None, fcn_args=None, data=None):
        try:
            upstream_device = self.route[0]
            retval = 0
            if upstream_device.device_type != 'Main Controller':
                retval = upstream_device.open_upstream(downstream_object=downstream_object, transaction_fcn=transaction_fcn, fcn_args=fcn_args, data=data)
                #self.open_mux_bus(downstream_object.mux_bus)
                #state = (self.bus.read_i2c_block_data(self.address, downstream_object.bank_address, 2) and not(1 << downstream_object.endpoint_pin)) | (data << downstream_object.endpoint_pin)
                # bank_addr = self.find_bank_register_address(register_addresses=self.REGDATA, pin=downstream_object.endpoint_pin)
                # state = set_bit(byte=self._read_register(bank_addr, 1), bit=downstream_object.endpoint_pin, value=data)
                # self._write(register=bank_addr, data=state)
                #self.master_bus.write_i2c_block_data(self.address, downstream_object.bank_address, bin(state))
                #else:
                #self.open_mux_bus(downstream_object.mux_bus)
            return transaction_fcn(return_value=retval, **fcn_args)
                # state = (self.bus.read_i2c_block_data(self.address, downstream_object.bank_address, 2) and not (
                #             1 << downstream_object.endpoint_pin)) | (data << downstream_object.endpoint_pin)
                # self.master_bus.write_i2c_block_data(self.address, downstream_object.bank_address, bin(state))
        except IndexError:
            #Should not be possible
            raise Exception

    def null_transaction_fcn(self, **kwargs):
        pass

    def null_write_fcn(self, return_value=0, **kwargs):
        #pass
        return return_value

    def null_read_fcn(self, return_value=0, **kwargs):
        #pass
        return return_value

class Interlock(Device):
    def __init__(self):
        pass

    def engage(self):
        pass

    def disengage(self):
        pass

class DigitalInterlock(Device):
    pass

class I2CDevice(Device):
    def __init__(self, bus=None, address=0x70, sample_rate=1, **kwargs):
        self.bus = bus
        self.address = address
        self.sample_rate = sample_rate
        self.simulate = True
        self.__dict__.update(kwargs)

    def _read(self, num_bytes=1):
        if not self.simulate:
            message = smbus2.i2c_msg.read(self.address, num_bytes)
            self.bus.i2c_rdwr(message)
            return message
        else:
            return 0x0

    def _write(self, register=0x0, data=None):
        if not self.simulate:
            if data != None:
                message = smbus2.i2c_msg.write(self.address, [register, data])
            else:
                message = smbus2.i2c_msg.write(self.address, [register])
            self.bus.i2c_rdwr(message)
            return message
        else:
            return 0x0
        #self.bus.write_i2c_block_data(self.address, register_command, data)

    def _read_register(self, register=0x0, num_bytes=1):
        if not self.simulate:
            write_msg = smbus2.i2c_msg.write(self.address, [register])
            read_msg = smbus2.i2c_msg.read(self.address, num_bytes)
            self.bus.i2c_rdwr(write_msg, read_msg)
            return read_msg
        else:
            return 0x0

    def _write_read(self, register=0x0, data=0x0, num_bytes=1):
        if type(data) != 'list':
            data = [data]
        if not self.simulate:
            write_msg = smbus2.i2c_msg.write(self.address, [register] + data)
            read_msg = smbus2.i2c_msg.read(self.address, num_bytes)
            self.bus.i2c_rdwr(write_msg, read_msg)
            return read_msg
        else:
            return 0x0

#class 1WireDevice()

class HTTPDevice():
    def __init__(self, address='192.168.1.1', sample_rate=1, **kwargs):
        self.address = address
        self.sample_rate = sample_rate
        self.__dict__.update(kwargs)

class DIODevice(Device):
    def __init__(self, pin=0, output=False, sample_rate=1, **kwargs):
        self.pin = pin
        self.output = output
        self.sample_rate = sample_rate
        self.__dict__.update(kwargs)

    def write(self, value):
        # upstream_device = self.route[0]
        # if upstream_device.device_type != 'Main Controller':
        #     upstream_device.open_upstream(data=value, device_object=self)
        #self.transact(value)
        self._open_upstream(downstream_object=self, transaction_fcn=self.null_write_fcn, fcn_args={}, data=value)

    # def _write(self, value):
    #     self.value = value

    def read(self):
        # upstream_device = self.route[0]
        # if upstream_device.device_type != 'Main Controller':
        #     upstream_device.open_upstream(device_object=self)
        #self.transact()
        return self._open_upstream(downstream_object=self, transaction_fcn=self.null_read_fcn, fcn_args={})

class AIODevice(Device):
    def __init__(self, pin=0, output=False, scaling_factor=1, **kwargs):
        self.pin = pin
        self.output = output
        self.scaling_factor = scaling_factor
        self.__dict__.update(kwargs)

        self.range = [0, 1]

    def read(self):
        return self._open_upstream(downstream_object=self, transaction_fcn=self.null_read_fcn, fcn_args={})

class TemperatureSensor(I2CDevice):
    def __init__(self, address=0x0):
        super().__init__(address=address)

    def ReadValue(self):
        self.Write()

class pHSensor(I2CDevice):
    def __init__(self, address=0x0):
        super().__init__(address=address)

#class DS18B20_driver(OneWireDevice)

class RPi_driver(MainController):
    def __init__(self, address='127.0.0.1', **kwargs):
        super(RPi_driver, self).__init__(address=address, **kwargs)

class TCA9548A_driver(I2CDevice):
    def __init__(self, bus=0, address=0x70, **kwargs):
        super(TCA9548A_driver, self).__init__(bus=bus, address=address, **kwargs)

    def open_upstream(self, downstream_object=None, transaction_fcn=None, fcn_args={}, data=None):
        self._open_upstream(downstream_object=downstream_object, transaction_fcn=self.open_mux_bus,
                                      fcn_args={'bus': downstream_object.mux_bus})

    def open_mux_bus(self, bus=0, **kwargs):
        self._write(1 << bus)

class SX1509_driver(I2CDevice):
    def __init__(self, master_bus=0, address=0x3E, **kwargs):
        super(SX1509_driver, self).__init__(bus=master_bus, address=address, **kwargs)
        self.REGDATAB = 0x10
        self.REGDATAA = 0x11
        self.REGDATA = (0x10, 0x11)

    def configure_device(self):
        self._write(self.address, 0x08, bin(self.data_register_configuration))

    def find_bank_register_address(self, register_addresses=(0x0, 0x0), pin=0):
        #return (start_register_addr+1, start_register_addr)[pin > 7]
        return register_addresses[pin > 7]

    def open_upstream(self, downstream_object=None, transaction_fcn=None, fcn_args={}, data=None):
        if transaction_fcn.__func__ == self.null_write_fcn.__func__:
            return self._open_upstream(downstream_object=self, transaction_fcn=self.set_IO_point,
                                fcn_args={'pin': downstream_object.pin, 'value': data}, data=data)
        elif transaction_fcn.__func__ == self.null_read_fcn.__func__:
            return self._open_upstream(downstream_object=self, transaction_fcn=self.get_IO_point,
                                fcn_args={'pin': downstream_object.pin}, data=data)
        else:
            raise Exception

    def set_IO_point(self, pin=0, value=0, **kwargs):
        bank_addr = self.find_bank_register_address(register_addresses=self.REGDATA, pin=pin)
        state = set_bit(byte=self._read_register(bank_addr, 1), bit=pin, value=value)
        self._write(register=bank_addr, data=state)

    def get_IO_point(self, pin=0, **kwargs):
        bank_addr = self.find_bank_register_address(register_addresses=self.REGDATA, pin=pin)
        register_state = self._read_register(bank_addr, 1)
        return ((register_state >> pin) and 1)
        #state = set_bit(byte=self._read_register(bank_addr, 1), bit=pin, value=value)
        #self._write(register=bank_addr, data=state)

    def read(self):
        pass
        # upstream_device = self.route[0]
        # if upstream_device.device_type != 'Main Controller':
        #     upstream_device.open_upstream(self.bus)

class ADS1115_driver(I2CDevice):
    def __init__(self, master_bus=0, address=0x3E, **kwargs):
        super(ADS1115_driver, self).__init__(bus=master_bus, address=address, **kwargs)
        #self.REGDATAB = 0x10
        #self.REGDATAA = 0x11
        #self.REGDATA = (0x10, 0x11)
        self.op_status_config = 0
        self.input_mux_config = 1 << 2
        self.gain_config = 1 << 1
        self.op_mode_config = 0
        self.data_rate_config = (1 << 2) + (1 << 1) + 1
        self.comparator_mode_config = 0
        self.comparator_polarity_config = 0
        self.comparator_latch_config = 0
        self.comparator_queue_config = (1 << 1) + 1
        # self.config_word = (self.op_status_config << 15) + (self.input_mux_config << 12) + (self.gain_config << 9) + (
        #             self.op_mode_config << 8) + (self.data_rate_config << 5) + (self.comparator_mode_config << 4) + (
        #                                self.comparator_polarity_config << 3) + (self.comparator_latch_config << 2) + (
        #                                self.comparator_queue_config << 1)


    def build_config_word(self):
        return (self.op_status_config << 15) + (self.input_mux_config << 12) + (self.gain_config << 9) + (
                    self.op_mode_config << 8) + (self.data_rate_config << 5) + (self.comparator_mode_config << 4) + (
                                       self.comparator_polarity_config << 3) + (self.comparator_latch_config << 2) + (
                                       self.comparator_queue_config << 1)

    def configure_device(self):
        self._open_upstream(downstream_object=self, transaction_fcn=self._configure, fcn_args={})

    def select_single_ended_input_line(self, input_line=0):
        self.input_mux_config = 0x4 + hex(input_line)
        self.configure_device()

    def _configure(self):
        self._write(register=0x1, data=self.build_config_word())

    def open_upstream(self, downstream_object=None, transaction_fcn=None, fcn_args={}, data=None):
        if transaction_fcn.__func__ == self.null_read_fcn.__func__:
            self._open_upstream(downstream_object=downstream_object, transaction_fcn=self.read_input_line,
                                fcn_args={'input_line': downstream_object.pin})

    def read_input_line(self, input_line=0):
        self.select_single_ended_input_line(input_line)
        return self._write_read(register=0, num_bytes=2)

class zetlight_lancia2_driver(HTTPDevice):
    def __init__(self, address='192.168.1.1', sample_rate=1, **kwargs):
        super(zetlight_lancia2_driver, self).__init__(address=address, sample_rate=sample_rate, **kwargs)
        # self.address = address
        # self.sample_rate = sample_rate
        # self.__dict__.update(kwargs)

class generic_digital_driver(DIODevice):
    def __init__(self, pin=0, output=False, sample_rate=1, **kwargs):
        super(generic_digital_driver, self).__init__(pin=pin, output=output, sample_rate=sample_rate, **kwargs)
        # self.pin = pin
        # self.output = output
        # self.sample_rate = sample_rate
        # self.__dict__.update(kwargs)

class generic_analog_driver(AIODevice):
    def __init__(self, pin=0, output=False, scaling_factor=1, sample_rate=1, **kwargs):
        super(generic_analog_driver, self).__init__(pin=pin, output=output, scaling_factor=scaling_factor, **kwargs)