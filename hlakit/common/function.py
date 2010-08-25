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

class Function(object):
    """
    Encapsulates Functions
    """

    def __init__(self, decl):
        super(Function, self).__init__(decl.get_name())
        self._decl = decl
        self._tokens = []
        self._dependencies = []

    def get_noreturn(self):
        return self._decl.get_type().get_noreturn()

    def get_params(self):
        return self._decl.get_params()

    def get_type(self):
        # returns 'inline', 'function', or 'interrupt'
        type_ = self._decl.get_type().get_type()
        name = self.get_interrupt_name()

        if name != None:
            return '%s.%s' % (type_, name)

        return type_

    def get_interrupt_name(self):
        if self._decl.get_type().get_type() != 'interrupt':
            return None
        return self._decl.get_type().get_name()

    def get_name(self):
        return self._decl.get_name()

    def append_token(self, token):
        self._tokens.append(token)

    def get_tokens(self):
        return self._tokens

    def add_dependency(self, fnname):
        fn = '%s' % fnname
        if fn in self._dependencies:
            return
        self._dependencies.append(fn)

    def __str__(self):
        s = ''
        s += self.get_type() + ' '
        s += str(self.get_name())
        s += '('
        if self.get_params():
            for i in range(0, len(self.get_params())):
                if i > 0:
                    s += ','
                s += ' ' + str(self.get_params()[i])
            s += ' '
        s += ')\n'
        for t in self._tokens:
            s += str(t) + '\n'
        return s

