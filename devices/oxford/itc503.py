#!/usr/bin/python
""" This module offers all necessary classes to handle communication with the
    oxford ITC
"""

__author__ = 'Peter Gruszka'
__version__ = '1.0'

__email__ = 'gruszka@physik.uni-frankfurt.de'
__status__ = 'alpha'
__license__ = 'MIT'

import visa
import gpib

class ITC(object):
    """ This class  offers an easy access to the temperature sensors of
        the ITC
    """
    def __init__(self, device):
        """ Initializes the ITC class. It depends on an visa device

            Arguments:
            device -- (visa.instrument) a GPIB instrument is required
        """
        self.itc = device
        self.itc.term_chars = '\r'
        # needed for error free communication
        gpib.config(self.itc.device, gpib.IbcEOSchar, ord('\r'))
        # use REOS und XEOS
        gpib.config(self.itc.device, gpib.IbcEOSrd, 0x800 | 0x400)

    def get_temperature(self, identifier):
        """
            Returns the temperature of a certain temperature sensor in the ITC

            Arguments:
            identifier -- (int) the identifier of a sensor
                                which can take the values [1,2,3]

            Return:
            (float) Temperature in Kelvin from sensor with given identifier
            if identifier is not allowed this function returns 0.0
        """

        #if identifier is not allowed return just 0
        if identifier != 1 and identifier != 2 and identifier != 3:
            return 0.0

        #get answer from itc for sensor with given identifier
        #discard first character since it is just the character 'R'
        answer = self.itc.ask('@0R' + str(identifier))[1:]

        return float(answer)

    def get_temperature1(self):
        """
            Return:
            (float) Temperature in Kelvin of sensor 1
        """
        return self.get_temperature(1)

    def get_temperature2(self):
        """
            Return:
            (float) Temperature in Kelvin of sensor 2
        """
        return self.get_temperature(2)

    def get_temperature3(self):
        """
            Return:
            (float) Temperature in Kelvin of sensor 3
        """
        return self.get_temperature(3)


# Example
if __name__ == '__main__':
    DEVICE = visa.instrument('GPIB::24')
    ITC_CONNECTION = ITC(DEVICE)

    print ITC_CONNECTION.get_temperature1(), 'K'
    print ITC_CONNECTION.get_temperature2(), 'K'
    print ITC_CONNECTION.get_temperature3(), 'K'