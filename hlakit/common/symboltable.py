"""
HLAKit
Copyright (c) 2010-2011 David Huseby. All rights reserved.

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

class SymbolTable(object):

    ANON_NAMESPACE = '__anonymous__'

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def current_namespace(self):
        return '.'.join(self._scope_stack)

    def reset_state(self):
        self._scope_stack = []
        self._scopes = {}

    def scope_push(self, namespace=ANON_NAMESPACE):
        if not hasattr(self, '_scope_stack'):
            self.reset_state()
        self._scope_stack.append(namespace)

    def scope_pop(self):
        if len(self._scope_stack) <= 1:
            raise ParseFatalException("can't pop scope from empty scope stack")
        self._scope_stack.pop()

    def get_scopes(self):
        return self._scopes

    def new_symbol(self, name, value, namespace=None):
        if namespace is None:
            namespace = self.current_namespace()

        # make sure the scope exists
        if not self._scopes.has_key(namespace):
            self._scopes[namespace] = {}

        # add the symbol to the scope
        self._scopes[namespace][name] = value

    def lookup_symbol(self, name, namespace=None):
        if namespace is None:
            namespace = self.current_namespace()
        ns = namespace.split('.')  

        while len(ns):
            # make sure it is a valid scope
            if not self._scopes.has_key('.'.join(ns)):
                ns.pop()
                continue

            # now grab the scope and check for the symbol
            scope = self._scopes['.'.join(ns)]
            if scope.has_key(name):
                return scope[name]

            # no symbol here, so try the parent scope
            ns.pop()

        # not in any of the scopes
        return None

