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



"""
class VariableDeclaration(object):
    def __init__(self, label, type = None, value = None, address = None, shared = False):
        self._label = label
        self._type = type
        self._value = value
        self._address = address
        self._shared = shared

    def get_type(self):
        return self._type

    def set_type(self, type):
        self._type = type

    def get_label(self):
        return self._label

    def get_value(self):
        return self._value

    def get_address(self):
        return self._address

    def get_shared(self):
        return self._shared

    def set_shared(self, shared):
        self._shared = shared

    def __str__(self):
        s = ''
        if self._shared:
            s += 'shared '

        if self._type:
            s += self._type + ' '
        
        s += self._label + ' '

        if self._address:
            s += ': 0x%x ' % self._address

        if self._value:
            s += '= %s' % self._value

        return s

    __repr__ = __str__

class ArrayValue(object):
    def __init__(self, value, labels = []):
        self._value = value
        self._labels = labels

    def get_value(self):
        return self._value

    def get_labels(self):
        return self._labels

    def __str__(self):
        s = ''
        for i in range(0, len(self._labels)):
            s += '%s: ' % self._labels[i]

        s += '%d' % self._value

        return s

    __repr__ = __str__

class ArrayDeclaration(VariableDeclaration):
    def __init__(self, label, type = None, value = None, address = None, shared = False):
        super(ArrayDeclaration, self).__init__(label, type, value, address, shared)

    def get_size(self):
        return len(self._value)

    def __str__(self):
        s = ''
        if self._shared:
            s += 'shared '

        if self._type:
            s += self._type + ' '
        
        s += self._label + '[' + str(self.get_size()) + '] '

        if self._address:
            s += ': 0x%x ' % self._address

        if self._value and isinstance(self._value, list):
            s += '= { '
            for i in range(0, len(self._value)):
                if i > 0:
                    s += ', '
                s += '%s' % self._value[i]
            s += ' }'

        return s

    __repr__ = __str__

class StructDeclaration(VariableDeclaration):
    def __init__(self, label, type = None, members = [], address = None, shared = False):
        super(StructDeclaration, self).__init__(label, 'struct ' + type, members, address, shared)

    def get_members(self):
        return self.get_value()

    def __str__(self):
        s = ''
        if self._shared:
            s += 'shared '

        s += self._label + ' '

        if self._address:
            s += ': 0x%x ' % self._address

        if len(self._value):
            s += '\n'
            s += '{\n'

            for m in self._value:
                s += '\t%s\n' % m
            
            s += '}'

        return s

    __repr__ = __str__
"""


