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

from lexer import Lexer, LexerError

class CPU(object):

    reserved = {
        'shared'    : 'SHARED',
        'noreturn'  : 'NORETURN',
        'if'        : 'IF',
        'else'      : 'ELSE',
        'while'     : 'WHILE',
        'do'        : 'DO',
        'loop'      : 'LOOP',
        'switch'    : 'SWITCH',
        'case'      : 'CASE',
        'default'   : 'DEFAULT',
        'function'  : 'FUNCTION',
        'inline'    : 'MACRO',
        'return'    : 'RETURN',
        'struct'    : 'STRUCT',
    }

    tokens = [ 'VARIABLE' ] + list(reserved.values())

    def __init__(self):
        pass

    @property
    def callbacks(self):
        return { ( 'NORESOLVE_ID',      self._ni_id ),
                 ( 'INITIAL_ID',        self._ni_id ) }

    @property
    def handlers(self):
        return {
            'SHARED': self._shared,
            'NORETURN': self._noreturn,
            'IF': self._if,
            'ELSE': self._else,
            'WHILE': self._while,
            'DO': self._do,
            'LOOP': self._loop,
            'SWITCH': self._switch,
            'CASE': self._case,
            'DEFAULT': self._default,
            'FUNCTION': self._function,
            'MACRO': self._macro,
            'RETURN': self._return,
            'STRUCT': self._struct
        }

    def _ni_id(self, l, t):
        t.type = self.reserved.get( t.value, 'ID' )
        if t.type != 'ID' and l.lexer.lexstate == 'INITIAL_ID':
            handler = self.handlers[t.type]
            return handler(l, t)

        # not one of our reserved words so we don't handle it
        return (False, t)

    def _shared(self, l, t):
        shared_obj = l.token()
        if shared_obj.type not in ('VARIABLE', 'FUNCTION'):
            raise LexerError(l)
        # set shared flag
        shared_obj.share = True
        return (True, shared_obj)

    def _noreturn(self, l, t):
        noreturn_fn = l.token()
        if noreturn_fn.type != 'FUNCTION':
            raise LexerError(l)
        # set noreturn flag
        noreturn_fn.noreturn = True
        return (True, noreturn_fn)

    def _if(self, l, t):
        return (True, t)

    def _else(self, l, t):
        return (True, t)

    def _while(self, l, t):
        return (True, t)

    def _do(self, l, t):
        return (True, t)

    def _loop(self, l, t):
        return (True, t)

    def _switch(self, l, t):
        return (True, t)

    def _case(self, l, t):
        return (True, t)

    def _default(self, l, t):
        return (True, t)

    def _function(self, l, t):
        return (True, t)

    def _macro(self, l, t):
        return (True, t)

    def _return(self, l, t):
        return (True, t)

    def _struct(self, l, t):
        return (True, t)

