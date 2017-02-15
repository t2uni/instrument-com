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

    def get_temperature(self, id):
        """
            Returns the temperature of a certain temperature sensor in the ITC

            Arguments:
            id -- (int) the id of a sensor which can take the values [1,2,3]

            Return:
            (float) Temperature in Kelvin from sensor with given id
            if id is not allowed this function returns 0.0
        """

        #if id is not allowed return just 0
        if id != 1 and id != 2 and id != 3:
            return 0.0

        #get answer from itc for sensor with given id
        #discard first character since it is just the character 'R'
        answer = self.itc.ask('@0R' + str(id))[1:]

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
    device = visa.instrument('GPIB::24')
    itc = ITC(device)

    print itc.get_temperature1(), 'K'
    print itc.get_temperature2(), 'K'
    print itc.get_temperature3(), 'K'
