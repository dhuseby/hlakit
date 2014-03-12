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
import sys
import random

from lexer import Lexer, LexerError
from symboltable import SymbolTable
from paths import Paths
from buffers import Buffers

class Preprocessor(object):

    # the symbtol table namespace for macro definitions
    NAMESPACE = '__PREPROCESSOR_MACROS__'

    # these need to be refactored to be in a "General" preprocesor
    # object that gets registered with the preprocessor.
    reserved = {
        'define'        : 'DEFINE',
        'undef'         : 'UNDEF',
        'ifdef'         : 'IFDEF',
        'ifndef'        : 'IFNDEF',
        'else'          : 'ELSE',
        'endif'         : 'ENDIF',
        'todo'          : 'TODO',
        'warning'       : 'WARNING',
        'error'         : 'ERROR',
        'fatal'         : 'FATAL',
        'include'       : 'INCLUDE',
        'incbin'        : 'INCBIN',
        'usepath'       : 'USEPATH',
        'lo'            : 'LO',
        'hi'            : 'HI',
        'nylo'          : 'NYLO',
        'nyhi'          : 'NYHI',
        'sizeof'        : 'SIZEOF',
        'setpad'        : 'SETPAD'
    }

    tokens = [
        'IMMEDIATE'
    ] + list(reserved.values())

    def __init__(self):
        st = SymbolTable()
        st.new_namespace( self.NAMESPACE, None )

    @property
    def callbacks(self):
        return { ( 'RAW_ID',            self._raw_id       ),
                 ( 'NORESOLVE_ID',      self._noresolve_id ),
                 ( 'INITIAL_ID',        self._initial_id   ),
                 ( 'IGNORE_HASH',       self._ignore_hash  ),
                 ( 'RAW_STRING',        self._rni_string   ),
                 ( 'NORESOLVE_STRING',  self._rni_string   ),
                 ( 'INITIAL_STRING',    self._rni_string   ),
                 ( 'RAW_DECIMAL',       self._rni_decimal  ),
                 ( 'NORESOLVE_DECIMAL', self._rni_decimal  ),
                 ( 'INITIAL_DECIMAL',   self._rni_decimal  ),
                 ( 'RAW_KILO',          self._rni_kilo     ),
                 ( 'NORESOLVE_KILO',    self._rni_kilo     ),
                 ( 'INITIAL_KILO',      self._rni_kilo     ),
                 ( 'RAW_HEXC',          self._rni_hexc     ),
                 ( 'NORESOLVE_HEXC',    self._rni_hexc     ),
                 ( 'INITIAL_HEXC',      self._rni_hexc     ),
                 ( 'RAW_HEXS',          self._rni_hexs     ),
                 ( 'NORESOLVE_HEXS',    self._rni_hexs     ),
                 ( 'INITIAL_HEXS',      self._rni_hexs     ),
                 ( 'RAW_BINARY',        self._rni_binary   ),
                 ( 'NORESOLVE_BINARY',  self._rni_binary   ),
                 ( 'INITIAL_BINARY',    self._rni_binary   ),
                 ( 'RAW_HASH',          self._rni_hash     ),
                 ( 'NORESOLVE_HASH',    self._rni_hash     ),
                 ( 'INITIAL_HASH',      self._rni_hash     ) }

    @property
    def handlers(self):
        return {
            'NUMBER': self._number,
            'DEFINE': self._define,
            'INCLUDE': self._include,
            'IFDEF': self._ifdef,
            'IFNDEF': self._ifdef,
            'ELSE': self._else,
            'ENDIF': self._endif,
            'INCBIN': self._incbin,
            'UNDEF': self._undef,
            'HI': self._hi,
            'LO': self._lo,
            'NYHI': self._nyhi,
            'NYLO': self._nylo,
            'TODO': self._msgs,
            'WARNING': self._msgs,
            'ERROR': self._msgs,
            'FATAL': self._msgs,
            'SETPAD': self._setpad,
            'USEPATH': self._usepath,
            'SIZEOF': self._sizeof
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

    def _initial_id(self, l, t):
        t.type = self.reserved.get( t.value, 'ID' )
        if t.type != 'ID':
            # it is one of our reserved words, so we handle it
            return (True, t)

        # look up the token to see if it is the name of
        # a preprocessor macro
        symbol = self._lookup_symbol( t.value )

        if symbol != None:
            # we found a macro that needs to be replaced
            data = symbol['value']

            # if the replacement value is empty, just eat the ID token
            if len(data) == 0:
                return

            # push the current lexer state, using the macro value data
            l.push_lex_context( data, l.lexer.lexstate )

            return (True, l.token())

        # not one of our reserved words or a defined macro name
        # so we don't handle it
        return (False, t)

    def _raw_id(self, l, t):
        # in RAW mode we don't do anything, just return the token
        return (True, t)

    def _noresolve_id(self, l, t):
        # in NORESOLVE mode we just check for reserved words
        t.type = self.reserved.get( t.value, 'ID' )
        return (True, t)

    def _ignore_hash(self, l, t):
        cl = l.lexer.clone()
        cl.begin('NORESOLVE')
        ntok = cl.token()

        # we're in the ignore state, we must track IFDEF, IFNDEF, ELSE, and
        # ENDIF so that we know when to get out of the ignore state.
        if ntok.type in ('IFDEF', 'IFNDEF'):
            self._ignore_depth += 1

        if ntok.type == 'ELSE':
            if self._ignore_depth == 0:
                l.lexer.pop_state()
                # eat the else token
                l.token()

        if ntok.type == 'ENDIF':
            self._ignore_depth -= 1
            if self._ignore_depth == 0:
                l.lexer.pop_state()
                if l.lexer.lexstate != 'INITIAL':
                    raise LexerError(t.lexer)

        return (True, l.token())

    def _rni_string(self, l, t):
        # remove the double quotes
        t.value = t.value[1:-1]
        return (True, t)

    def _rni_decimal(self, l, t):
        # convert to int
        if t.lexer.lexstate == 'INITIAL':
            t.value = int(t.value)
        t.type = 'NUMBER'
        return (True, t)

    def _rni_kilo(self, l, t):
        # convert to int
        if t.lexer.lexstate == 'INITIAL':
            t.value = int(t.value[0:-1]) * 1024
        t.type = 'NUMBER'
        return (True, t)

    def _rni_hexc(self, l, t):
        # convert to int
        if t.lexer.lexstate == 'INITIAL':
            t.value = int(t.value, 16)
        t.type = 'NUMBER'
        return (True, t)

    def _rni_hexs(self, l, t):
        # covert to int
        if t.lexer.lexstate == 'INITIAL':
            t.value = int(t.value[1:], 16)
        t.type = 'NUMBER'
        return (True, t)

    def _rni_binary(self, l, t):
        # convert to int
        if t.lexer.lexstate == 'INITIAL':
            t.value = int(t.value[1:], 2)
        t.type = 'NUMBER'
        return (True, t)

    def _rni_hash(self, l, t):
        if t.lexer.lexstate in ('RAW', 'NORESOLVE'):
            # don't do immediate processing when in RAW or NORESOLVE state
            t.type = 'ID'
            return (True, t)

        # peek at next token
        cl = l.lexer.clone()
        ntok = cl.token()

        # if we don't handle it, punt to the next callback
        if not self.handlers.has_key(ntok.type):
            return (False, None)

        # otherwise, call our handler function
        handler = self.handlers[ntok.type]
        return handler(l, t, ntok, cl)

    def _number(self, l, t, ntok, cl):
        # immediate values are HASH followed by NUMBER
        l.lexer.token()
        t.type = 'IMMEDIATE'
        t.value = ntok.value
        return (True, t)

    def _define(self, l, t, ntok, cl):
        # get the ID without resolving it (e.g. doing macro expansion)
        cl.begin('NORESOLVE')
        symbol = cl.token()
        if symbol.type != 'ID':
            raise LexerError(l)

        # try to look up the macro definition
        srec = self._lookup_symbol(symbol.value)
        if srec != None:
            print >> sys.stderr, "%s:%d: WARNING: '%s' defined" % (l.file, l.line, symbol.value)
            print >> sys.stderr, "%s:%d: NOTE: this is the location of the previous definition" % (srec['file'], srec['line'])

        # this reads in the macro value until we hit an un-slashed newline
        cl.begin('RAW')
        vtokens = []
        vtoken = cl.token()
        lastpos = vtoken.lexpos
        while vtoken and vtoken.type != 'NL':
            if vtoken.type == 'SLASHNL':
                lastpos += 2
            else:
                lastpos += len(vtoken.value)
            vtokens.append(vtoken.value)
            vtoken = cl.token()

        # build the macro record
        srec = { 'file': l.file,
                 'line': l.line,
                 'id': symbol.value,
                 'value': ''.join(vtokens).strip() }

        # store the macro record
        self._new_symbol( symbol.value, srec )

        # skip over the macro definition in the main stream
        l.lexer.skip(lastpos - ntok.lexpos)

        return (True, None)

    def _include(self, l, t, ntok, cl):
        # peek at the next token
        f = cl.token()
        if f.type != 'STRING':
            raise LexerError(l)

        # eat the INCLUDE and STRING tokens
        l.token()
        l.token()

        filepath = Paths().resolve_filepath( f.value)
        if filepath is None:
            raise LexerError(l)

        # read in the included file
        file_size = os.stat(f.value).st_size

        # if the file is empty, just return nothing
        if file_size == 0:
            return (True, l.token())
        
        # eat the NL token as well
        l.token()

        # push the current lexer state, reading data from the file
        l.push_lex_context_file(f.value, l.lexer.lexstate)

        return (True, l.token())

    def _ifdef(self, l, t, ntok, cl):
        cl.begin('NORESOLVE')
        symbol = cl.token()
        if symbol.type != 'ID':
            raise LexerError(l)

        # eat IFDEF/IFNDEF and ID tokens
        l.lexer.push_state('NORESOLVE')
        l.token()
        l.token()
        l.lexer.pop_state()

        srec = self._lookup_symbol(symbol.value)
        if (ntok.type == 'IFDEF' and srec == None) or (ntok.type == 'IFNDEF' and srec != None):
            # the test failed so we're going into IGNORE state where
            # all tokens are eaten except IFDEF/IFNDEF, ELSE and/or ENDIF.  the
            # ignore depth tracks pairs if IFDEF/IFNDEF, ELSE, and ENDIF so that we
            # know when we've reached the ELSE/ENDIF that matches these IFDEF/IFNDEF
            l.lexer.push_state('IGNORE')
            # we have to reset the ignore depth whenever going into IGNORE state
            self._ignore_depth = 0

        return (True, l.token())

    def _else(self, l, t, ntok, cl):
        # eat the ELSE
        l.token()

        # the IFDEF/IFNDEF that matches this ELSE was true, so we were processing
        # tokens until here.  now we need to switch into the IGNORE state so
        # that all tokens will be ignored until we reach the matching ENDIF
        l.lexer.push_state('IGNORE')

        # we have to reset the ignore depth whenever going into IGNORE state
        self._ignore_depth = 0

        return (True, l.token())

    def _endif(self, l, t, ntok, cl):
        # eat the ENDIF
        l.token()
        # if we get here, then we're in the INITIAL state and this is the matching
        # ENDIF for IFDEF/IFNDEF that evaluated to true, or an ELSE.
        if t.lexer.lexstate != 'INITIAL':
            raise LexerError(l)

        return (True, l.token())

    def _incbin(self, l, t, ntok, cl):
        f = cl.token()
        if f.type != 'STRING':
            raise LexerError(l)

        # eat the INCLUDE and STRING tokens
        l.token()
        l.token()

        filepath = Paths().resolve_filepath( f.value )
        if filepath is None:
            raise LexerError(l)

        # read in the included file
        in_file = open(f.value, 'rb')
        in_data = in_file.read()
        in_file.close()

        # build a byte array from the binary data in hla
        tokens = "byte blob_%d[%d] = {" % (random.randint(0,65535), len(in_data))
        for i in xrange(0, len(in_data)):
            if i > 0:
                tokens += ","
            tokens += hex(ord(in_data[i]))
        tokens += "}\n"

        # process it
        l.push_lex_context(tokens)

        return (True, l.token())

    def _undef(self, l, t, ntok, cl):
        cl.begin('NORESOLVE')
        symbol = cl.token()
        if symbol.type != 'ID':
            raise LexerError(l)

        try:
            self._del_symbol( symbol.value )
        except:
            raise LexerError(l)

        # each the UNDEF and ID
        l.token()
        l.token()

        return (True, l.token())

    def _hi(self, l, t, ntok, cl):
        lparen = cl.token()
        number = cl.token()
        rparen = cl.token()

        if lparen.type != '(' or number.type != 'NUMBER' or rparen.type != ')':
            raise LexerError(l)

        # eat HI, (, NUMBER, ) tokens from main stream
        l.token()
        l.token()
        number = l.token()
        l.token()

        num_size = len(bin(number.value)[2:])
        if num_size <= 8:
            number.value = ((number.value & 0xF0) >> 4)
        elif num_size <= 16:
            number.value = ((number.value & 0xFF00) >> 8)
        elif num_size <= 32:
            number.value = ((number.value & 0xFFFF0000) >> 16)
        else:
            LexerError(l)

        return (True, number)

    def _lo(self, l, t, ntok, cl):
        lparen = cl.token()
        number = cl.token()
        rparen = cl.token()

        if lparen.type != '(' or number.type != 'NUMBER' or rparen.type != ')':
            raise LexerError(l)

        # eat LO, (, NUMBER, ) tokens from main stream
        l.token()
        l.token()
        number = l.token()
        l.token()

        num_size = len(bin(number.value)[2:])
        if num_size <= 8:
            number.value = (number.value & 0x0F)
        elif num_size <= 16:
            number.value = (number.value & 0x00FF)
        elif num_size <= 32:
            number.value = (number.value & 0x0000FFFF)
        else:
            LexerError(l)

        return (True, number)

    def _nyhi(self, l, t, ntok, cl):
        lparen = cl.token()
        number = cl.token()
        rparen = cl.token()

        if lparen.type != '(' or number.type != 'NUMBER' or rparen.type != ')':
            raise LexerError(l)

        # eat NYHI, (, NUMBER, ) tokens from main stream
        l.token()
        l.token()
        number = l.token()
        l.token()

        num_size = len(bin(number.value)[2:])
        if num_size <= 8:
            number.value = ((number.value & 0xF0) >> 4)
        else:
            LexerError(l)

        return (True, number)

    def _nylo(self, l, t, ntok, cl):
        lparen = cl.token()
        number = cl.token()
        rparen = cl.token()

        if lparen.type != '(' or number.type != 'NUMBER' or rparen.type != ')':
            raise LexerError(l)

        # eat NYLO, (, NUMBER, ) tokens from main stream
        l.token()
        l.token()
        number = l.token()
        l.token()

        num_size = len(bin(number.value)[2:])
        if num_size <= 8:
            number.value = (number.value & 0x0F)
        else:
            LexerError(l)

        return (True, number)

    def _msgs(self, l, t, ntok, cl):
        msg = cl.token()
        if msg.type != 'STRING':
            print >> sys.stderr, "%s:" % ntok.type
            # need to eat ntok token from main stream
            l.token()
        else:
            print >> sys.stderr, "%s: %s" % (ntok.type, msg.value)
            # need to eat ntok token and msg token from main stream
            l.token()
            l.token()
        return (True, l.token())

    def _setpad(self, l, t, ntok, cl):
        padding = cl.token()
        if padding.type not in ('STRING', 'NUMBER'):
            raise LexerError(l)
        # store the padding on the current buffer
        Buffers().buffer.padding = padding.value
        l.token()
        l.token()
        return (True, l.token())

    def _usepath(self, l, t, ntok, cl):
        path = cl.token()
        if path.type != 'STRING':
            raise LexerError(l)
        # add the path to the list of search paths
        Paths().add_path(path.value)
        l.token()
        l.token()
        return (True, l.token())

    def _sizeof(self, l, t, ntok, cl):
        lparen = cl.token()
        value = cl.token()
        rparen = cl.token()

        if lparen.type != '(' or value.type not in ('ID', 'IMMEDIATE') or rparen.type != ')':
            raise LexerError(l)

        l.token()
        l.token()
        value = l.token()
        l.token()

        if value.type == 'IMMEDIATE':
            num_size = len(bin(value.value)[2:])
            num_bytes = 1
            while (num_bytes * 8) <= num_size:
                num_bytes += 1
            value.value = num_bytes
        else:
            # TODO: look up the symbol in the current scoped symbol table to get it's type
            value.value = 4
            pass

        value.type = 'IMMEDIATE'
        return (True, value)

