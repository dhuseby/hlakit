"""
Copyright (c) 2010-2014 David Huseby. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDERS AND CONTRIBUTORS OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of copyright holders and contributors.
"""

import os
from exceptions import KeyError

class SymbolTable(object):
    
    GLOBAL_NAMESPACE = '__global__'

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def _reset_state(self):
        self._scopes = { self.GLOBAL_NAMESPACE: ( None, {} ) }

    def _check_state(self):
        if getattr(self, '_scopes', None) is None:
            self._reset_state()

    def new_namespace(self, namespace, parent=GLOBAL_NAMESPACE):
        self._check_state()

        if self._scopes.has_key(namespace):
            raise KeyError("namespace %s already exists" % namespace)
        self._scopes[namespace] = (parent, {})

    def new_symbol(self, name, value, namespace=GLOBAL_NAMESPACE):
        self._check_state()

        # make sure the namespace exists
        if not self._scopes.has_key(namespace):
            raise KeyError("namespace %s does not exist" % namespace)

        # add the symbol to the namespace
        self._scopes[namespace][1][name] = value
    
    def del_symbol(self, name, namespace=GLOBAL_NAMESPACE):
        self._check_state()

        # make sure the namespace exists
        if not self._scopes.has_key(namespace):
            raise KeyError("namespace %s does not exist" % namespace)

        if self._scopes[namespace][1].has_key(name):
            del self._scopes[namespace][1][name]

    def lookup_symbol(self, name, namespace=GLOBAL_NAMESPACE):
        self._check_state()

        value = None
        while namespace != None:
            value = self._scopes[namespace][1].get(name, None)

            if value != None:
                break
            
            namespace = self._scopes[namespace][0]

        return value

    def dump(self):
        self._check_state()
        import pprint
        for k, v in self._scopes.iteritems():
            print "namespace: %s" % k
            print "parent: %s" % v[0]
            pprint.pprint( v[1] )

