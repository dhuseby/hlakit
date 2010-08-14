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
from symbol import Symbol
from type_ import Type
from name import Name
from numericvalue import NumericValue

class Enum(Symbol):
    """
    The struct type
    """

    class Member(Symbol):
        @classmethod
        def parse(klass, pstring, location, tokens):
            pp = Session().preprocessor()

            if pp.ignore():
                return []

            if 'mname' not in tokens.keys():
                raise ParseFatalException('struct member without name')

            value = None
            if 'mvalue' in tokens.keys():
                value = tokens.mvalue[0]

            return klass(tokens.mname[0], Type('enum member'), value)

        def __init__(self, name, type_, value):
            super(Enum.Member, self).__init__(name, type_)
            self._value = value

        def get_value(self):
            return self._value

        def __str__(self):
            s = str(self.get_name())
            if self.get_value() != None:
                s += ' = ' + str(self.get_value())
            return s

        __repr__ = __str__


    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'enum' not in tokens.keys():
            raise ParseFatalException('enum declared without enum keyword')

        if 'ename' not in tokens.keys():
            raise ParseFatalException('enum declared without name')

        # initialize the Enum type
        t = klass(tokens.ename[0], Type('enum %s' % tokens.ename[0]))
        for m in tokens.member_list:
            t.append_member(m)

        return t

    @classmethod
    def exprs(klass):
        lbrace = Suppress('{')
        rbrace = Suppress('}')
        enum = Forward()

        # an enum emmber can have an optional initialization clause
        member = Group(Name.exprs()).setResultsName('mname') + \
                 Optional(Suppress('=') + NumericValue.exprs()).setResultsName('mvalue')
        member.setParseAction(klass.Member.parse)

        # the member list is a delimited list of members and other enums 
        member_list = delimitedList(Or([member, enum]), delim=',')
        
        # an enum is the keyword enum name { member list }
        enum << Keyword('enum').setResultsName('enum') + \
                Group(Name.exprs()).setResultsName('ename') + \
                lbrace + \
                Optional(member_list).setResultsName('member_list') + \
                Optional(Suppress(',')) + \
                rbrace
        enum.setParseAction(klass.parse)
        return enum

    def __init__(self, name, type_):
        super(Enum, self).__init__(name, type_)
        self._members = []
        self._member_vars = {}

    def append_member(self, member):
        if not isinstance(member, Enum.Member) and \
           not isinstance(member, Enum):
            raise ParseFatalException('attempting to add non Member as member of enum')

        self._members.append(member.get_name())
        self._member_vars[member.get_name()] = member

    def has_member(self, name):
        return self._member_vars.has_key(name)

    def get_member(self, name):
        return self._member_vars.get(name, None)

    def __str__(self):
        s = 'enum %s' % self.get_name()
        return s

    __repr__ = __str__

