#!/usr/bin/python
""" This module offers all necessary classes to handle communication with the
    HP4284A Precision LCR Meter
"""

__author__ = 'Marc Hanefeld'
__version__ = '1.0'

__email__ = 'hanefeld@physik.uni-frankfurt.de'
__status__ = 'alpha'
__license__ = 'MIT'

import visa
import gpib
import time
import numpy as np


class LCR(object):
    """ This class  offers an easy access to the different functionalities
    of the LCR Meter
    """
    def __init__(self, device):
        """ Initializes the ITC class. It depends on an visa device

            Arguments:
            device -- (visa.instrument) a GPIB instrument is required
        """
        self.__lcr = device
        self.__lcr.term_chars = '\r'
        # needed for error free communication
        gpib.config(self.itc.device, gpib.IbcEOSchar, ord('\r'))
        # use REOS und XEOS
        gpib.config(self.itc.device, gpib.IbcEOSrd, 0x800 | 0x400)


        # Setup the device to work as needed for the following functions
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.__lcr.write("FORM ASCII") # Set data output format to ASCii
        self.__lcr.write("TRIG:SOUR BUS") # Set trigger to listen only on gpib-bus
        self.__lcr.write("INIT:CONT ON") # Set the system to continuously wait for the next trigger


        # Load a list of allowed frequency vaules for the device
        self.__frequency_list = np.loadtxt('HP4284A_LCRMeter_frequency_table.par')

        # Set a list of all possible meaurement settings
        self.__measurement_ident_list = ['CPD', 'CPQ', 'CPG', 'CPRP', 'CSD', 'CSQ', 'CSRS','LPQ', 'LPD', 'LPG',
                                        'LPRP', 'LSD','LSQ', 'LSRS', 'RX', 'ZTD', 'ZTR', 'GB', 'YTD', 'YTR']

        # Set variables important for the state of the instrument
        self.high_power_mode = False
        self.__num_averages = 1 # Has to be preset, because the number averages and the integration time use one LCR-command
        self.__integration_time = 'MED'


    @property
    def frequency(self):
        ''' Method to get the frequency set for the device '''
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        frequency = self.__lcr.ask("FREQ?")
        return frequency

    @frequency.setter
    def frequency(self, frequency):
        ''' Set (Query) the measurement frequency of the device. Non-allowed frequencies are blocked. '''
        
        if frequency in self.__frequency_list:
            value_verified = True
        else:
            print "Desired frequency is not an allowed frequency for the device"
            value_verified = False

        # Communication with the instrument
        if value_verified:
            signal_str = 'FREQ ' + str(frequency)
            self.clear() # Clears the GPIB Bus to prevent problems in communication.
            self.__lcr.write(signal_str)

    

    @property
    def measurement_type(self):
        ''' Method to get the measurement type set for the device '''
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        measurement_type = self.__lcr.ask("FUNC:IMP?")
        return measurement_type

    @measurement_type.setter
    def measurement_type(self, identifier):
        ''' Set (Query) the type of measurement by one identifier.

            Arguments:
                identifier -- Which can take one of the following values:
                CPD Sets function to Cp-D
                CPQ Sets function to Cp-Q 
                CPG Sets function to Cp-G 
                CPRP Sets function to Cp-Rp
                CSD Sets function to Cs-D 
                CSQ Sets function to Cs-Q 
                CSRS Sets function to Cs-Rs 
                LSD Sets function to Ls-D
                LPRP Sets function to Lp-Rp
                LSQ Sets function to Ls-Q 
                LSRS Sets function to Ls-Rs
                LPQ Sets function to Lp-Q 
                LPD Sets function to Lp-D 
                LPG Sets function to Lp-G 
                RX Sets function to R-X
                ZTD Sets function to Z-Theta (deg)
                ZTR Sets function to Z-Theta (rad)
                GB Sets function to G-B
                YTD Sets function to Y-Theta (deg)
                YTR Sets function to Y-Theta (rad)
            '''

        if identifier in self.__measurement_ident_list:
            value_verified = True
        else:
            print "Measurement identifier is not a valid identifier. Please chose from the following list."
            print self.__measurement_ident_list
            value_verified = False

        # Communication with the instrument
        if value_verified:
            signal_str = 'FUNC:IMP ' + str(identifier)
            self.clear() # Clears the GPIB Bus to prevent problems in communication.
            self.__lcr.write(signal_str)



    @property
    def auto_range(self):
        ''' Method to get the auto-range setting for the device '''
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        auto_range = self.__lcr.ask("FUNC:IMP:RANG:AUTO?")
        return bool(auto_range)

    @auto_range.setter  
    def auto_range(self, value):
        """
            Enables or disables the Auto-Range function of the device.
                        
            Arguments:
            value -- (Bool/Int) Enables [Ture/1] or Disables [False/0] Auto-Range

        """
        
        # Check and adjust user input
        try:
            value = bool(value)
        except:
            raise ScriptSyntaxError("The Toggle Value must be 1, 0 or a Bool")


        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        if value:
            self.__lcr.write("FUNC:IMP:RANG:AUTO ON")
        else:
            self.__lcr.write("FUNC:IMP:RANG:AUTO OFF")



    @property
    def auto_level_control(self):
        ''' Method to get the auto level control setting for the device '''
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        auto_level_control = self.__lcr.ask("AMPL:ALC?")
        return bool(auto_level_control)
    
    @auto_level_control.setter
    def auto_level_control(self, value):
        """
            Enables or disables the Auto-Level-Control of the device.
                        
            Arguments:
            value -- (Bool/Int) Enables [Ture/1] or Disables [False/0] Auto-Level-Control

        """
        
        # Check and adjust user input
        try:
            value = bool(value)
        except:
            raise ScriptSyntaxError("The Toggle Value must be 1, 0 or a Bool")


        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        if value:
            self.__lcr.write("AMPL:ALC ON")
        else:
            self.__lcr.write("AMPL:ALC OFF")



    @property
    def high_power_mode(self):
        ''' Method to get the high power mode setting for the device '''

        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        high_power_mode = self.__lcr.ask("OUTP:HPOW?")
        self.__high_power_mode = bool(high_power_mode)
        return self.__high_power_mode

    @high_power_mode.setter
    def high_power_mode(self, value):
        """
            Enables or disables the High Power Mode of the device.
                        
            Arguments:
            value -- (Bool/Int) Enables [Ture/1] or Disables [False/0] High Power Mode

        """
        
        # Check and adjust user input
        try:
            value = bool(value)
        except:
            raise ScriptSyntaxError("The Toggle Value must be 1, 0 or a Bool")


        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        if value:
            self.__lcr.write("OUTP:HPOW ON")
            self.__high_power_mode = True
        else:
            self.__lcr.write("OUTP:HPOW OFF")
            self.__high_power_mode = False



    @property
    def dc_bias_status(self):
        ''' Method to get the status of a dc bias set for the device '''
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        dc_bias_status = self.__lcr.ask("BIAS:STAT?")
        return bool(dc_bias_status)

    @dc_bias_status.setter
    def dc_bias_status(self, value):
        """
            Enables or disables the usage of a bias current or voltage of the device.
                        
            Arguments:
            value -- (Bool/Int) Enables [Ture/1] or Disables [False/0] a bias current or voltage

        """
        
        # Check and adjust user input
        try:
            value = bool(value)
        except:
            raise ScriptSyntaxError("The Toggle Value must be 1, 0 or a Bool")


        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        if value:
            self.__lcr.write("BIAS:STAT ON")
        else:
            self.__lcr.write("BIAS:STAT OFF")



    @property
    def source_voltage(self):
        ''' Method to get the source oszillator voltage level set for the device '''
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        source_voltage = self.__lcr.ask("VOLT?")
        return source_voltage

    @source_voltage.setter
    def source_voltage(self, voltage):
        """
            Adjusts the source oszillator voltage level set for the device

            Arguments:
            voltage -- (float) source oszillator voltage level to be set in volts (5mV-2V/20V)

        """

        # Check and adjust user input
        try:
            voltage = float(voltage)
        except:
            raise ScriptSyntaxError("The voltage must be a float!")
        if voltage < 0.005:
            voltage = 0.005
            print "Source voltage too low, set to 5mV."
        if self.high_power_mode:
            if voltage > 20.0:
                voltage = 20.0
                print "Source voltage too high for HP-Mode, set to 20.0V."
        else:
            if voltage > 2.0:
                voltage = 2.0
                print "Source voltage too high, set to 2.0V. Switch to high power mode for voltages up to 20.0V."

        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.__lcr.write("VOLT " + str(voltage) + "V") 



    @property
    def source_current(self):
        ''' Method to get the source oszillator current level set for the device '''
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        source_current = self.__lcr.ask("CURR?")
        return source_current

    @source_current
    def source_current(self, current):
        """
            Adjusts the source oszillator current level set for the device

            Arguments:
            current -- (float) source oszillator current level to be set in mil__lcrmpere (0.05mA-20mA/200mA)

        """

        # Check and adjust user input
        try:
            current = float(current)
        except:
            raise ScriptSyntaxError("The current must be a float!")
        if current < 0.05:
            current = 0.05
            print "Source current too low, set to 0.05mA."
        if self.high_power_mode:
            if current > 200.0:
                current = 200.0
                print "Source current too high for HP-Mode, set to 200.0mA."
        else:
            if current > 20.0:
                current = 20.0
                print "Source current too high, set to 20.0mA. Switch to high power mode for currents up to 200.0mA."

        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.__lcr.write("CURR " + str(current) + "MA") 



    @property
    def dc_bias_voltage(self):
        ''' Method to get the voltage of a dc bias set for the device '''
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        dc_bias_voltage = self.__lcr.ask("BIAS:VOLT?")
        return dc_bias_voltage

    @dc_bias_voltage.setter
    def bias_voltage(self, voltage):
        """
            Adjusts the bias voltage set for the device

            Arguments:
            voltage -- (float) bias voltage to be set in volts  (0V-2V/40V)

        """

        # Check and adjust user input
        try:
            voltage = float(voltage)
        except:
            raise ScriptSyntaxError("The voltage must be a float!")
        if voltage < 0.0:
            voltage = 0.0
            print "Bias voltage too low, set to 0V."
        if self.high_power_mode:
            if voltage > 40.0:
                voltage = 40.0
                print "Bias voltage too high for HP-Mode, set to 40.0V."
        else:
            if voltage > 2.0:
                voltage = 2.0
                print "Bias voltage too high, set to 2.0V. Switch to high power mode for voltages up to 40.0V."

        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.__lcr.write("BIAS:VOLT " + str(voltage) + "V")  



    @property
    def dc_bias_current(self):
        ''' Method to get the current of a dc bias set for the device '''
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        dc_bias_current = self.__lcr.ask("BIAS:CURR?")
        return dc_bias_current

    @dc_bias_current.setter
    def bias_current(self, current):
        """
            Adjusts the bias current set for the device

            Arguments:
            current -- (float) bias current to be set in ampere  (0mA-100mA)

        """

        # Check and adjust user input
        try:
            current = float(current)
        except:
            raise ScriptSyntaxError("The current must be a float!")
        if current < 0.0:
            current = 0.0
            print "Bias current too low, set to 0mA."
        if self.high_power_mode:
            if current > 100.0:
                current = 100.0
                print "Bias current too high for HP-Mode, set to 100.0mA."
        else:
            print "Bias current not available for normal mode, use high-power mode instead."

        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.__lcr.write("BIAS:CURR " + str(current) + "MA")



    @property
    def integration_time(self):
        ''' Method to get integration time set for the device '''

        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        integration_time = self.__lcr.ask("APER?")
        return integration_time.split(',')[0]

    @integration_time.setter
    def integration_time(self, identifier):
        ''' Set (Query) the integration time to a value or use an identifier.

            Arguments:
                identifier -- Which can take one of the following values:
                SHOR - Short integration time
                MED  - Medium integration time
                LONG - Long Integration time
            '''

        if identifier in ['SHOR', 'MED', 'LONG']:
            value_verified = True
        else:
            print "Identifier is not a valid identifier. Please chose from 'SHOR', 'MED' and 'LONG'."
            value_verified = False

        # Communication with the instrument
        if value_verified:
            signal_str = 'APER ' + str(identifier) + ',' + str(self.__num_averages)
            self.clear() # Clears the GPIB Bus to prevent problems in communication.
            self.__lcr.write(signal_str)



    @property
    def num_averages(self):
        ''' Method to get the number measurements that should be averaged for one data point set for the device '''

        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        num_averages = self.__lcr.ask("APER?")
        return num_averages.split(',')[1]

    @num_averages.setter
    def num_averages(self, value):
        ''' Set (Query) the integration time to a value or use an identifier.

            Arguments:
                value -- (int) a number between 1 and 128 for the averaging rate
            '''

        try:
            value = int(value)
        except:
            raise ScriptSyntaxError("The valuee must be an integer!")
        if value < 1:
            value = 1
            print "Number of averages to low, set to 1."
        if value > 128:
            value = 128
            print "Number of averages to high, set to 128."

        # Communication with the instrument
        signal_str = 'APER ' + str(self.integration_time) + ',' + str(value)
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.__lcr.write(signal_str)



    def read_data(self):
        ''' 
        Method to get the measuement data from the device. The *TRG command (trigger command) performs the same function as the Group Execute Trigger. This command moves the primary and secondary parameter measurement data into the HP 4284A's output buffer. '''

        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        data = self.__lcr.ask("*TRG")
        value1 = float(data.split(',')[0])
        value2 = float(data.split(',')[1])
        return value1, value2

    def clear(self):
            """
                Clears the GPIB Bus to prevent problems in communication.

            """
            time.sleep(0.1)
            self.__lcr.clear()
            time.sleep(0.1)

# Example
if __name__ == '__main__':
    DEVICE = visa.instrument('GPIB::4')
    lcr = LCR(DEVICE)

    print lcr.frequency