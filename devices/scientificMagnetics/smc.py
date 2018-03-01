#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alfons Schuck'
__version__ = '0.1'

import visa

assert visa.__version__ >= '1.5', 'visa should be 1.5 or newer'


class SMC(object):
    """Scientific Magnetic / Twickenham Super Conducting Magnet Controller (SMC) 5.52"""

    def __init__(self, GPIBPort: str):
        """
        Inititialisiert SMC
        :param GPIBPort: Example: 'GPIB0::12::INSTR'
        :type GPIBPort: str
        """
        rm = visa.ResourceManager('@py')
        self.inst = rm.open_resource(GPIBPort,
                                     write_termination='\r\n',
                                     read_termination='\r\n')

        # Initial Valiues
        self._ampsPerTesla = 9.755555  # A/T
        self._bRate = 0.005  # T/s, max: 0.006
        self._iRate = self._bRate * self._ampsPerTesla

        # Max Values
        self._TMax = 10  # T
        self._IMax = self._TMax * self._ampsPerTesla
        self._bRateMax = 0.006  # T/s
        self._iRateMax = self._bRateMax * self._ampsPerTesla  # A/s

        # Initialize Instrument
        self.inst.query('T0')  # Units displayed off (Amps)
        self.inst.query('P1')  # Pause
        self.iRate = self._iRate  # Set I-Rate

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
        self.inst.query('A{%08.5f}').format(self.bRate)

    @property
    def iRate(self) -> float:
        return self._iRate

    @iRate.setter
    def iRate(self, value: float):
        assert abs(value) <= self._iRateMax, "Absolute I-Rate should be lower than {}".format(self._iRateMax)
        self._iRate = value
        self.inst.query('A{%08.5f}').format(self.iRate)

    @property
    def amps(self) -> float:
        return float(self.inst.query('G')[1:9])

    @property
    def tesla(self) -> float:
        return self.amps * self.apt
