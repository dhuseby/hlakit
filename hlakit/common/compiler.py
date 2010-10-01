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
import copy
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
from conditionaldecl import ConditionalDecl
from codeblock import CodeBlock
from filemarkers import FileBegin, FileEnd
from scopemarkers import ScopeBegin, ScopeEnd
from symboltable import SymbolTable
from variableinitializer import VariableInitializer

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

    def reset_state(self):
        self.set_exprs(self.__class__.exprs())
        self._tokens = []

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

    def _push_scope(self, scope):
        self._scope_stack.insert(0, [scope, 0])

    def _pop_scope(self):
        scope = self._scope_stack.pop(0)
        return (scope[0], scope[1])

    def _increment_depth(self):
        self._scope_stack[0][1] += 1

    def _decrement_depth(self):
        self._scope_stack[0][1] -= 1

    def _get_depth(self):
        return self._scope_stack[0][1]

    def _get_scope_context(self):
        return self._scope_stack[0][0]

    def _append_token_to_scope(self, token):
        self._get_scope_context().append_token(token)

    def _scope_depth(self):
        return len(self._scope_stack)

    def _peek_token(self):
        return self._in_tokens[0]

    def _get_token(self):
        return self._in_tokens.pop(0)

    def _put_token(self, token):
        self._in_tokens.insert(0, token)

    def _parse_next(self):

        st = SymbolTable()

        # NOTE: we handle adding the symbols to the symbol table here rather
        # than in the Variable/Function classes themeselve so that we can
        # define them in the proper scope.  This function uses a state machine
        # to track the scope and therefore properly define the symbols...

        # get the next token
        token = self._get_token()

        if isinstance(token, FunctionDecl):

            # make sure all functions are declared at file scope
            if self._scope_depth() != 0:
                raise ParseFatalError('cannot declare a function here')

            # create the function container
            fn = Function(token)

            self._push_scope(fn)

            # get the next token, it should be ScopeBegin
            token = self._get_token()
            if isinstance(token, ScopeBegin):
                self._append_token_to_scope(token)
                self._increment_depth()

                # set the current symbol table scope to the function
                st.scope_push(str(fn.get_name()))

                # set the function's full scope name to the current scope
                fn.set_scope(st.current_scope_name())
            else:
                s = 'function decl not followed by {\n'
                s += str(fn) + '\n'
                s += str(token)
                raise ParseFatalException(s)

        elif isinstance(token, Variable):
            st.new_symbol(token)

            # peek at the next token to see if it is an initializer
            next_token = self._peek_token()
            if isinstance(next_token, VariableInitializer):
                # assign the value to the variable
                token.set_value(next_token.get_value())
                # consume the initializer token
                self._get_token()

            # return the Variable token
            return token
        
        elif isinstance(token, FileBegin):
            # set the symbol table scope to the file
            st.scope_push(str(token.get_name()))
            return None
        
        elif isinstance(token, FileEnd):
            # end the file scope 
            st.scope_pop()
            return None
       
        # this is a standalone { token to localize names
        elif isinstance(token, ScopeBegin):
            self._increment_depth()
            self._append_token_to_scope(token)

            # start a new symbol table scope but not a fn/cond scope
            st.scope_push()
            return None

        elif isinstance(token, ScopeEnd):
            self._append_token_to_scope(token)
            self._decrement_depth()
            if self._get_depth() == 0:

                # end the symbol table scope 
                st.scope_pop()

                (token, depth) = self._pop_scope()

                # if we were defining a function, then add it as a symbol
                if isinstance(token, Function):
                    st.new_symbol(token)

                # if we're back to the top level of scope (file scope),
                # then return the token, otherwise add it to the 
                # containing scope...
                if self._scope_depth() == 0: 
                    return token
                else:
                    self._append_token_to_scope(token)
            return None

        elif isinstance(token, Label):
            # pass labels through unchanged because they will be resolved
            # into an address during the resolve phase
            self._append_token_to_scope(token)
            return None

        elif isinstance(token, FunctionCall):
            self._append_token_to_scope(token)
            return None

        elif isinstance(token, FunctionReturn):
            self._append_token_to_scope(token)
            return None

        else:
            # this allows all other tokens to pass through...thus we can
            # let the ROM building preprocessr tokens to get through to
            # the ROM building phase.
            return token

        return None

    def _parse(self, tokens):
        """ go through the list of tokens looking for well structred functions
        """
        self._scope_stack = []
        self._in_tokens = copy.copy(tokens)
        self._parsed_tokens = []
        while True:
            token = self._parse_next()
            if token != None:
                self._parsed_tokens.append(token)

            if len(self._in_tokens) == 0:
                break

    def _resolve_token(self, token):
        st = SymbolTable()

        if isinstance(token, Function):
            tokens = []
            fn = token

            # start all functions with a label
            tokens.append(Label(fn.get_name()))

            # then append it's tokens and count them as unresolved
            tokens.extend(fn.get_tokens())

            # return the tokens and let
            return (tokens, len(fn.get_tokens()))

        elif isinstance(token, FunctionCall):
            tokens = []

            # look up the function call
            fn = st[token.get_name()]
            fn_type = fn.get_type().get_name()

            if fn_type == 'inline':
                # paste the body of the inline function here, alias
                # the function parameters to the function variables
                # so they can be resolved.
                pass
            elif fn_type == 'function':
                # create an instruction line that calls the function
                pass
            else:
                raise ParseFatalException('invalid function type called')

        return (token, 0)


    def _resolve(self, tokens):
        """ go through the parsed tokens and convert to all instruction lines
        and iterate through, resolving references until everything is resolved
        as much as can be.
        """
        out_tokens = tokens
        while True:
            left_to_resolve = 0
            round_tokens = []
            for t in out_tokens:
                # try to resolve the token
                (token, unresolved) = self._resolve_token(t)

                # count how many are left to resolve
                left_to_resolve = left_to_resolve + unresolved

                # process what we get back
                if isinstance(token, list):
                    round_tokens.extend(token)
                else:
                    out_tokens.append(token)

            # if nothing left to resolve, then we are done
            if left_to_resolve == 0:
                return round_tokens

            # otherwise, go around for another pass 
            out_tokens = round_tokens

    def get_output(self):
        return self._get_tokens()

    def get_scanner_output(self):
        return self._scanned_tokens

    def get_parser_output(self):
        return self._parsed_tokens

    def get_resolver_output(self):
        return self._resolved_tokens

    def compile(self, tokens, debug=False):
        # first we tokenize
        self._scanned_tokens = self._scan(tokens)

        # now we need to run the parsed tokens to the structure builder
        # this populates the symbol table and builds complete functions
        self._parse(self._scanned_tokens)

        # now resolve all references and convert everything to instruction lines
        #self._resolved_tokens = self._resolve(self._parsed_tokens)

        #return self._resolved_tokens
