#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alfons Schuck'
__version__ = '0.1'


import visa
#import virtual_visa as visa

assert visa.__version__ >= '1.5', 'visa should be 1.5 or newer'


class SMC(object):
    """
    Scientific Magnetic / Twickenham Super Conducting Magnet Controller (SMC) 5.52
    Operating Manual: http://www.twicksci.co.uk/manuals/pdf/smc552+.pdf
    """

    def __init__(self, GPIBPort: str = 'GPIB0::4::INSTR'):
        """
        Inititialisiert SMC
        :param GPIBPort: Example: 'GPIB0::12::INSTR'
        :type GPIBPort: str
        """
        rm = visa.ResourceManager('@py')
        self.inst = rm.open_resource(GPIBPort,
                                     write_termination='\r\n',
                                     read_termination='\r\n',
                                     delay = 0.1)

        # Initial Valiues
        self._ampsPerTesla = 9.755555  # A/T
        self._bRate = 0.005  # T/s, max: 0.006
        self._iRate = self._bRate * self._ampsPerTesla
        self._unit = 0  # A
        self._rampTarget = 0
        self._direction = 0  # Forward

        # Max Values
        self._TMax = 10  # T
        self._IMax = self._TMax * self._ampsPerTesla
        self._bRateMax = 0.006  # T/s
        self._iRateMax = self._bRateMax * self._ampsPerTesla  # A/s

        # Initialize Instrument
        self.unit = 0
        self.pause = 0
        self.direction = 0
        self.iRate = self.iRate  # Set I-Rate


    @property
    def unit(self) -> int:
        return self._unit

    @unit.setter
    def unit(self, value: int):
        assert (value == 0) or (value == 1), 'Value should be 0 (A) or 1(T)!'
        self._unit = value
        self.inst.query('T{:1d}'.format(self.unit))

    @property
    def pause(self) -> int:
        return self._pause

    @pause.setter
    def pause(self, value:int):
        assert (value == 0) or (value == 1), 'Value should be 0 (A) or 1(T)!'
        self._pause = value
        self.inst.query('P{:1d}'.format(self.pause))

    @property
    def apt(self) -> float:
        return self._ampsPerTesla

    @property
    def bRate(self) -> float:
        return self._bRate

    @bRate.setter
    def bRate(self, value: float):
        assert abs(value) <= self._bRateMax, "Absolute B-Rate should be lower than {}".format(self._bRateMax)
        self._bRate = value / self.apt
        self.inst.query('A{:08.5f}'.format(self._bRate))

    @property
    def iRate(self) -> float:
        return self._iRate

    @iRate.setter
    def iRate(self, value: float):
        assert abs(value) <= self._iRateMax, "Absolute I-Rate should be lower than {}".format(self._iRateMax)
        self._iRate = value
        self.inst.query('A{:08.5f}'.format(self._iRate))

    @property
    def amps(self) -> float:
        return float(self.inst.query('G')[1:9])

    @property
    def tesla(self) -> float:
        return self.amps * self.apt

    @property
    def setPoint(self) -> dict:
        valueString = self.inst.query('S')
        setPoint = {'unit' : int(valueString[1]),
                    'upper' : float(valueString[3:10]),
                    'lower' : float(valueString[11:18])}

        return setPoint

    @property
    def upperSetPoint(self) -> float:
        return self.setPoint['upper']

    @upperSetPoint.setter
    def upperSetPoint(self, value: float):
        if self.unit == 0:
            assert abs(value) < self._IMax
            self.inst.query('U{:07.3f}'.format(value))
        elif self.unit == 1:
            assert abs(value) < self._TMax
            self.inst.query('U{:07.4f}'.format(value))
        else:
            pass

        if value >= 0:
            self.direction = 0
        elif value < 0:
            self.direction = 1

    @property
    def lowerSetPoint(self) -> float:
        return self.setPoint['upper']

    @lowerSetPoint.setter
    def lowerSetPoint(self, value: float):
        self.pause = 1
        if self.unit == 0:
            assert abs(value) < self._IMax
            self.inst.query('L{:07.3f}'.format(value))
        elif self.unit == 1:
            assert abs(value) < self._TMax
            self.inst.query('L{:07.4f}'.format(value))
        else:
            pass

        if value >= 0:
            self.direction = 0
        elif value < 0:
            self.direction = 1


    @property
    def rampTarget(self) -> int:
        return self._rampTarget

    @rampTarget.setter
    def rampTarget(self, value:int):
        assert (value == 0) or (value == 1) or (value ==2), 'Value should be 0 (Zero), 1(Lower) or 2(Upper)!'
        self._rampTarget = value
        self.inst.query('R{:1d}'.format(self.rampTarget))

    @property
    def direction(self) -> int:
        return self._direction

    @direction.setter
    def direction(self, value:int):
        assert (value == 0) or (value == 1), 'Value should be 0 (Forward) or 1(Reverse)!'
        self._direction = value
        self.inst.query('D{:1d}'.format(self.direction))


if __name__ == '__main__':
    dev = SMC()
    print(dev.upperSetPoint)







