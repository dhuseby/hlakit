"""
HLAKit
Copyright (c) 2010 David Huseby. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY DAVID HUSEBY ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DAVID HUSEBY OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of David Huseby.
"""

from pyparsing import *
from session import Session
from type_ import Type
from name import Name
from numericvalue import NumericValue

class Struct(Type):
    """
    The struct type
    """

    class Member(Type):
        @classmethod
        def parse(klass, pstring, location, tokens):
            pp = Session().preprocessor()

            if pp.ignore():
                return []

            if 'type_' not in tokens.keys():
                raise ParseFatalException('struct member without type')

            if 'name_list' not in tokens.keys():
                raise ParseFatalException('struct member without name')

            m = []
            for (name, size) in tokens.name_list: 
                m.append(klass(name, tokens.type_, size))

            return m

        def __init__(self, name, type_, size=None):
            super(Struct.Member, self).__init__(name)
            self._type = type_
            self._size = size

        def get_type(self):
            return self._type

        def is_array(self):
            return self._size != None

        def is_struct(self):
            return isinstance(self._type, Struct)

        def has_member(self, name):
            if not self.is_struct():
                raise ParseFatalException('trying to access member of non-struct member')
            return self._type.has_member(name)

        def get_member(self, name):
            if not self.is_struct():
                raise ParseFatalException('trying to access member of non-struct member')
            return self._type.get_member(name)

        def get_array_size(self):
            if self._size != None:
                return int(self._size)
            return None

        def __str__(self):
            s = '%s %s' % (self.get_type(), self.get_name())
            if self.is_array():
                s += '[%s]' % self.get_array_size()
            return s

        __repr__ = __str__


    @classmethod
    def parse_name(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'name' not in tokens.keys():
            raise ParseFatalException('struct member missing name')

        if 'array' in tokens.keys() and 'size' not in tokens.keys():
            raise ParseFatalException('array struct members must have an explicit size')

        size = None
        if 'array' in tokens.keys():
            size = tokens.size

        return (tokens.name, size)
            

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'struct' not in tokens.keys():
            raise ParseFatalException('struct declared without struct keyword')

        if 'name' not in tokens.keys():
            raise ParseFatalException('struct declared without name')

        if 'member_list' not in tokens.keys():
            raise ParseFatalException('struct missing at least one member')

        # initialize the Struct type
        t = klass('struct %s' % tokens.name)
        for m in tokens.member_list:
            t.append_member(m)

        return t

    @classmethod
    def exprs(klass):
        lbrace = Suppress('{')
        rbrace = Suppress('}')
        lbracket = Suppress('[')
        rbracket = Suppress(']')
        struct = Forward()

        # names in structs can have arrays after them
        name = Name.exprs().setResultsName('name') + \
               Optional(lbracket + \
                        NumericValue.exprs().setResultsName('size') + \
                        rbracket).setResultsName('array')
        name.setParseAction(klass.parse_name)

        member = Or([Type.exprs(), struct]).setResultsName('type_') + \
                 delimitedList(name).setResultsName('name_list')
        member.setParseAction(klass.Member.parse)

        struct << Keyword('struct').setResultsName('struct') + \
                  Name.exprs().setResultsName('name') + \
                  Optional(lbrace + \
                           OneOrMore(member).setResultsName('member_list') + \
                           rbrace)
        struct.setParseAction(klass.parse)
        
        return struct

    def __init__(self, name):
        super(Struct, self).__init__(name)
        self._members = []
        self._member_vars = {}

    def append_member(self, member):
        if not isinstance(member, Struct.Member):
            raise ParseFatalException('attempting to add non Member as member of struct')

        self._members.append(member.get_name())
        self._member_vars[member.get_name()] = member

    def has_member(self, name):
        return self._member_vars.has_key(name)

    def get_member(self, name):
        return self._member_vars.get(name, None)

    def __str__(self):
        s = '%s\n{\n' % self.get_name()
        for m in self._members:
            s += '\t%s %s\n' % (self.get_member(m).get_type(), self.get_member(m).get_name())
        s += '}'
        return s

    __repr__ = __str__

