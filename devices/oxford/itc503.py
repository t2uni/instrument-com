#!/usr/bin/python
""" This module offers all necessary classes to handle communication with the
    oxford ITC
"""

__author__ = 'Peter Gruszka, Marc Hanefeld'
__version__ = '1.0'

__email__ = 'gruszka@physik.uni-frankfurt.de'
__status__ = 'alpha'
__license__ = 'MIT'

import visa
import gpib
import time

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

    @property
    def T1(self):
        """
            Return:
            (float) Temperature in Kelvin of sensor 1
        """
        return self.__get_temperature(1)

    @property
    def T2(self):
        """
            Return:
            (float) Temperature in Kelvin of sensor 2
        """
        return self.__get_temperature(2)

    @property
    def T3(self):
        """
            Return:
            (float) Temperature in Kelvin of sensor 3
        """
        return self.__get_temperature(3)


    @property
    def temperature_set_point(self):
        """
            Return current temperature_set_point

            Return:
            temperature_set_point -- (float)
        """

        # Communication witht the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        temperature_set_point = float(self.itc.ask('@0R0')[1:])

        return temperature_set_point

    @temperature_set_point.setter
    def temperature_set_point(self, temperature):
        """
            Adjusts the temperature set point of the device

            Arguments:
            temperature -- (float) temperature to be set as a set point

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
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.itc.write("@0C3")  # remote & unlocked     
        self.itc.write("@0S0")  # stop possibly existing sweep
        self.itc.write("@0T" + str(temperature)[:5])    # set Temperature-set-point with a maximum of 5 digits
        self.itc.write("@0C0")          # local & locked


    @property
    def pid_parameters(self):
        """
            Return current PID_parameters of the System

            Return:
            proportional -- (float) proportional band in K
            integral -- (float) integral action time in min
            derivative -- (float) derivative action time in min
        """

        # Communication witht the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        proportional = float(self.itc.ask('@0R8')[1:])
        integral = float(self.itc.ask('@0R9')[1:])
        derivative = float(self.itc.ask('@0R10')[1:])

        return proportional, integral, derivative

    @pid_parameters.setter
    def pid_parameters(self, pid_list):
        """
            Adjusts the settings of the PID-Parameters of the device.

            Arguments:
            pid_list -- [proportional, integral, derivative]
            proportional -- (float) Value for the proportional band of the PID Parameters (0-300 K)
            integral -- (float) Value for the integral action time of the PID Parameters ( 0-140 min)
            derivative -- (float) Value for the derivative action time of the PID Parameters ( 0-273 min)

        """
        proportional, integral, derivative = pid_list    
        # Check and adjust user input
        try:
            proportional = float(proportional)
        except:
            raise ScriptSyntaxError("The proportional value must be a float!")
        if proportional < 0:
            proportional = 0
            print "Proportional value too low, set to 0."
        if proportional > 300:
            proportional = 300
            print "Proportional value too high, set to 300K."
        try:
            integral = float(integral)
        except:
            raise ScriptSyntaxError("The integral value entered must be a float")
        if integral < 0:
            integral = 0
            print "The integral value entered is too low, set to 0 min."
        if integral > 140.0:
            integral = 140.0 # Set integral time to maximum value 140.0 min.
            print "The  integral value entered is too high, set to 140 min."
        try:
            derivative = float(derivative)
        except:
            raise ScriptSyntaxError("The derivative value entered must be a float")
        if derivative < 0:
            derivative = 0
            print "The derivative value entered is too low, set to 0 min."
        if derivative > 273.0:
            derivative = 273.0 # Set derivatie value to maximum value 273 min.
            print "The derivative value entered is too high, set to 273 min."


        # Communication with the instrument 
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.toggle_pid_auto(False) # Stop automatic PID Control
        self.itc.write("@0C3")  # remote & unlocked     
        self.itc.write("@0P" + str(proportional)[:5])   # Set proportional value
        self.itc.write("@0I" + str(integral)[:5])   # Set proportional value
        self.itc.write("@0D" + str(derivative)[:5]) # Set proportional value
        self.itc.write("@0C0")  # local & locked


    @property
    def heater_output(self):
        """
            Return current heater output setting of the System

            Return: 
            heater_output_percentage -- (float) current heater output in %
            herter_output_volts -- (float) current heater output in Volts
        """

        # Communication witht the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        heater_output_percentage = float(self.itc.ask('@0R5')[2:])
        heater_output_volts = float(self.itc.ask('@0R6')[2:])

        return heater_output_percentage, heater_output_volts

    @heater_output.setter
    def heater_output(self, value):
        """
            Sets the heater output valve setting of the device
                        
            Arguments:
            value -- (float) Heater Output in percent of the maximum heater value

        """
        
        # Check and adjust user input
        try:
            heater_output = float(value)
        except:
            raise ScriptSyntaxError("The Heater Output value must be a float")
        if heater_output < 0:
            heater_output = 0
            print "Heater Output value too low, set to 0%."
        if heater_output > 100:
            heater_output = 100
            print "Heater Output value too high, set to 100%."


        # Communication with the instrument
        self.itc.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.itc.write("@0C3")  # remote & unlocked 
        self.itc.write("@0O" + str(heater_output * 10)[0:4]) # Set the heater_output to desired value, requirements: 3 digit with 0.1% resolution
        self.itc.write("@0C0")  # local & locked


    @property
    def gas_flow(self):
        """
            Return current gas flow setting of the System

            Return: gas_flow -- (float) current needle valve opening in %
        """
        
        # Communication witht the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        gas_flow = float(self.itc.ask('@0R7')[2:])

        return gas_flow

    @gas_flow.setter
    def gas_flow(self, value):
        """
            Sets the gas flow/needle valve setting of the device
                        
            Arguments:
            value -- (float) Gas flow value in % with a resolution of 0.1%

        """
        
        # Check and adjust user input
        try:
            gas_flow = float(value)
        except:
            raise ScriptSyntaxError("The Gas-Flow value must be a float")
        if gas_flow < 0:
            gas_flow = 0
            print "Gas-Flow value too low, set to 0%."
        if gas_flow > 100:
            gas_flow = 100
            print "Gas-Flow value too high, set to 100%."


        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.itc.write("@0C3")  # remote & unlocked 
        self.itc.write("@0G" + str(gas_flow)[0:4]) # Set the gasflow to desired value, requirements: 3 digit with 0.1% resolution
        self.itc.write("@0C0")  # local & locked     


    @property
    def device_status(self):
        """
            Returns the current settings and status of the ITC

            Return:
            (dictionary of integers/boolean) The returned Dictionary contains information about the system status:
                    "heater_auto": Heater set to automatic control
                    "gas_flow_auto": Gas-Flow set to automatic control
                    "system_remote": System is to be controlled remotely
                    "system_locked": System is locked to any input
                    "sweep_running": A sweep is currently running
                    "sweep_holding": Sweep finished, holding final temperature
                    "heater_sensor_used": Heater sensor used to control Temperature
                    "auto_pid": PID-Parameters chosen automatically from internal list
        """

        # Communication with the instrument
        heater_output_percentage, heater_output_volts = self.heater_output()
        gas_flow = self.gas_flow()  
        temperature_set_point = self.temperature_set_point()
        pid_proportional, pid_integral, pid_derivative = self.pid_parameters()
        self.clear() # Clears the GPIB Bus to prevent problems in communication.pyth
        status = self.itc.ask("@0X")    # stop existing sweep

        # Device output Sequence:   XnAnCnSnnHn L n
        #                           0123456789101112


        # Examine Heater and Gas-Flow settings
        if int(status[3]) == 0:
            heater_auto = 0
            gas_flow_auto = 0
        elif int(status[3]) == 1:
            heater_auto = 1
            gas_flow_auto = 0
        elif int(status[3]) == 2:
            heater_auto = 0
            gas_flow_auto = 1
        elif int(status[3]) == 3:
            heater_auto = 1
            gas_flow_auto = 1

        # Examine System LOC/REM/LOCK-Status
        if int(status[5]) == 0:
            system_remote = 0
            system_locked = 1
        elif int(status[5]) == 1:
            system_remote = 1
            system_locked = 1
        elif int(status[5]) == 2:
            system_remote = 0
            system_locked = 0
        elif int(status[5]) == 3:
            system_remote = 1
            system_locked = 0

        # Examine System Sweep-Stautus for Sweep Table 1
        if int(status[7:9]) == 0:
            sweep_running = 0 # No sweep running
            sweep_holding = 0
        elif int(status[7:9]) == 1:
            sweep_running = 1 # Sweeping to Sweep Point 1
            sweep_holding = 0
        elif int(status[7:9]) == 2:
            sweep_running = 0 # Sweep finished holding temperature
            sweep_holding = 1

        # Examine which Heat Sensor is used for Heater Control
        if int(status[10]) == 1:
            heater_sensor_used = 1
        elif int(status[10]) == 2:
            heater_sensor_used = 2
        elif int(status[10]) == 3:
            heater_sensor_used = 3

        # Examine Auto-PID Status
        if int(status[12]) == 0:
            auto_pid = 0
        elif int(status[12]) == 1:
            auto_pid = 1


        status_dic = {
                    "temperature_set_point": temperature_set_point,
                    "sweep_running": sweep_running,
                    "sweep_holding": sweep_holding,
                    "heater_sensor_used": heater_sensor_used,
                    "heater_auto": heater_auto,
                    "heater_output_percentage": heater_output_percentage,
                    "heater_output_volts": heater_output_volts,
                    "gas_flow_auto": gas_flow_auto,
                    "gas_flow" : gas_flow,
                    "system_remote": system_remote,
                    "system_locked": system_locked,
                    "pid_proportional": pid_proportional,
                    "pid_integral": pid_integral,
                    "pid_derivative": pid_derivative,
                    "auto_pid": auto_pid
                    }

        return status_dic


    def __get_temperature(self, identifier):
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

    def set_temperature_sweep(self, temperature, sweep_time = 0, hold_time = 1399):
        """
            Adjusts the settings of a temperature sweep of the device.

            Arguments:
            temperature -- (float) temperature to be set as sweep goal
            sweep_time -- (float) total time for the sweep
            hold_time -- (float) time the temperature should be held, once reached

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
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.itc.write("@0C3")  # device set to state "remote & unlocked"   
        self.itc.write("@0S0")  # stop possibly existing sweep

        if sweep_time == 0:
            self.itc.write("@0T" + str(temperature)[:5])    # set Temperature-set-point with a maximum of 5 digits
        else:
            self.itc.write("@0x001")        # Adjust sweep-step no. 1 of the sweep table
            self.itc.write("@0y001")        # Choose to adjust step temperature
            self.itc.write("@0s" + str(temperature)[:5])    # Set step temperature
            self.itc.write("@0y002")        # Choose to adjust sweep time
            self.itc.write("@0s" + str(sweep_time)[:5]) # Set sweep time
            self.itc.write("@0y003")        # Choose to adjust hold time
            self.itc.write("@0s" + str(hold_time)[:5])  # Set hold time
            self.itc.write("@0x000")        # Good practice according to manual
            self.itc.write("@0y000")        # Good practice according to manual
        
        self.itc.write("@0C0")          # device set to state "local & locked"
 
    def start_temperature_sweep(self):
        """
            Starts a temperature sweep.

        """
        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.itc.write("@0C3")  # remote & unlocked     
        self.itc.write("@0S0")  # stop possibly existing sweep
        self.itc.write("@0S1")  # start sweep       
        self.itc.write("@0C0")  # local & locked
     
    def stop_temperature_sweep(self):
        """
            Stops an existing temperature sweep.

        """
        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.itc.write("@0C3")  # remote & unlocked     
        self.itc.write("@0S0")  # stop existing sweep
        self.itc.write("@0C0")  # local & locked



    def toggle_pid_auto(self, value):
        """
            Enables or disables the Auto-PID button according to user input
                        
            Arguments:
            value -- (Bool/Int) Enables [Ture/1] or Disables [False/0] Auto-PID

        """
        
        # Check and adjust user input
        try:
            value = bool(value)
        except:
            raise ScriptSyntaxError("The Toggle Value must be 1, 0 or a Bool")


        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.itc.write("@0C3")  # remote & unlocked 
        if value:
            self.itc.write("@0L1")  # Use Auto-PID
        else:
            self.itc.write("@0L0")  # Disables use of Auto-PID

        self.itc.write("@0C0")  # local & locked

    def toggle_gas_flow_auto(self, value):
        """
            Enables or disables the Auto-Gas-Flow button according to user input
                        
            Arguments:
            value -- (Bool/Int) Enables [Ture/1] or Disables [False/0] Auto-Gas-Flow

        """
        
        # Check and adjust user input
        try:
            value = bool(value)
        except:
            raise ScriptSyntaxError("The Toggle Value must be 1, 0 or a Bool")


        heater_auto_state = self.device_status["heater_auto"]


        # Control sequence for device according to system status, since heater and gas_flow auto are coupled
        if value:
            if heater_auto_state == 0:
                send_string = "A2"
            else:
                send_string = "A3"
        else:
            if heater_auto_state == 0:
                send_string = "A0"
            else:
                send_string = "A1"



        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.itc.write("@0C3")  # remote & unlocked 
        self.itc.write("@0" + send_string) # Set Auto Gas-Flow according to users preference
        self.itc.write("@0C0")  # local & locked

    def toggle_heater_auto(self, value):
        """
            Enables or disables the Auto-Heater button according to user input
                        
            Arguments:
            value -- (Bool/Int) Enables [Ture/1] or Disables [False/0] Auto-Heater

        """
        
        # Check and adjust user input
        try:
            value = bool(value)
        except:
            raise ScriptSyntaxError("The Toggle Value must be 1, 0 or a Bool")


        gas_flow_auto_state = self.device_status["gas_flow_auto"]


        # Control sequence for device according to system status, since heater and gas_flow auto are coupled
        if value:
            if gas_flow_state == 0:
                send_string = "A1"
            else:
                send_string = "A3"
        else:
            if gas_flow_state == 0:
                send_string = "A0"
            else:
                send_string = "A2"



        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.itc.write("@0C3")  # remote & unlocked 
        self.itc.write("@0" + send_string) # Set Auto Heater according to users preference
        self.itc.write("@0C0")  # local & locked


    def set_heater_sensor_used(self, identifier):
        """
            Sets the heater and temperature sensor used for temperature control.
            In the special case of the ITC503 the setting 3 uses the temperature
            sensor 3 but still controls the VTI heater (1)

            Arguments:
            identifier -- (int) the identifier of the sensor heater:#
                                1 - VTI Temperature Senor and Heater
                                2 - Sample Probe T-Sensor and Heater
                                3 - Sample Mounting Position T-Sensor and VTI Heater

        """

        # Check and adjust user input
        try:
            identifier = int(identifier)
        except:
            raise ScriptSyntaxError("The Heater Output value must be an integer (1,2 or 3)")
        if identifier != 1 and identifier != 2 and identifier != 3:
            raise ScriptSyntaxError("The Heater Output value must be 1,2 or 3")

        # Communication with the instrument
        self.clear() # Clears the GPIB Bus to prevent problems in communication.
        self.itc.write("@0C3")  # remote & unlocked 
        self.itc.write("@0H" + str(identifier)) # Set heater sensor used for temperature control
        self.itc.write("@0C0")  # local & locked

        return float(answer)


    def clear(self):
        """
            Clears the GPIB Bus to prevent problems in communication.

        """
        time.sleep(0.1)
        self.itc.clear()
        time.sleep(0.1)


# Example
if __name__ == '__main__':
    DEVICE = visa.instrument('GPIB::24')
    ITC_CONNECTION = ITC(DEVICE)

    print ITC_CONNECTION.T1, 'K'
    print ITC_CONNECTION.T2, 'K'
    print ITC_CONNECTION.T3, 'K'
    
    #ITC_CONNECTION.set_pid_parameters(5.0, 2.7, 0)
    #print ITC_CONNECTION.get_device_status()
    #ITC_CONNECTION.toggle_auto_pid(0)
    
    #print ITC_CONNECTION.set_temperature_sweep(2, 5)
    #print ITC_CONNECTION.start_temperature_sweep()
