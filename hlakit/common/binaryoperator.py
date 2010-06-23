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
from name import Name
from type_ import Type
from struct import Struct
from value import Value

class BinaryOperator(object):
    """
    The base class of binary operators
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'struct' in tokens.keys():
            return klass(symbol=tokens.struct)

        if 'name' in tokens.keys():
            if len(tokens.name) == 1:
                return klass(symbol=tokens.name[0])
            else:
                return klass(symbol=Name('.'.join([n.get_name() for n in tokens.name])))
            raise ParseFatalException('invalid parameter for keyword operator')

        if 'operator_' in tokens.keys():
            return klass(symbol=tokens.operator_)

        if 'value' in tokens.keys():
            return klass(value=tokens.value)
        
        raise ParseFatalException('no parameter specified')

    @classmethod
    def exprs(klass):
        kw = Keyword(klass._get_keyword())
        variable_ref = Group(Name.exprs() + ZeroOrMore(Suppress('.') + Name.exprs()))
        expr = Forward()
        expr << Suppress(kw) + \
                Or([Struct.exprs().setResultsName('struct'), 
                    variable_ref.setResultsName('name'),
                    Value.exprs().setResultsName('value'),
                    expr.setResultsName('operator_')]) + \
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, symbol=None, value=None):
        self._symbol = symbol
        self._value = value

    def get_symbol(self):
        return self._symbol

    def get_value(self):
        return self._value


