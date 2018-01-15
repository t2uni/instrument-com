import io

class FlowControllerResult(object):
    def __init__(self, message):
        self.__empty()
        split = message.split(' ')

        if len(split) > 5:
            self.__init(split)

    def __init(self, split):
        self.pressure = 70.0 * float(split[1]) #umrechnung von psia in mbar
        self.temperature = float(split[2])
        self.volflow = float(split[3])
        self.massflow = float(split[4])
        self.setpoint = float(split[5])

    def __empty(self):
        self.pressure = 0
        self.temperature = 0
        self.volflow = 0
        self.massflow = 0
        self.setpoint = 0

    def __repr__(self):
        return 'Pressure: {0}\nTemperature: {1}\nVolume Flow: {2}\nMass Flow: {3}\nSet Point: {4}\n'.format(self.pressure, self.temperature, self.volflow, self.massflow, self.setpoint)

class FlowController(object):
    def __init__(self, connection, unit_id='A'):
        self.connection = connection
        self.unit_id = unit_id
        self.__init()

    def __init(self):
        self.connection.baudrate = 19200
        self.connection.parity = serial.PARITY_NONE
        self.connection.stopbits = 1
        self.connection.bytesize = 8
        self.connection.timeout = 0.1

    def poll(self):
        self.connection.write('{0}\r'.format(self.unit_id).encode())
        raw_message = self.connection.readline()

        return FlowControllerResult(raw_message)

    def set(self, value):
        parameter = self.__calculate_parameter(value)

        self.connection.write('{0}{1}\r'.format(self.unit_id, parameter))
        raw_message = self.connection.readline()

        return FlowControllerResult(raw_message)

    def off(self):
        return self.set(0.0)

    def __calculate_parameter(self, value):
        value = min(100, max(value, 0)) #maximal 100 sccm and minimum 0 sccm
        return  int((value * 64000) / 100)

if __name__ == '__main__':
    
    import sys

    flow = 0
    if len(sys.argv) == 2:
        flow = float(sys.argv[1])

    import serial
    S = serial.Serial('/dev/ttyUSB3')

    fc = FlowController(S)

    print(fc.poll())
    print(fc.set(flow))
    fc.off()


