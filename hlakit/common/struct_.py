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

    class Member(object):

        def __init__(self, name, type_, array_=False, size=None):
            self._name = name
            while type_.is_alias():
                #print "following type alias '%s' -> '%s'" % (type_, type_.get_aliased_type())
                type_ = type_.get_aliased_type()
            self._type = type_
            self._array = array_
            if (array_ == True) and (size is None):
                raise ParseFatalException("struct member array is missing required size")
            self._size = size

        def get_name(self):
            return self._name

        def get_type(self):
            return self._type

        def is_array(self):
            return self._array

        def get_array_size(self):
            if self._size != None:
                return int(self._size)
            return None

        def get_size(self):
            if self.is_array():
                return self.get_array_size() * self._type.get_size()
            else:
                return self._type.get_size()

        def has_member(self, name):
            if isinstance(self._type, Struct):
                return self._type.has_member(name)

        def get_member(self, name):
            if isinstance(self._type, Struct):
                return self._type.get_member(name)

        def __str__(self):
            s = '%s %s' % (str(self._type), self._name)
            if self.is_array():
                s += '[%d]' % self.get_array_size()
            return s

    @classmethod
    def parse_members(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'name_list' not in tokens.keys():
            raise ParseFatalException('struct member has no name')

        if 'type_' not in tokens.keys():
            raise ParseFatalException('struct member has no type')

        members = []
        for n in tokens.name_list:
            array_ = False
            array_size = None
            if 'array_' in n.keys():
                array_ = True
                if 'array_size' not in n.keys():
                    raise ParseFatalException('struct member array has no size')
                array_size = n.array_size

            members.append(Struct.Member(n.name, tokens.type_, array_, array_size))
            
        return members

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'struct' not in tokens.keys():
            raise ParseFatalException('struct declared without struct keyword')

        if 'name' not in tokens.keys():
            raise ParseFatalException('struct declared without name')

        members = None
        if 'member_list' in tokens.keys():
            members = tokens.member_list

        # initialize the Struct type
        t = klass('struct %s' % tokens.name, members)

        return t

    @classmethod
    def exprs(klass):
        lbrace = Suppress('{')
        rbrace = Suppress('}')
        lbracket = Suppress('[')
        rbracket = Suppress(']')
        size = NumericValue.exprs()
        struct = Forward()

        # build rule for members
        member = Or([Type.exprs(), struct]).setResultsName('type_') + \
               ~LineEnd() + \
               delimitedList(Group(Name.exprs().setResultsName('name') + \
                                   Optional(lbracket + \
                                            size.setResultsName('array_size') + \
                                            rbracket).setResultsName('array_') \
                                  ), \
                             delim=',').setResultsName('name_list')
        member.setParseAction(klass.parse_members)

        struct << Keyword('struct').setResultsName('struct') + \
                  Name.exprs().setResultsName('name') + \
                  Optional( \
                           lbrace + \
                           OneOrMore(member).setResultsName('member_list') + \
                           rbrace)
        struct.setParseAction(klass.parse)
        
        return struct

    def __init__(self, name, members=None):
        self._members = []
        self._member_vars = {}
        size = None
        if members != None:
            for m in members:
                if not isinstance(m, Struct.Member):
                    raise ParseFatalException('attempting to add non Member as member of struct')
                if size is None:
                    size = m.get_size()
                else:
                    size += m.get_size()
                self._members.append(m.get_name())
                self._member_vars[m.get_name()] = m

        # NOTE: make sure the struct is fully initialized before calling
        # the Type base class because it will add the type to the TypeRegistry
        # and needs to know its size
        super(Struct, self).__init__(name, size)

    def has_member(self, name):
        return self._member_vars.has_key(name)

    def get_member(self, name):
        return self._member_vars.get(name, None)

    def __str__(self):
        return self.get_name()

