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
from pyparsing import *
from symbol import Symbol

class Scope(dict):

    def __init__(self, namespace=None):
        self._namespace = {}

    def get_namespace(self):
        return self._namespace

class SymbolTable(object):

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def reset_state(self):
        self._scope_stack = [Scope()]

    def scope_push(self, namespace=None):
        self._scope_stack.insert(Scope(namespace), 0)

    def scope_pop(self):
        if len(self._scope_stack) <= 1:
            raise ParseFatalException('can\'t pop scope from empty scope stack')
        self._scope_stack.pop(0)

    def scope_top(self):
        return self._scope_stack[0]

    def scope_global(self):
        return self._scope_stack[-1]

    def __getitem__(self, name):
        """ Scan through the scope frames from most local to most global
        looking for the symbol they client is asking for"""

        for i in range(0, len(self._scope_stack)):
            if self._scope_stack[i].has_key(name):
                return self._scope_stack[i][name]

        return None

    def __setitem__(self, name, symbol):
        # this is for updating an already defined symbol 
        for i in range(0, len(self._scope_stack)):
            if self._scope_stack[i].has_key(name):
                self._scope_stack[i][name] = symbol

    def new_symbol(self, symbol):
        # This is used to define a new symbol in the current scope
        self._scope_stack[0][symbol.get_name()] = symbol

