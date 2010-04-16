"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

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
    def __init__(self, name, type):
        self._name = name
        self._type = type

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type


class Variable(Symbol):
    """
    encapsulates a variable symbol
    """
    def __init__(self, name, type, shared = False, address = None):
        super(Variable, self).__init__(name, type)
        self._shared = shared
        self._address = address

        # register this symbol
        SymbolTable.instance()[name] = self

    def is_shared(self):
        return self._shared

    def set_address(self, address):
        self._address = address

    def get_address(self):
        return self._address

    def __str__(self):
        s = ''
        if self._shared:
            s += 'shared '

        s += self.get_type().get_name() + ' '
        s += self.get_name() + ' '

        if self._address:
            s += ': 0x%x' % self._address

        return s

    __repr__ = __str__
