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

import os
from cStringIO import StringIO
from pyparsing import *
from type_ import Type
from struct import Struct
from typedef import Typedef
from immediate import Immediate
from variable import Variable
from function import Function
from functioncall import FunctionCall
from codeblock import CodeBlock
from filemarkers import FileBegin, FileEnd
from scopemarkers import ScopeBegin, ScopeEnd
from symboltable import SymbolTable

class Compiler(object):

    @classmethod
    def exprs(klass):
        e = []
        e.extend(klass.first_exprs())
        e.extend(klass.last_exprs())
        return e

    @classmethod
    def first_exprs(klass):
        e = []
        e.append(('type', Type.exprs()))
        e.append(('struct', Struct.exprs()))
        e.append(('typedef', Typedef.exprs()))
        e.append(('variable', Variable.exprs()))
        e.append(('function', Function.exprs()))
        e.append(('functioncall', FunctionCall.exprs()))
        e.append(('scopebegin', ScopeBegin.exprs()))
        e.append(('scopeend', ScopeEnd.exprs()))
        return e

    @classmethod
    def last_exprs(klass):
        e = []
        return e

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def __init__(self):
        if not hasattr(self, '_exprs'):
            self.set_exprs(self.__class__.exprs())
        if not hasattr(self, '_tokens'):
            self._tokens = []

    def reset_state(self):
        self.set_exprs(self.__class__.exprs())
        self._tokens = []

    def basic_types(klass):
        # these are the basic type identifiers
        return [ Type('byte'),
                 Type('char'),
                 Type('bool'),
                 Type('word'),
                 Type('pointer') ]

    def get_exprs(self):
        return getattr(self, '_exprs', [])

    def set_exprs(self, value):
        self._exprs = value

    def _get_tokens(self):
        return getattr(self, '_tokens', [])

    def _append_tokens(self, tokens):
        if not hasattr(self, '_tokens'):
            self._tokens = []
        self._tokens.extend(tokens)

    def get_output(self):
        return self._get_tokens()

    def compile(self, tokens):
        expr_or = Or([])
        for e in self.get_exprs():
            expr_or.append(e[1])
        parser = ZeroOrMore(expr_or)
        parser.ignore(cStyleComment)

        # process the tokens the compiler cares about
        cc_tokens = []
        for token in tokens:
            if isinstance(token, FileBegin):
                # set up the file scope
                SymbolTable().scope_push(token.get_name())
            elif isinstance(token, FileEnd):
                # take down the file scope
                SymbolTable().scope_pop()
            elif isinstance(token, CodeBlock):
                # compile the code block
                cc_tokens.extend(parser.parseFile(StringIO(str(token))))
            else:
                # pass the token on
                cc_tokens.append(token)

        self._tokens = cc_tokens
