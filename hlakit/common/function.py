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
from symboltable import SymbolTable
from symbol import Symbol
from name import Name
from functiontype import FunctionType
from functionparameter import FunctionParameter


class Function(Symbol):
    """
    The base class of function definitions
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        fnname = None
        if 'fnname' in tokens.keys():
            fnname = Name(tokens.fnname)

        type_ = None
        if 'type_' in tokens.keys():
            # if we get in here, then this is a func decl
            type_ = tokens.type_
        else:
            raise ParseFatalException('function decl missing type')

        params = None
        if 'params' in tokens.keys():
            # only inline function decl's can have params
            if type_.get_type() != 'inline':
                raise ParseFatalException('non-inline function decl with params')
            params = [ p for p in tokens.params ]

        # add the function to the symbol table
        fn = klass(fnname, type_, params)
        SymbolTable().new_symbol(fn)

        return fn

    @classmethod
    def exprs(klass):
        fnname = Word(alphas, alphanums + '_')
        expr = FunctionType.exprs().setResultsName('type_') + \
               fnname.setResultsName('fnname') + \
               Suppress('(') + \
               Optional(delimitedList(Name.exprs()).setResultsName('params')) + \
               Suppress(')')
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, name, type_=None, params=None):
        super(Function, self).__init__(name, type_)
        self._params = params

    def get_noreturn(self):
        return self.get_type().get_noreturn()

    def get_params(self):
        return self._params

    def __str__(self):
        s = ''
        if self.get_type():
            s += str(self.get_type()) + ' '
        s += str(self.get_name())
        s += '('
        if self._params:
            for i in range(0, len(self._params)):
                if i > 0:
                    s += ','
                s += ' ' + str(self._params[i])
            s += ' '
        s += ')'
        return s

