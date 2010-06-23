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
from value import Value
from struct import Struct
from operatorparameter import OperatorParameter
from keywordoperator import KeywordOperator

class SizeOfParameter(OperatorParameter):
    """ encapsulates the parameter for a sizeof() operator """

    @classmethod
    def exprs(klass):
        variable_ref = Group(Name.exprs() + ZeroOrMore(Suppress('.') + Name.exprs()))
        # sizeof() takes the normal params as well as full struct declarations
        expr = Or([Struct.exprs().setResultsName('struct'), 
                   variable_ref.setResultsName('name'),
                   Value.exprs().setResultsName('value')])
        expr.setParseAction(klass.parse)
        return expr

class SizeOf(KeywordOperator):
    """
    The sizeof() keyword operator
    """

    @classmethod
    def _get_keyword(klass):
        return 'sizeof'

    @classmethod
    def _get_param(klass):
        return SizeOfParameter.exprs()

    def __len__(self):
        if self.get_value():
            return len(self.get_value())

        # TODO: look up the type or the variable from the symbol and get its size
        return 0

    def __str__(self):
        return 'sizeof(%s)' % self.get_symbol() or self.get_value()

    __repr__ = __str__

