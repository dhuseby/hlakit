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
from name import Name
from functionparameter import FunctionParameter

class FunctionCall(object):
    """
    The class representing a function call
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        fn = None
        # get a reference to the symbol table
        st = SymbolTable()

        name = None
        if 'name' in tokens.keys():
            name = tokens.name

        # look up the function decl
        fn = st[name]
        if fn is None:
            raise ParseFatalException('function %s not defined' % name)
        type_ = fn.get_type()

        params = None
        if 'params' in tokens.keys():
            # some built-in functions are "operator" type functions and they can
            # have parameters because they are a special type of inline macro
            if type_.get_type() not in ('inline', 'operator'):
                raise ParseFatalException('calling non-inline function with params')
            params = [ p for p in tokens.params ]

        return FunctionCall(name, type_, params)

    @classmethod
    def exprs(klass):
        expr = Forward()
        func = Name.exprs() + \
               Suppress('(') + \
               Optional(delimitedList(expr).setResultsName('params')) + \
               Suppress(')') 
        expr << (func | FunctionParameter.exprs())
        func.setParseAction(klass.parse)
        return func

    def __init__(self, name, type_, params=None):
        self._name = name
        self._type = type_
        self._params = params

    def get_name(self):
        return self._name

    def get_params(self):
        return self._params

    def get_type(self):
        return self._type


