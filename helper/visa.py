"""emulation of visa-library to access gpib-,serial- and network-devices
written in 2015 by Peter Gruszka for He3-Cryo
"""

__author__ = 'Peter Gruszka'
__version__ = '1.0'

__email__ = 'gruszka@physik.uni-frankfurt.de'
__status__ = 'alpha'
__license__ = 'MIT'


print "--- no visa-library installed ---"
print "--- using linux-gpib,PySerial,socket and minimalmodbus library ---"

import socket
import gpib
import serial

class GenericInstrument(object):
    """ This is an abstract class for a generic instrument """
    def __init__(self):
        """ Initialises the generic instrument """
        self.term_chars = '\n'

    def ask(self, query):
        """ ask will write a request and waits for an answer

            Arguments:
            query -- (string) the query which shall be sent

            Result:
            (string) -- answer from device
        """
        self.write(query)
        return self.read()

    def write(self, query):
        """ writes a query to remote device

            Arguments:
            query -- (string) the query which shall be sent
        """
        pass

    def read(self):
        """ reads a message from remote device

            Result:
            (string) -- message from remote device
        """
        pass

    def close(self):
        """ closes connection to remote device """
        pass

class EthernetInstrument(GenericInstrument):
    """ Implementation of GenericInstrument to communicate with ethernet devices """
    def __init__(self, connection):
        """ initializes connection to ethernet device

            Arguments:
            connection - (socket) a socket object to speak to
        """
        GenericInstrument.__init__(self)
        self.connection = connection
        self.term_chars = '\n'

    def write(self, query):
        """ writes a query to remote device

            Arguments:
            query -- (string) the query which shall be sent
        """
        self.connection.sendall(query + self.term_chars)

    def read(self):
        """ reads a message from remote device

            Result:
            (string) -- message from remote device
        """
        return self.connection.recv(512).rstrip()

    def close(self):
        """ closes connection to remote device """
        self.connection.close()

class GpibInstrument(GenericInstrument):
    """ Implementation of GenericInstrument to communicate with gpib devices """
    def __init__(self, device):
        """ initializes connection to gpib device

            Arguments:
            connection - (gpib.dev) a gpib object to speak to
        """
        GenericInstrument.__init__(self)
        self.device = device
        self.term_chars = '\n'

    def write(self, query):
        """ writes a query to remote device

            Arguments:
            query -- (string) the query which shall be sent
        """
        gpib.write(self.device, query + self.term_chars)

    def read(self):
        """ reads a message from remote device

            Result:
            (string) -- message from remote device
        """
        return gpib.read(self.device, 512).rstrip()

    def close(self):
        """ closes connection to remote device """
        gpib.close(self.device)

    def clear(self):
        """ clears all communication buffers """
        gpib.clear(self.device)

class SerialInstrument(GenericInstrument):
    """ Implementation of GenericInstrument to communicate with gpib devices """
    def __init__(self, device):
        GenericInstrument.__init__(self)
        self.device = device
        self.term_chars = '\r'

    def write(self, query):
        """ writes a query to remote device

            Arguments:
            query -- (string) the query which shall be sent
        """
        self.device.write(query + self.term_chars)

    def read(self):
        """ reads a message from remote device

            Result:
            (string) -- message from remote device
        """
        message = ""
        while message[-len(self.term_chars):] != self.term_chars:
            message = message + self.device.read()
        return message.rstrip()

    def close(self):
        """ closes connection to remote device """
        return self.device.close()


def get_gpib_timeout(timeout):
    """ returns the correct timeout object to a certain timeoutvalue
        it will find the nearest match, e.g., 120us will be 100us

        Arguments:
        timeout -- (float) number of seconds to wait until timeout
    """
    gpib_timeout_list = [(0, gpib.TNONE), \
                         (10e-6, gpib.T10us), \
                         (30e-6, gpib.T30us), \
                         (100e-6, gpib.T100us), \
                         (300e-6, gpib.T300us), \
                         (1e-3, gpib.T1ms), \
                         (3e-3, gpib.T3ms), \
                         (10e-3, gpib.T10ms), \
                         (30e-3, gpib.T30ms), \
                         (100e-3, gpib.T100ms), \
                         (300e-3, gpib.T300ms), \
                         (1, gpib.T1s), \
                         (3, gpib.T3s), \
                         (10, gpib.T10s), \
                         (30, gpib.T30s), \
                         (100, gpib.T100s), \
                         (300, gpib.T300s), \
                         (1000, gpib.T1000s)]

    for val, res in gpib_timeout_list:
        if timeout <= val:
            return res
    return gpib.T1000s



def instrument(inst, timeout=10.0):
    """ returns the correct instrument given bei the inst string

        Arguments:
        inst -- (string) has the format  <INSTRUMENT_TYPE>::<ADDRESS>
                e.g., GPIB::24, SERIAL::COM1, ETHER::127.0.0.1
                possible INSTRUMENT_TYPES are [GPIB, ETHER, SERIAL]

        timeout -- (float) defines the time to wait for a read command

    """
    #TODO: make this look nicer
    #TODO: add minimalmodbus support  MODBUS:: ?
    try:
        inst_type, address = inst.split("::")
    except ValueError:
        raise RuntimeError(inst + " is not a legal instrument")

    if inst_type == "GPIB" or inst_type == "GPIB0":
        addr = int(address)
        device = gpib.dev(0, addr)
        gpib.timeout(device, get_gpib_timeout(timeout))
        return GpibInstrument(device)
    elif inst_type == "ETHER":
        addr, port = address.split(":")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((addr, int(port)))
        return EthernetInstrument(sock)
    elif inst_type == "SERIAL":
        ser = serial.Serial(address,
                            baudrate=9600, stopbits=serial.STOPBITS_TWO,
                            bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                            xonxoff=False, rtscts=False, dsrdtr=False,
                            timeout=timeout)
        return SerialInstrument(ser)

    raise ValueError("type not found " + inst)
