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


      	self.clear() # Clears the GPIB Bus to prevent problems in communication.


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


    def set_temperature_set_point(self, temperature):
        """
            Adjusts the temperature set point of the device

            Arguments:
            temperature -- (float) temperature to be set as a set point

            Return:
            Message that the temperature has been set sucessfully.
        """


    	# Check and adjust user input
    	try:
            temperature = float(temperature)
        except:
            raise ScriptSyntaxError("The temperature must be a float!")
        if temperature < 0:
            temperature = 0
            print "Temperature too low, set to 0K."
        if temperature > 299:
            temperature = 299
            print "Temperature too high, set to 299K."

        # Communication with the instrument
        self.itc.write("@0C3")	# remote & unlocked		
        self.itc.write("@0S0")	# stop possibly existing sweep
        self.itc.write("@0T" + str(temperature)[:5])	# set Temperature-set-point with a maximum of 5 digits
        self.itc.write("@0C0")			# local & locked


    def set_temperature_sweep(self, temperature, sweep_time = 0, hold_time = 1399):
        """
            Adjusts the settings of a temperature sweep of the device.

            Arguments:
            temperature -- (float) temperature to be set as sweep goal
            sweep_time -- (float) total time for the sweep
            hold_time -- (float) time the temperature should be held, once reached

            Return:
            Message that the sweep parameters have been set sucessfully.
        """
			
        # Check and adjust user input
        try:
            temperature = float(temperature)
        except:
            raise ScriptSyntaxError("The temperature must be a float!")
        if temperature < 0:
            temperature = 0
            print "Temperature too low, set to 0K."
        if temperature > 299:
            temperature = 299
            print "Temperature too high, set to 299K."
        try:
            sweep_time = float(sweep_time)
        except:
            raise ScriptSyntaxError("The sweep time entered must be a float")
        if sweep_time < 0:
            sweep_time = 0
            print "The sweep time entered is too low, set to 0 min."
        if sweep_time > 1399:
            sweep_time = 1399 # Set sweep time to maximum value.
            print "The sweep time entered is too high, set to 1399 min."
        try:
            hold_time = float(hold_time)
        except:
            raise ScriptSyntaxError("The hold time entered must be a float")
        if hold_time < 0:
            hold_time = 0
            print "The hold time entered is too low, set to 0 min."
        if hold_time > 1399:
            hold_time = 1399 # Set hold time to maximum value.
            print "The hold time entered is too high, set to 1399 min."

        # Communication with the insrument
        self.itc.write("@0C3")	# device set to state "remote & unlocked"	
        self.itc.write("@0S0")	# stop possibly existing sweep

        if sweep_time == 0:
            self.itc.write("@0T" + str(temperature)[:5])	# set Temperature-set-point with a maximum of 5 digits
        else:
            self.itc.write("@0x001")		# Adjust sweep-step no. 1 of the sweep table
            self.itc.write("@0y001")		# Choose to adjust step temperature
            self.itc.write("@0s" + str(temperature)[:5])	# Set step temperature
            self.itc.write("@0y002")		# Choose to adjust sweep time
            self.itc.write("@0s" + str(sweep_time)[:5])	# Set sweep time
            self.itc.write("@0y003")		# Choose to adjust hold time
            self.itc.write("@0s" + str(hold_time)[:5])	# Set hold time
            self.itc.write("@0x000")		# Good practice according to manual
            self.itc.write("@0y000")		# Good practice according to manual
        
        self.itc.write("@0C0")			# device set to state "local & locked"

        
    def start_temperature_sweep(self):
        """
            Starts a temperature sweep.

            Return:
            Message that the sweep is running.
        """
        # Communication with the instrument
        self.itc.write("@0C3")	# remote & unlocked		
        self.itc.write("@0S0")	# stop possibly existing sweep
        self.itc.write("@0S1")	# start sweep		
        self.itc.write("@0C0")	# local & locked



    def clear(self):
        """
        Clears the GPIB Bus to prevent problems in communication.

        """
        self.itc.clear()

# Example
if __name__ == '__main__':
    DEVICE = visa.instrument('GPIB::24')
    ITC_CONNECTION = ITC(DEVICE)

    print ITC_CONNECTION.get_temperature1(), 'K'
    print ITC_CONNECTION.get_temperature2(), 'K'
    print ITC_CONNECTION.get_temperature3(), 'K'
    
    print ITC_CONNECTION.set_temperature_sweep(300, 10)
    print ITC_CONNECTION.start_temperature_sweep()
