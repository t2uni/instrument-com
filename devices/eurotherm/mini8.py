#!/usr/bin/python
""" This module offers all necessary classes to handle communication with the 
    Eurotherm 
"""
__author__ = 'Peter Gruszka'
__version__ = '1.0'

__email__ = 'gruszka@physik.uni-frankfurt.de'
__status__ = 'alpha'



try:
    from minimalmodbus import Instrument as ModbusInstrument
except:
    print 'minimalmodbus is not installed. Please install it to use it'
    import sys
    sys.exit()


class Loop(object):
    """ This class enables an easy access to a certain Loop """
    def __init__(self, instrument, baseNumber):
        """ Initializes the Loop class with an EurothermMini8 instrument and the 
            Loop number
        
        Arguments:
        instrument -- (EurothermMini8) Instrument instance which should be used
        baseNumber -- (int) Identifier of Loop, 0 <= baseNumber <= 7
        """
        self.instrument = instrument
        self.baseNumber = baseNumber

    def get_process_value(self):
        """ returns the current ProcessValue in Degrees C """
        return self.instrument.read_register(self.baseNumber + 1, 
                                             numberOfDecimals = 2, 
                                             signed = True)


    def get_target_set_point(self):
        """ returns the current TargetSetPoint """
        return self.instrument.read_register(self.baseNumber + 2, 
                                             numberOfDecimals = 2, 
                                             signed = True)

    def set_target_set_point(self, value):
        """ sets the current TargetSetPoint

            Arguments:
            value -- (float) Temperature
        """
        self.instrument.write_register(self.baseNumber + 2, value,
                                       numberOfDecimals = 2,
                                       signed = True) 

    def get_working_set_point(self):
        """ returns the current working set point """
        return self.instrument.read_register(self.baseNumber + 5,
                                             numberOfDecimals = 2,
                                             signed = True)

    def get_active_out(self):
        """ returns the current Output """
        return self.instrument.read_register(self.baseNumber + 4,
                                             numberOfDecimals = 2,
                                             signed = True)


class EurothermMini8(ModbusInstrument):
    """ An abstract layer for the Eurotherm Mini8 """
    
    # all temperature sensor registers which are available
    __temperature_registers = [4228, 4229, 4230, 4231, 4236, 4237, 4238, 4239]
    
    def __init__(self, port):
        """ inititalizes the ModbusInstrument at a certain COM-Port

            Arguments:
            port -- path to serial port, e.g. for Windows "COM1"
        """
        ModbusInstrument.__init__(self, port, 1)

    def get_temperature(self, sensor_number):
        """ returns the current Temperature of a sensor

            Arguments:
            sensor_number -- (int)  0 <= sensor_number <= 7
        """
        if sensorNumber >= 0 and sensorNumber <= 7:
            register = self.__temperature_registers[sensorNumber]
            value = self.read_register(register,
                                       numberOfDecimals=2,
                                       signed=True)
            return value
        else:
            raise Exception('sensorNumber not existent')

    def get_loop(self, loop_number):
        """ returns a Loop

            Arguments:
            loop_number -- (int)  0 <= loop_number <= 7
        """
                
        return Loop(self, loop_number * 256)


if __name__ == '__main__':
    mini8 = EurothermMini8('COM9')

    loop = mini8.get_loop(0)

    print loop.get_process_value(), 'C'
    
    loop.set_target_set_point(10.0)
    
    print loop.get_target_set_point()
    print loop.get_working_set_point()
    print loop.get_active_out()


