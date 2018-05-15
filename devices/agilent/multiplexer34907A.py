class Multiplexer34970A(object):
    """With add-in card Agilent 34901A on channel 1."""
    
    def __init__(self, device):
        self.dev = device
        self.dev.write_termination = "\n"
        self.dev.read_termination = "\n"
        self.dev.write('*RST')

    def open(self, route: int):
       """Open the relay on a route."""
       self.dev.write(":ROUTE:OPEN (@1{:02d})".format(route))
       
    def close(self, route: int):
       """Close the relay on a route."""
       self.dev.write(":ROUTE:CLOSE (@1{:02d})".format(route))


if __name__=='__main__':
    from visa import ResourceManager
    from time import sleep

    rm = ResourceManager('@py')

    dev = rm.open_resource('GPIB::03::INSTR')

    mux = Multiplexer34970A(dev)
    
    for i in range(5):
        mux.open(12)
        sleep(1)
        mux.close(12)
        sleep(1)
    
