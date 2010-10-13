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
from symbol import Symbol
from variable import Variable
from functioncall import FunctionCall

class Function(Symbol):
    """
    Encapsulates Functions
    """

    def __init__(self, decl):
        super(Function, self).__init__(decl.get_name(), decl.get_fn_type())
        self._decl = decl
        self._tokens = []
        self._dependencies = []
        self._scope_name = None
        self._start_label = None

    def get_noreturn(self):
        return self._decl.get_noreturn()

    def get_params(self):
        return self._decl.get_params()

    def get_type(self):
        return self._decl.get_type()

    def get_interrupt_name(self):
        if self._decl.get_type().get_name() != 'interrupt':
            return None
        return self._decl.get_type().get_sub_type()

    def get_name(self):
        return self._decl.get_name()
    
    def set_scope(self, name):
        self._scope_name = name

    def get_scope(self):
        return self._scope_name

    def append_token(self, token):
        self._tokens.append(token)
        if isinstance(token, FunctionCall):
            token.set_scope(self.get_scope())
            self.add_dependency(token)
        elif isinstance(token, Variable):
            token.set_scope(self.get_scope())

    def get_tokens(self):
        return self._tokens

    def add_dependency(self, fn):
        fnname = str(fn.get_name())
        if fnname in self._dependencies:
            return

        # add it to the list
        self._dependencies.append(fn)

    def get_dependencies(self):
        return self._dependencies

    def set_start_label(self, label):
        self._start_label = label

    def get_start_label(self):
        return self._start_label

    def get_address(self):
        if self._start_label != None:
            return self._start_label.get_address()
        return None

    def __str__(self):
        return str(self._decl)

