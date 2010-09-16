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
from enum import Enum
from type_ import Type
from label import Label
from struct_ import Struct
from typedef import Typedef
from immediate import Immediate
from variable import Variable
from function import Function
from functiondecl import FunctionDecl
from functioncall import FunctionCall
from functionreturn import FunctionReturn
from conditional import Conditional
from codeblock import CodeBlock
from filemarkers import FileBegin, FileEnd
from scopemarkers import ScopeBegin, ScopeEnd
from symboltable import SymbolTable
from variableinitializer import VariableInitializer

class Compiler(object):

    OUTSIDE, FN, INSIDE, CONDITIONAL, ERROR = range(5)
    STATE_NAME = { OUTSIDE:     'OUTSIDE',
                   FN:          'FN',
                   INSIDE:      'INSIDE',
                   CONDITIONAL: 'CONDITIONAL',
                   ERROR:       'ERROR' }

    @classmethod
    def exprs(klass):
        e = []
        e.extend(klass.first_exprs())
        e.extend(klass.last_exprs())
        return e

    @classmethod
    def first_exprs(klass):
        e = []
        e.append(('return', FunctionReturn.exprs()))
        e.append(('enum', Enum.exprs()))
        e.append(('label', Label.exprs()))
        e.append(('typedef', Typedef.exprs()))
        e.append(('variable', Variable.exprs()))
        e.append(('struct', Struct.exprs()))
        e.append(('functiondecl', FunctionDecl.exprs()))
        e.append(('functioncall', FunctionCall.exprs()))
        e.append(('scopebegin', ScopeBegin.exprs()))
        e.append(('scopeend', ScopeEnd.exprs()))
        e.append(('initializer', VariableInitializer.exprs()))
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
        if not hasattr(self, '_debug'):
            self._debug = False

    def reset_state(self):
        self.set_exprs(self.__class__.exprs())
        self._tokens = []
        self._state = self.OUTSIDE

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

    def _scan(self, tokens):
        # build the parser phase rules
        expr_or = MatchFirst([])
        for e in self.get_exprs():
            expr_or.append(e[1])
        parser = ZeroOrMore(expr_or)
        parser.ignore(cStyleComment | cppStyleComment)

        # run the pre-processor tokens through the parser phase
        cc_tokens = []
        for token in tokens:
            if isinstance(token, CodeBlock):
                # compile the code block
                cc_tokens.extend(parser.parseFile(StringIO(str(token))))
            else:
                # pass the token on
                cc_tokens.append(token)

        return cc_tokens

    def _debug_state(self, token, state=None):
        if self._debug:
            if state is None:
                print '%s (%s) %s' % (self.STATE_NAME[self._state], type(token), token)
            else:
                print '%s -> %s (%s) %s' % (self.STATE_NAME[self._state], self.STATE_NAME[state], type(token), token)

    def _next_state(self, token):

        st = SymbolTable()

        # outside of a function declaration
        if self._state == self.OUTSIDE:
            if isinstance(token, FunctionDecl):
                if self._depth != 0:
                    self._debug_state(token, self.ERROR)
                    self._state = self.ERROR
                    raise ParseFatalError('cannot declare a function here')
                self._fn = Function(token)
                self._debug_state(token)
                self._state = self.FN
            elif isinstance(token, Variable):
                self._debug_state(token)
                st.new_symbol(token)
                return token
            elif isinstance(token, FileBegin):
                self._debug_state(token)
                st.scope_push(str(token.get_name()))
            elif isinstance(token, FileEnd):
                self._debug_state(token)
                st.scope_pop()
            else:
                return token

        # have seen a function decl, looking for {
        elif self._state == self.FN:
            if isinstance(token, ScopeBegin):
                self._fn.append_token(token)
                self._depth += 1
                self._debug_state(token, self.INSIDE)
                self._state = self.INSIDE
                self._debug_state(token)
                st.scope_push(str(self._fn.get_name()))
            else:
                self._debug_state(token, self.ERROR)
                self._state = self.ERROR
                s = 'function decl not followed by {\n'
                s += str(self._fn) + '\n'
                s += str(token)
                raise ParseFatalException(s)

        # inside function decl
        elif self._state == self.INSIDE:
            if isinstance(token, Conditional):
                self._debug_state(token)
                self._fn.append_token(token)
            elif isinstance(token, ScopeBegin):
                self._debug_state(token)
                self._fn.append_token(token)
                self._depth += 1
                st.scope_push()
            elif isinstance(token, ScopeEnd):
                self._fn.append_token(token)
                self._depth -= 1
                st.scope_pop()
                if self._depth == 0:
                    self._debug_state(token, self.OUTSIDE)
                    self._state = self.OUTSIDE
                    st.new_symbol(self._fn)
                    return self._fn
            elif isinstance(token, Label):
                # TODO: register the label with the global label list
                self._debug_state(token)
                self._fn.append_token(token)
            elif isinstance(token, FunctionCall):
                self._debug_state(token)
                self._fn.append_token(token)
                self._fn.add_dependency(token.get_name())
            elif isinstance(token, FunctionReturn):
                self._debug_state(token)
                self._fn.append_token(token)
            elif isinstance(token, Variable):
                self._debug_state(token)
                self._debug_state(token)
                st.new_symbol(token)
                self._fn.append_token(token)
            else:
                self._debug_state(token, self.ERROR)
                self._state = self.ERROR
                s = 'invalid token in body of function\n'
                s += str(self._fn) + '\n'
                s += '%s: %s' % (type(token), str(token))
                raise ParseFatalException(s)

        return None

    def _parse(self, tokens):
        """ go through the list of tokens looking for well structred functions
        """
        self._state = self.OUTSIDE
        self._fn = None
        self._depth = 0
        out_tokens = []
        for t in tokens:
            token = self._next_state(t)
            if token != None:
                out_tokens.append(token)

        return out_tokens

    def get_output(self):
        return self._get_tokens()

    def get_scanner_output(self):
        return self._scanned_tokens

    def get_parser_output(self):
        return self._parsed_tokens

    def compile(self, tokens, debug=False):
        # first we tokenize
        self._scanned_tokens = self._scan(tokens)

        # now we need to run the parsed tokens to the structure builder
        # this populates the symbol table and builds complete functions
        tmp = self._debug
        self._debug = debug
        self._tokens = self._parse(self._scanned_tokens) 
        self._debug = tmp

        return self._tokens
