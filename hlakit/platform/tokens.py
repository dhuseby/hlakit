"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

class Memory(object):
    RAM = 1
    ROM = 2
    CHR = 3

    def __init__(self, type):
        self._type = type

    def get_type(self):
        return self._type


class MemOrg(Memory):
    """
    This is a wrapper class for a memory org statement
    """
    
    def __init__(self, type, org, max = None):
        super(MemOrg, self).__init__(type)
        self._org = org
        self._max_size = max

    def get_org(self):
        return self._org

    def get_max_size(self):
        return self._max_size

    def __str__(self):
        if self._max_size is None:
            return "<org: 0x%x>" % int(self._org)
        return "<org: 0x%x, max: 0x%x>" % (self._org, self._max_size)

    __repr__ = __str__


class MemEnd(Memory):
    """
    This is a wrapper class for a memory end statement
    """
    
    def __init__(self, type):
        super(MemEnd, self).__init__(type)

    def __str__(self):
        return "<end>"

    __repr__ = __str__


class MemBankSize(Memory):
    """
    This is a wrapper class for a memory bank size statement
    """
    
    def __init__(self, type, size):
        super(MemBankSize, self).__init__(type)
        self._size = size

    def get_size(self):
        return self._size

    def __str__(self):
        return "<0x%x>" % self._size

    __repr__ = __str__


class MemBankNumber(Memory):
    """
    This is a wrapper class for a memory bank size statement
    """
    
    def __init__(self, type, number, max = None):
        super(MemBankNumber, self).__init__(type)
        self._number = number
        self._max_size = max

    def get_number(self):
        return self._number

    def get_max_size(self):
        return self._max_size

    def __str__(self):
        if self._max_size is None:
            return "<bank: %d>" % self._number
        return "<bank: %d, max: 0x%x>" % (self._number, self._max_size)

    __repr__ = __str__

class MemBankLink(Memory):
    """
    This is a wrapper class for a memory bank link to a binary file
    """

    def __init__(self, type, file, size = None):
        super(MemBankLink, self).__init__(type)
        self._file = file
        self._size = size

    def get_file(self):
        return self._file

    def get_size(self):
        return self._size

    def __str__(self):
        if self._size is None:
            return "<file: %s>" % self._file
        return "<file: %s, size: 0x%x>" % (self._file, self._size)

    __repr__ = __str__


class Tell(object):
    """
    Tell token for all of the different tells
    """
    NUMBER = 0
    OFFSET = 1
    SIZE = 2
    FREE = 3
    TYPE = 4
    NAMES = [ 'NUMBER', 'OFFSET', 'SIZE', 'FREE', 'TYPE' ]

    def __init__(self, type):
        self._type = type

    def get_type(self):
        return self._type

    def __str__(self):
        return "<type: %s>" % Tell.NAMES[self._type]

    __repr__ = __str__

