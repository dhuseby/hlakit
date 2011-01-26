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
from struct_ import Struct
from numericvalue import NumericValue

class Typedef(Type):
    """
    TypeDef parser/handler
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'typedef' not in tokens.keys():
            raise ParseFatalException('missing typedef')

        if 'type_' not in tokens.keys():
            raise ParseFatalException('typedef missing type')

        if 'name' not in tokens.keys():
            raise ParseFatalException('typedef missing alias')

        array_ = 'array_' in tokens.keys()
        size = None
        if 'size' in tokens.keys():
            size = tokens.size

        return klass(tokens.name, tokens.type_, array_, size)    

    @classmethod
    def exprs(klass):
        lbracket = Suppress('[')
        rbracket = Suppress(']')
        expr = Keyword('typedef').setResultsName('typedef') + \
               Or([Struct.exprs(),
                   Type.exprs()]).setResultsName('type_') + \
               Name.exprs().setResultsName('name') + \
               Optional(lbracket + \
                        Optional(NumericValue.exprs()).setResultsName('size') + \
                        rbracket).setResultsName('array_')
        expr.setParseAction(klass.parse)
        
        return expr

    def __init__(self, name, aliased_type, array_=False, size=None):
        # typedef's have a zero size...
        super(Typedef, self).__init__(str(name), 0)

        self._aliased_type = aliased_type
        self._array = array_
        self._size = size

    def is_alias(self):
        return True

    def get_aliased_type(self):
        return self._aliased_type

    def is_array(self):
        return self._array

    def get_array_size(self):
        if self._size != None:
            return int(self._size)
        return None

    def __str__(self):
        s = 'typedef %s' % self._aliased_type
        return s

    __repr__ = __str__

