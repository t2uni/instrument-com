import io


class FlowController(object):
    def __init__(self, connection, unit_id='A'):
        self.connection = connection
        self.unit_id = unit_id
        self.init()

    def init(self):
        self.connection.baudrate = 19200
        self.connection.parity = serial.PARITY_NONE
        self.connection.stopbits = 1
        self.connection.bytesize = 8
        self.connection.timeout = 0.1

    def poll(self):
        self.connection.write('{0}\r'.format(self.unit_id).encode())
        raw_message = self.connection.readline()

        return raw_message.split(' ')

    def set(self, value):
        value = min(100, max(value, 0)) #maximal 100 sccm and minimum 0 sccm
        parameter = int( (value * 64000) / 100)
        self.connection.write('{0}{1}\r'.format(self.unit_id, parameter))
        return self.connection.readline()


if __name__ == '__main__':
    import serial
    S = serial.Serial('/dev/ttyUSB3')

    fc = FlowController(S)

    print(fc.poll())
    print(fc.set(10.0))


