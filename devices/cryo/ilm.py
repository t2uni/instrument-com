#!/usr/bin/python
""" This module offers all necessary classes to handle communication with the 
    oxford ILM  
"""

__author__ = 'Peter Gruszka'
__version__ = '1.0'

__email__ = 'gruszka@physik.uni-frankfurt.de'
__status__ = 'alpha'
__license__ = 'MIT'

import visa
import gpib

class ILM(object):
    """ This class offers an easy access to the ILM """
    def __init__(self, device):
        """ Initializes the ILM class. It depends on an visa device

            Arguments:
            device -- (visa.instrument) a GPIB instrument is required
        """
        self.ilm = device
        self.ilm.term_chars = '\r'
        gpib.config(self.ilm.device, gpib.IbcEOSchar, ord('\r'))
        # use REOS und XEOS
        gpib.config(self.ilm.device, gpib.IbcEOSrd, 0x800 | 0x400)

    def get_level(self):
        """ 
            Returns the current He4 level of the cryostat in percent 
            
            Return: 
            (float) He4 level in percent
        """
        # ask ilm and discard first character since this is a 'R'
        # ILM has 6 as internal address 
        level_string = self.ilm.ask('@6R1')[1:]

        return float(level_string) / 10.0


# example usage of the ILM class
if __name__ == '__main__':
    device = visa.instrument('GPIB::24')
    ilm = ILM(device)

    print ilm.getLevel(), '%'
