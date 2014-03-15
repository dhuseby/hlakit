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

import types

from ..platform import Platform
from ..lexer import Lexer, LexerError
from ..symboltable import SymbolTable

PLATFORM_CLASS = 'Lynx'
CPUS = ['mos65sc02']

class LynxCPU(object):

    reserved = {
        'interrupt'     : 'INTERRUPT'
    }

    tokens = list(reserved.values())

    @property
    def callbacks(self):
        return { ( 'NORESOLVE_ID',      self._ni_id ),
                 ( 'INITIAL_ID',        self._ni_id   ) }

    def _ni_id(self, l, t):
        t.type = self.reserved.get( t.value, 'ID' )
        if t.type != 'ID':
            # it's an 'interrupt' keyword, make sure the next token isn't '.'
            cl = l.lexer.clone()
            ntok = cl.token()
            if ntok.type == '.':
                raise LexerError(l)

            return (True, t)

        # not one of our reserved words or a defined macro name
        # so we don't handle it
        return (False, t)


class LynxPreprocessor(object):

    # the symbol table namespace for the lynx
    NAMESPACE = '__LYNX_HEADER__'

    # this class needs to register these as #<keyword> callbacks
    # with the lexer object that is passed into the regiser function
    # these will use register_preprocessor call to hook up the callbacks
    reserved = {
        'rom'           : 'ROM',
        'ram'           : 'RAM',
        'loader'        : 'LOADER',
        'lnx'           : 'LNX',
        # lnx
        'version'       : 'VERSION',
        'name'          : 'NAME',
        'manufacturer'  : 'MANUFACTURER',
        'rotation'      : 'ROTATION',
        'banks'         : 'BANKS',
        'block_count'   : 'BLOCKS',
        'block_size'    : 'BLOCKSIZE',
        'off'           : 'OFF',
        # rom
        'bank'          : 'BANK',
        'blockof'       : 'BLOCKOF',
        # rom, ram, loader
        'org'           : 'ORG',
        'end'           : 'END'
    }

    tokens = list(reserved.values())

    def __init__(self):
        SymbolTable().new_namespace( self.NAMESPACE, None )

    @property
    def callbacks(self):
        return { ( 'NORESOLVE_ID',      self._ni_id    ),
                 ( 'INITIAL_ID',        self._ni_id    ),
                 ( 'INITIAL_HASH',      self._rni_hash ) }

    @property
    def handlers(self):
        return {
            'LNX': {
                'VERSION'      : self._lnx_version,
                'NAME'         : self._lnx_name,
                'MANUFACTURER' : self._lnx_manufacturer,
                'ROTATION'     : self._lnx_rotation,
                'BANKS'        : self._lnx_banks,
                'BLOCKS'       : self._lnx_block_count,
                'BLOCKSIZE'    : self._lnx_block_size,
                'OFF'          : self._lnx_off
            },
            'ROM': {
                'BANK'         : self._rom_bank,
                'ORG'          : self._rom_org,
                'END'          : self._rom_end,
                'BLOCKOF'      : self._rom_blockof
            },
            'RAM': {
                'ORG'          : self._ram_org,
                'END'          : self._ram_end
            },
            'LOADER': {
                'ORG'          : self._loader_org,
                'END'          : self._loader_end
            }
        }

    def _new_symbol(self, name, value):
        st = SymbolTable()
        st.new_symbol( name, value, self.NAMESPACE )

    def _del_symbol(self, name):
        st = SymbolTable()
        st.del_symbol( name, self.NAMESPACE )

    def _lookup_symbol(self, name):
        st = SymbolTable()
        return st.lookup_symbol( name, self.NAMESPACE )

    def _ni_id(self, l, t):
        t.type = self.reserved.get( t.value, 'ID' )
        if t.type != 'ID':
            # it is one of our reserved words, so we handle it
            return (True, t)

        # not one of our reserved words or a defined macro name
        # so we don't handle it
        return (False, t)

    def _rni_hash(self, l, t):
        if t.lexer.lexstate in ('RAW', 'NORESOLVE'):
            # don't do immediate processing when in RAW or NORESOLVE state
            t.type = 'ID'
            return (True, t)

        # peek at next token
        cl = l.lexer.clone()

        handler = self.handlers
        while type(handler) is types.DictType:
            ntok = cl.token()
            if ntok.value == '.':
                continue
            handler = handler.get(ntok.type, None)

        # is it ours?
        if handler is None:
            return (False, t)

        # call our handler function
        return handler(l, t, ntok, cl)

    def _lnx_version(self, l, t, ntok, cl):
        v = cl.token()
        if v.type != 'NUMBER':
            raise LexerError(l)
        if v.value not in ( 1,2 ):
            raise LexerError(l)
        self._new_symbol(ntok.type, v.value)
        l.token() # lnx
        l.token() # '.'
        l.token() # version
        l.token() # NUMBER
        return (True, l.token())

    def _lnx_name(self, l, t, ntok, cl):
        v = cl.token()
        if v.type != 'STRING':
            raise LexerError(l)
        self._new_symbol(ntok.type, v.value)
        l.token() # lnx
        l.token() # '.'
        l.token() # name
        l.token() # STRING
        return (True, l.token())

    def _lnx_manufacturer(self, l, t, ntok, cl):
        v = cl.token()
        if v.type != 'STRING':
            raise LexerError(l)
        self._new_symbol(ntok.type, v.value)
        l.token() # lnx
        l.token() # '.'
        l.token() # manufacturer
        l.token() # STRING
        return (True, l.token())

    def _lnx_rotation(self, l, t, ntok, cl):
        v = cl.token()
        if v.type != 'STRING':
            raise LexerError(l)
        if v.value.lower() not in ('none', 'left', 'right'):
            raise LexerError(l)
        self._new_symbol(ntok.type, v.value)
        l.token() # lnx
        l.token() # '.'
        l.token() # rotation
        l.token() # STRING
        return (True, l.token())

    def _lnx_banks(self, l, t, ntok, cl):
        v = cl.token()
        if v.type != 'NUMBER':
            raise LexerError(l)
        if v.value not in ( 1,2 ):
            raise LexerError(l)
        self._new_symbol(ntok.type, v.value)
        l.token() # lnx
        l.token() # '.'
        l.token() # banks
        l.token() # NUMBER
        return (True, l.token())

    def _lnx_block_count(self, l, t, ntok, cl):
        v = cl.token()
        if v.type != 'NUMBER':
            raise LexerError(l)
        if v.value not in ( 256,512 ):
            raise LexerError(l)
        self._new_symbol(ntok.type, v.value)
        l.token() # lnx
        l.token() # '.'
        l.token() # block_count
        l.token() # NUMBER
        return (True, l.token())

    def _lnx_block_size(self, l, t, ntok, cl):
        v = cl.token()
        if v.type != 'NUMBER':
            raise LexerError(l)
        if v.value not in ( 256,512,1024,2048,4096 ):
            raise LexerError(l)
        self._new_symbol(ntok.type, v.value)
        l.token() # lnx
        l.token() # '.'
        l.token() # block_size
        l.token() # NUMBER
        return (True, l.token())

    def _lnx_off(self, l, t, ntok, cl):
        self._new_symbol(ntok.type, True)
        l.token() # lnx
        l.token() # '.'
        l.token() # off
        return (True, l.token())

    def _rom_bank(self, l, t, ntok, cl):
        return (False, l.token())

    def _rom_org(self, l, t, ntok, cl):
        return (False, l.token())

    def _rom_end(self, l, t, ntok, cl):
        return (False, l.token())

    def _rom_blockof(self, l, t, ntok, cl):
        return (False, l.token())

    def _ram_org(self, l, t, ntok, cl):
        return (False, l.token())

    def _ram_end(self, l, t, ntok, cl):
        return (False, l.token())

    def _loader_org(self, l, t, ntok, cl):
        return (False, l.token())

    def _loader_end(self, l, t, ntok, cl):
        return (False, l.token())


