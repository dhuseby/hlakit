"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

from pyparsing import *
from types import *

class SymbolTable(object):

    class __impl(object):
        """
        Implementation of the symbol table
        """
        def __init__(self):
            self._table = {}

        def __getitem__(self, name):
            if self._table.has_key(name):
                return self._table[name]
            return None
        def __setitem__(self, name, symbol):
            self._table[name] = symbol

        def keys(self):
            return self._table.keys()

        def dump(self):
            print 'SymbolTable'
            for t in self._table.itervalues():
                print '\t%s' % t

    __instance = None

    def __init__(self):
        if SymbolTable.__instance is None:
            SymbolTable.__instance = SymbolTable.__impl()

        self.__dict__['_SymbolTable__instance'] = SymbolTable.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)

    @staticmethod
    def instance():
        st = SymbolTable()
        return st.__instance

class Symbol(object):
    """
    encapsulates a declared symbol
    """
    def __init__(self, name, type=None):
        self._name = name
        self._type = type

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    def set_type(self, _type):
        self._type = _type


class Variable(Symbol):
    """
    encapsulates a variable symbol
    """
    def __init__(self, name, type=None, shared=False, address=None, array=False, size=None):
        super(Variable, self).__init__(name, type)
        self._shared = shared
        self._address = address
        self._array = array
        self._size = size
        
        # register this symbol
        SymbolTable.instance()[name] = self

    def is_shared(self):
        return self._shared

    def set_shared(self, shared):
        self._shared = shared

    def set_array(self, array):
        self._array = array

    def is_array(self):
        return self._array

    def set_address(self, address):
        self._address = address

    def get_address(self):
        return self._address

    def get_array_size(self):
        if self._array and self._size:
            return self._size

        return None

    def set_array_size(self, size):
        if self._array:
            if self._size:
                # make sure the declared size matches the data size
                if int(self._size) != int(size):
                    raise ParseFatalException('array variable "%s" declaration doesn\'t match data size' % self.get_name())
            else:
                self._size = size
        else:
            raise ParseFatalException('variable "%s" is not declared as an array' % self.get_name())

    def get_size_in_bytes(self):
        size = self.get_type().get_size()
        if self._array:
            if self._size:
                size *= self._size
        return size

    def set_type(self, type_):
        super(Variable, self).set_type(type_)

        # if it is a typedef type, it can have an array, 
        # array size, and address
        if isinstance(type_, TypedefType):
            self._array = type_.is_array()
            self._size = type_.get_array_size()
            self._address = type_.get_address()

    def __str__(self):
        s = ''
        if self._shared:
            s += 'shared '

        if self.get_type():
            if isinstance(self.get_type(), TypedefType):
                s += self.get_type().get_name() + ' (' + self.get_type().get_type().get_name() + ') '
            else:
                s += self.get_type().get_name() + ' '

        s += self.get_name() + ' '

        if self._array:
            s += '['
            if self._size:
                s += '%s' % self._size
            s += ']'

        if self._address:
            s += ': 0x%x' % self._address

        return s

    __repr__ = __str__
