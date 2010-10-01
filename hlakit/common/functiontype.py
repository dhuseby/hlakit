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

class FunctionType(Type):
    """
    The type of a function.  Functions can be one of the following types:
        function  -- standard subroutine, cannot have parameters
        inline    -- macros that can have parameters
        interrupt -- interrupt handler, uses return from interrupt opcode to return
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        type_ = None
        if 'type_' in tokens.keys():
            type_ = tokens.type_[0]
        else:
            raise ParseFatalException('no function type specified')

        sub_type = None
        if 'name' in tokens.keys():
            if type_ != 'interrupt':
                raise ParseFatalException('non-interrupt function has name')
            sub_type = tokens.name

        noreturn = False
        if 'noreturn' in tokens.keys():
            noreturn = True
        
        return klass(type_, sub_type, noreturn)

    @classmethod
    def exprs(klass):
        intr_with_name = Literal('interrupt') + \
                         Suppress('.') + \
                         Name.exprs()
        expr = Or([Keyword('function'),
                   Keyword('inline'),
                   Keyword('interrupt'),
                   intr_with_name]).setResultsName('type_') + \
               Optional(Keyword('noreturn')).setResultsName('noreturn')
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, type, sub_type=None, noreturn=False):
        super(FunctionType, self).__init__(type)
        self._sub_type = sub_type
        self._noreturn = noreturn

    def get_sub_type(self):
        return self._sub_type

    def get_noreturn(self):
        return self._noreturn

    def __str__(self):
        s = '%s' % self.get_name()
        if self._sub_type:
            s += '.%s' % self._sub_type
        if self._noreturn:
            s += ' noreturn'
        return s

    def __hash__(self):
        return hash(self.__str__())

    __repr__ = __str__

