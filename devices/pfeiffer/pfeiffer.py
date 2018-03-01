#!/usr/bin/python
""" This module offers all necessary classes to handle communication with the
    pfeiffer TPG361 controller
"""

__author__ = 'Peter Gruszka'
__version__ = '1.0'

__email__ = 'gruszka@physik.uni-frankfurt.de'
__status__ = 'alpha'
__license__ = 'MIT'

import serial
from enum import Enum

# special characters for communication
ETC = chr(0x03)
CR = chr(0x0D)
LF = chr(0x0A)
ENQ = chr(0x05)
ACK = chr(0x06)
NAK = chr(0x15)
CRLF = CR + LF
MESSAGE_ACCEPTED = ACK + CRLF
MESSAGE_NOT_ACCEPTED = NAK + CRLF

class PressureGaugeState(Enum):
    """ This enum represents all possible gauge states """
    OKAY = 0
    UNDERRANGE = 1
    OVERRANGE = 2
    SENSOR_ERROR = 3
    GAUGE_INACTIVE = 4
    NO_GAUGE = 5
    ID_ERROR = 6

class SingleGaugeTPG361(object):
    """ Abstraction layer for the Pfeiffer Single Gauge TPG 361 controller """
    def __init__(self, path):
        """ Initialize connection parameters for futher usage

            Arguments:
            path -- (string) path to device e.g. for windows 'COM1'
                             or linux '/dev/usbtty1'
        """
        #TODO: use visa for serial connection
        self.connection = serial.Serial(path,
                                        baudrate=115200,
                                        bytesize=serial.EIGHTBITS,
                                        parity=serial.PARITY_NONE)

    def close(self):
        """ closes current connection to device """
        self.connection.close()

    def ask(self, message):
        """ ask for values

            Arguments:
            message -- (string) message to be sent

            Return:
            (string) -- Message from device
            on fail: None

        """
        conn = self.connection

        conn.write((message + CRLF).encode())
        result = conn.readline()
        if result == MESSAGE_ACCEPTED.encode():
            conn.write(ENQ.encode())
            result = conn.readline().decode('utf-8')
            return result

        if result == MESSAGE_NOT_ACCEPTED:
            return None

        return None

    def get_pressure(self, identifier=0):
        """ ask for pressure from gauge n

            Arguments:
            identifier -- (int) range 1 or 2

            Return
            (float) -- pressure in mbar
        """
        if identifier != 1 and  identifier != 2:
            return None, None

        result = self.ask('PR' + str(identifier))

        if isinstance(result, str):
            result_split = result.strip().split(',')
            state_id = int(result_split[0])
            value = float(result_split[1])
            state = PressureGaugeState(state_id)

            return state, value

        return None, None

#example
#shows the usage of the upper class
if __name__ == '__main__':
    path = '/dev/ttyUSB0'

    PFEIFFER = SingleGaugeTPG361(path)
    print(PFEIFFER.get_pressure(1))
    print(PFEIFFER.get_pressure(2))
    PFEIFFER.close()

    from time import time

    SPOT0 = time()
    PFEIFFER = SingleGaugeTPG361(path)
    N = 100

    SPOT1 = time()
    for i in range(N):
        PFEIFFER.get_pressure(1)
    SPOT2 = time()

    PFEIFFER.close()
    SPOT3 = time()

    print('load connection:', SPOT1 - SPOT0)
    print('get_pressure:', SPOT2 - SPOT1)
    print('get_pressure mean:', (SPOT2 - SPOT1) / float(N))
    print('closing connection:', SPOT3 - SPOT2)
    print('total time:', SPOT3 - SPOT0)
