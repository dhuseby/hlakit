"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

class TypeRegistry(object):

    class __impl(object):
        """
        Implementation of the type registry
        """
        def __init__(self):
            self._registry = {}

        def __getitem__(self, name):
            if self._registry.has_key(name):
                return self._registry[name]
            return None
        def __setitem__(self, name, type):
            self._registry[name] = type

        def keys(self):
            return self._registry.keys()

        def dump(self):
            print 'TypeRegistry:'
            for t in self._registry.itervalues():
                print '\t%s' % t

    __instance = None

    def __init__(self):
        if TypeRegistry.__instance is None:
            TypeRegistry.__instance = TypeRegistry.__impl()

        self.__dict__['_TypeRegistry__instance'] = TypeRegistry.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)

    @staticmethod
    def instance():
        tr = TypeRegistry()
        return tr.__instance

class Type(object):
    """
    encapsulates types
    """
    def __init__(self, name, size):
        self._name = name
        self._size = size

    def get_name(self):
        return self._name

    def get_size(self):
        return self._size


class ByteType(Type):
    """
    8-but unsigned
    """
    def __init__(self):
        super(ByteType, self).__init__('byte', 1)

    def __str__(self):
        return 'byte size: 1'

    __repr__ = __str__

    @classmethod
    def register(klass):
        TypeRegistry.instance()['byte'] = klass()

class CharType(Type):
    """
    8-bit signed
    """
    def __init__(self):
        super(CharType, self).__init__('char', 1)

    def __str__(self):
        return 'char size: 1'

    __repr__ = __str__

    @classmethod
    def register(klass):
        TypeRegistry.instance()['char'] = klass()

class BoolType(Type):
    """
    8-bit boolean value (true/false)
    """
    def __init__(self):
        super(BoolType, self).__init__('bool', 1)

    def __str__(self):
        return 'bool size: 1'

    __repr__ = __str__

    @classmethod
    def register(klass):
        TypeRegistry.instance()['bool'] = klass()

class WordType(Type):
    """
    16-bit unsigned integer
    """
    def __init__(self):
        super(WordType, self).__init__('word', 2)

    def __str__(self):
        return 'word size: 2'

    __repr__ = __str__

    @classmethod
    def register(klass):
        TypeRegistry.instance()['word'] = klass()

class StructType(Type):
    """
    User-defined conglomeration of data
    """
    def __init__(self, name):
        super(StructType, self).__init__('struct ' + name, 0)
        self._members = {}

        # register this type in the registry
        TypeRegistry.instance()[self.get_name()] = self

    def add_member(self, name, type):
        self._members[name] = type

    def get_size(self):
        """
        A struct's size is the sum of the sizes of its members
        """
        size = 0
        for v in self._members.itervalues():
            size += v.get_size()
        return size

    def __str__(self):
        return '%s size: %d' % (self.get_name(), self.get_size())

    __repr__ = __str__

class TypedefType(Type):
    """
    User-defined type alias
    """
    def __init__(self, alias, _type, address=None, array=False, array_size=None):
        super(TypedefType, self).__init__(alias, 0)

        # make sure that we have a reference to the type object
        if isinstance(_type, Type):
            self._type = _type
        else:
            self._type = TypeRegistry.instance()[str(_type)]

        # store the address if defined
        self._address = address

        # store the array and array size if defined
        self._array = array
        self._array_size = array_size

        # register this type in the registry
        TypeRegistry.instance()[self.get_name()] = self

    def get_size(self):
        if self._array and self._size:
            return self._size * self._type.get_size()

        return self._type.get_size()

    def is_array(self):
        return self._array

    def get_array_size(self):
        return self._array_size

    def get_address(self):
        return self._address

    def get_type(self):
        return self._type

    def __str__(self):
        return 'typedef %s -> %s size: %d' % (self.get_name(), self._type.get_name(), self._type.get_size())

    __repr__ = __str__


