# LIA-SR830m Klasse
# Einfaches Interface zum SR830m Lock-In-Amplifier
# Datum: 2017-02-16
# Autor: Marc Hanefeld

import visa
import gpib
import time
import numpy as np

class SR830m(object):
    def __init__(self, device):
        self.LIA = device
        
        # Defining the extremal values for the device
        self.Vrms_AC_min = 0.004
        self.Vrms_AC_max = 5.000
        self.V_AUX_output_min = -10.5
        self.V_AUX_output_max = 10.5        
        self.frequency_min = 0.001
        self.frequency_max = 102000
        
        # Possible integration times for the Lock-In amplifier
        self.integration_times = [10E-6, 30E-6, 100E-6, 300E-6, 1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 300E-3, 1, 3, 10, 30, 100, 300, 1E3, 3E3, 10E3, 30E3]
        self.sensitivities = np.array([2E-9, 5E-9, 10E-9, 20E-9, 50E-9, 100E-9, 200E-9, 500E-9, 1E-6, 2E-6, 5E-6, 10E-6, 20E-6, 50E-6, 100E-6, 200E-6, 500E-6, 1E-3, 2E-3, 5E-3, 10E-3, 20E-3, 50E-3, 100E-3, 200E-3, 500E-3, 1])

        # self.LIA.write('*RST') # Reset the unit to its default configurations. Careful V = 1V!
        self.LIA.clear()  # Clear the local buffer for GPIB communications
        self.LIA.write("OUTX 1")  # Set the LIA to output responses to the GPIB port
        self.LIA.write('REST')  # Reset the scan. All stored data is lost.
        self.LIA.write('IGND 0')  # Set (Query) the Input Shield Grounding to Float (0) or Ground (1)
        self.LIA.write('ISRC 1')  # Set (Query) the Input Configuration to A (0), A-B (1) , I (1 MW) (2) or I (100 MW) (3)
        self.LIA.write('PHAS 0.0')  # Set (Query) the Phase Shift to x degrees.
        self.LIA.write('HARM 1')  # Set (Query) the Detection Harmonic to 1 <= i <= 19999 and i*f <= 102 kHz.
        self.set_sensitivity(1)  # Set the Sensitivity 1 V rms full scale.
        self.set_integration_time(1)  # Set (Query) the Time Constant to 1s.
        time.sleep(1)
    
    def set_voltage(self, value):
        ''' Set (Query) the Sine Output Amplitude to x Vrms. 0.004 <= x <= 5.000V. Use "save" to set the voltage to the minimum value. '''
        
        if value == "save":
            value = 0.004
            value_verified = True    
        elif self.Vrms_AC_min <= value <= self.Vrms_AC_max:
            value_verified = True
        else:
            print("Desired voltage is out of device range.")
            value_verified = False
        
        if value_verified:
            signal_str = 'SLVL ' + str(value)
            # print signal_str
            self.LIA.write(signal_str)
            
    def get_voltage(self):
        ''' Method to get the output voltage set for the device '''
        output_str = self.LIA.ask("SLVL?")
        # print output_str + " Vrms"
        return output_str
    
    def set_frequency(self, value):
        ''' Set (Query) the Reference Frequency to f Hz.Set only in Internal reference mode. 0.001 <= x <= 102000Hz. '''
                
        if self.frequency_min <= value <= self.frequency_max:
            value_verified = True
        else:
            print("Desired frequency is out of device range.")
            value_verified = False
        
        if value_verified:
            signal_str = 'FREQ ' + str(value)
            # print signal_str
            self.LIA.write(signal_str)
            
    def get_frequency(self):
        ''' Method to get the output frequency set for the device '''
        output_str = self.LIA.ask("FREQ?")
        # print output_str + " Hz"
        return output_str
        
    def set_integration_time(self, value):
        '''Set (Query) the Time Constant to 10 us through 30 ks, allowed values are: [10E-6,30E-6,100E-6,300E-6,1E-3,3E-3,10E-3,30E-3,100E-3,300E-3,1,3,10,30,100,300,1E3,3E3,10E3,30E3] 
        Caution: Time constants greater than 30s may NOT be set if theharmonic x ref. frequency (detection frequency) exceeds 200 Hz. Read manual for further information.'''
        if value in self.integration_times:
            value_verified = True
        else:
            print("Desired integration time is not an allowed value for the device.")
            value_verified = False
        
        if value_verified == True:
            entry_index = self.integration_times.index(value)
            self.LIA.write('OFLT ' + str(entry_index))
        
    def get_integration_time(self):
        ''' Method to get the integration time set for the device '''
        output_str = str(self.integration_times[int(self.LIA.ask("OFLT?"))])
        # print output_str + " s"
        return output_str
    
    def auto_adjust_sensitivity(self):
        ''' Method to use the internal sensitivity adjustment of the LIA. Careful this takes some time and may cause problems. Better use adjust_sensitivity() '''
        self.LIA.write('AGAN')
        
    def adjust_sensitivity(self):
        ''' Method to automatically adjust the sensitivity of the device to fit the measured value. Returns the new sensitivity set for the system. '''
        integration_time = self.integration_times[int(self.LIA.ask('OFLT?'))]
        
        
        while True:
            time.sleep(3 * (integration_time))  # Wait for the system to be in a steady state before adjusting the sensitivity
            sensitivity = self.LIA.ask('SENS?')
            values = self.LIA.ask("SNAP? 1,2").split(',')  # Get the values for X and Y to set the sensitivity for the higher of both
            x = abs(float(values[0]))
            y = abs(float(values[1]))
            max_value = max(x, y) * 1.1  # Determine the necessary value for the sensitivity with a 10% margin for variation
            # Compare the measured value to the list of possible sensitivities and choose the lowest one possible
            result, = np.where(max_value < self.sensitivities)
            if len(result) > 0:
                new_sensitivity = np.min(result)
            else:
                new_sensitivity = np.where(self.sensitivities == 1)[0][0]  # If the value is higher than the list the sensitivity is set to 1 V

            # Set the new sensitivity if it differs from the old one
            if int(sensitivity) != int(new_sensitivity):
                self.LIA.write('SENS ' + str(new_sensitivity))
            else:
                break
            
        return self.sensitivities[new_sensitivity]
    
    def set_sensitivity(self, value):
        '''Set (Query) the Sensitivity to 2 nV through 1 V rms full scale. Use "max" to set the sensitivity to 1 V rms. Other allowed values are:
            [2E-9, 5E-9, 10E-9, 20E-9, 50E-9, 100E-9, 200E-9, 500E-9, 1E-6, 2E-6, 5E-6, 10E-6, 20E-6, 50E-6, 100E-6, 200E-6, 500E-6, 1E-3, 2E-3, 5E-3, 10E-3, 20E-3, 50E-3, 100E-3, 200E-3, 500E-3, 1].'''
        
        if value == "save":
            value = 1
            value_verified = True
        elif value in self.sensitivities:
            value_verified = True
        else:
            print("Desired sensitivity is not an allowed value for the device.")
            value_verified = False
        
        if value_verified == True:
            entry_index = np.where(self.sensitivities == value)[0][0]
            self.LIA.write('SENS ' + str(entry_index))
                
    def get_sensitivity(self):
        ''' Method to get the sensitivity set for the device '''
        output_str = str(self.sensitivities[int(self.LIA.ask("SENS?"))])
        # print output_str + " V/uA"
        return output_str
    
    def get_measured_values(self):
        ''' Method to get sevaral output values of the device: X, Y, R, angle, frequency. Returns dictionary with these values.'''
        output_str = self.LIA.ask("SNAP? 1,2,3,4,9")
        output_list = output_str.split(",")
        #print(output_list)
        output_dict = {}
        output_dict["X"] = float(output_list[0])
        output_dict["Y"] = float(output_list[1])
        output_dict["R"] = float(output_list[2])
        output_dict["angle"] = float(output_list[3])
        output_dict["frequency"] = float(output_list[4])
        
        return output_dict
    
    def get_value_X(self):
        ''' Method to get the measured X value. '''
        output_str = float(self.LIA.ask("OUTP? 1"))
        # print output_str
        return output_str
        
        
    def get_value_Y(self): 
        ''' Method to get the measured Y value. '''
        output_str = float(self.LIA.ask("OUTP? 2"))
        # print output_str
        return output_str 
        
    def get_value_R(self):
        ''' Method to get the measured R value. '''
        output_str = float(self.LIA.ask("OUTP? 3"))
        # print output_str
        return output_str
        
    def get_value_angle(self): 
        ''' Method to get the measured angle value. '''
        output_str = float(self.LIA.ask("OUTP? 4"))
        # print output_str
        return output_str   
    
    def set_voltage_aux_output(self, value, i):
        ''' Set (Query) voltage of Aux Output i (1,2,3,4) to x Volts. -10.500 <= x <= 10.500. '''
                
        if self.V_AUX_output_min <= value <= self.V_AUX_output_max:
            value_verified = True
        else:
            print("Desired voltage is out of device range.")
            value_verified = False
        
        
        if i in [1, 2, 3, 4]:
            output_verified = True
        else:
            print("Desired output is not allowed.")
            output_verified = False
        
        
        if value_verified and output_verified:
            signal_str = 'AUXV ' + str(i) + str(value)
            # print signal_str
            self.LIA.write(signal_str)
            
    def set_input_reference_mode(self, value):
        ''' The FMOD command sets or queries the reference source. The parameter i selects internal (i=1) or external (i=0).'''
        if value in [0, 1]:
            signal_str = "FMOD " + str(value)
        else:
            "Desired reference mode is not allowed."
        
        
             
    def clean_up(self):
        '''Resets the Lock-In-Amplifier to a save state by putting the outputs to zero. '''
        
        for i in [1, 2, 3, 4]:
            self.set_voltage_aux_output(0.0, i)
        
        self.set_voltage("save")
        self.set_sensitivity("save")
        
    
        
# Beispielprogramm
# Es werden immer das visa und das HP3325B Modul benoetigt
if __name__ == '__main__':
    device = visa.instrument("GPIB::7", timeout=None)  # Lock-In Amp
    LIA = SR830m(device)
    # LIA.set_frequency(120)
    # LIA.set_voltage(10)
    # LIA.adjust_sensitivity()
    print(LIA.get_voltage())
    # print LIA.get_frequency()
    # print LIA.get_integration_time()
    LIA.clean_up()
    
