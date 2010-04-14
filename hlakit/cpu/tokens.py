"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

from hlakit.number import Number

class InterruptVector(object):
    """
    Token for setting an interrupt vector value
    """

    START = 0
    NMI = 1
    IRQ = 2
    NAMES = ['START', 'NMI', 'IRQ' ]

    def __init__(self, type, value):
        self._type = type
        self._value = value

    def get_type(self):
        return self._type

    def get_value(self):
        return self._value

    def __str__(self):
        if isinstance(self._value, Number):
            return "<%s = 0x%x>" % (InterruptVector.NAMES[self._type], self._value)
        return "<%s = %s>" % (InterruptVector.NAMES[self._type], self._value)

    __repr__ = __str__

