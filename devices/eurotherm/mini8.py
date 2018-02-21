#!/usr/bin/python
""" This module offers all necessary classes to handle communication with the
    Eurotherm
"""
__author__ = 'Peter Gruszka'
__version__ = '1.0'

__email__ = 'gruszka@physik.uni-frankfurt.de'
__status__ = 'alpha'
__license__ = 'MIT'



try:
    from minimalmodbus import Instrument as ModbusInstrument
except ImportError as import_error:
    print('minimalmodbus is not installed. Please install it to use it')
    import sys
    sys.exit()

from threading import Lock
import sys
from datetime import datetime
import time

class Loop(object):
    """ This class enables an easy access to a certain Loop """
    def __init__(self, instrument, baseNumber, lock):
        """ Initializes the Loop class with an EurothermMini8 instrument and the
            Loop number

        Arguments:
        instrument -- (EurothermMini8) Instrument instance which should be used
        base_number -- (int) Identifier of Loop, 0 <= base_number <= 7
        """
        self.instrument = instrument
        self.base_number = baseNumber
        self.lock = lock

        self.tsp = 0
        self.pv = 0
        self.wsp = 0
        self.ao = 0
        self.tspr = 0

        self.last_time = time.time() - 1
        self.__get_all()



    def __allowed_to_get_new_data(self):
        return (time.time() - self.last_time > 0.5)

    def __get_all(self):
        if not self.__allowed_to_get_new_data():
            return 

        self.lock.acquire()
        self.last_time = time.time()

        try:
            data = self.instrument.read_registers(self.base_number + 1, 5)
            tspr = self.instrument.read_register(self.base_number + 70, 1)
        except:
            with open('temperature.log', 'a') as fh:
                fh.write('{} Unexpected error: {}\n'.format(
                        datetime.now().isoformat(), sys.exc_info()[0]))
            return
        finally:
            self.lock.release()

        self.pv = data[0] / 10.0
        self.tsp = data[1] / 10.0
        self.ao = data[3] / 10.0
        self.wsp = data[4] / 10.0
        self.tspr = tspr

    def get_process_value(self):
        """ returns the current ProcessValue in Degrees C """
        self.__get_all()
        return self.pv


    def get_target_set_point(self):
        """ returns the current TargetSetPoint """
        self.__get_all()
        return self.tsp

    def set_target_set_point(self, value):
        """ sets the current TargetSetPoint

            Arguments:
            value -- (float) Temperature
        """
        self.lock.acquire()
        try:
            fh = open('test.dat', 'w')
            fh.write('sonmething')
            fh.close()
            self.instrument.write_register(self.base_number + 2, value, 1)
        except:
            return -1
        finally:
            self.lock.release()
        
        return 1

    def get_working_set_point(self):
        """ returns the current working set point """
        self.__get_all()
        return self.wsp

    def get_active_out(self):
        """ returns the current Output """
        self.__get_all()
        return self.ao


    def get_set_point_rate(self):
        """ returns the current set point rate """
        self.__get_all()
        return self.tspr


    def set_set_point_rate(self, value):
        self.lock.acquire()
        try:
            self.instrument.write_register(self.base_number + 70,
                                            value, 
                                            numberOfDecimals=1,
                                            signed=False)
        except:
            return -1
        finally:
            self.lock.release()
        return 1

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
        self.lock = Lock()
        self.
        self.loops = []

        for i in range(0, 8):
            self.loops.append(Loop(self, i * 256, self.lock))



    def get_temperature(self, sensor_number):
        """ returns the current Temperature of a sensor

            Arguments:
            sensor_number -- (int)  0 <= sensor_number <= 7
        """

        if sensor_number < 0 or sensor_number > 7:
            raise Exception('sensorNumber not existent')

        self.lock.acquire()
        register = self.__temperature_registers[sensor_number]
        value = self.read_register(register,
                                   numberOfDecimals=2,
                                   signed=True)
        self.lock.release()
        
        return value

    def get_loop(self, loop_number):
        """ returns a Loop

            Arguments:
            loop_number -- (int)  0 <= loop_number <= 7
        """
        
        return self.loops[loop_number]

if __name__ == '__main__':
    MINI8 = EurothermMini8('/dev/ttyUSB5')

    for i in range(8):
        LOOP = MINI8.get_loop(i)
        temperature = LOOP.get_process_value()
        targetSP = LOOP.get_target_set_point()
        workingSP = LOOP.get_working_set_point()
        active_out = LOOP.get_active_out()
        print('{0}) {1}C (TSP: {2}, WSP: {3}, OUT: {4}%)'.format(i, temperature, targetSP, workingSP, active_out))
        

