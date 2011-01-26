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

class TypeRegistry(object):

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def __init__(self):
        if not hasattr(self, '_types'):
            self.reset_state()

    def reset_state(self):
        self._types = {}
        types = Session().basic_types()
        if types:
            for t in types:
                self._types[str(t)] = t

    def __getitem__(self, t):
        if str(t) in self._types:
            return self._types[str(t)]
        return None

    def __setitem__(self, name, t):
        self._types[name] = t


class Type(object):
    """
    The type of a variable
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'type_' in tokens.keys():
            t = TypeRegistry()[str(tokens.type_)]
            if t is None:
                # create the new type
                return klass(str(tokens.type_))
            else:
                # otherwise return the one we found
                return t
        
        raise ParseFatalException('no type specified')

    @classmethod
    def exprs(klass):
        ops = Session().opcodes()
        kwds = Session().keywords()
        conds = Session().conditions()

        # build the proper expression for detecting types
        type_expr = None
        if ops:
            type_expr = ~ops
        if kwds:
            if type_expr:
                type_expr += ~kwds
            else:
                type_expr = ~kwds
        if conds:
            if type_expr:
                type_expr += ~conds
            else:
                type_expr = ~conds
        if type_expr:
            type_expr += Word(alphas, alphanums + '_').setResultsName('type_')
        else:
            type_expr = Word(alphas, alphanums + '_').setResultsName('type_')

        type_expr.setParseAction(klass.parse)
        return type_expr

    def __init__(self, name, size=None):
        self._name = name
        self._size = size

        tr = TypeRegistry()
        t = tr[name]
        if t is None:
            # the type is not registered...
            if size is None:
                #import pdb; pdb.set_trace()
                raise ParseFatalException('defining new type without size: %s' % name)
            # add the type to the TypeRegistry
            #print 'registering type: %s (size: %d)' % (name, size)
            tr[name] = self
        else:
            # the type is already registered, so get its size if needed
            if size is None:
                self._size = t.get_size()
            else:
                if size != t.get_size():
                    raise ParseFatalException('specifying a size for an already defined type: %s' % name)

    def is_alias(self):
        return False

    def get_name(self):
        return self._name

    def get_size(self):
        return self._size

    def __str__(self):
        return self._name

    def __cmp__(self, t):
        return cmp(self._name, t)

    __repr__ = __str__

