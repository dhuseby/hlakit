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

from collections import defaultdict
from exceptions import NotImplementedError, Exception
import ply.lex as lex

class Lexer(object):

    # the lexer states behave like so:
    #  INITIAL    the default lexer state parses NL, ID, WS, STRING, NUMBER
    #             tokens.  NL tokens increment lexer.lineno.  WS tokens are
    #             eaten.  STRING tokens have their quotes removed.  NUMBER
    #             token values are converted to int.  ID callbacks are called
    #             for standalone ID's as well as ID's that follow # literals.
    #  RAW        this state returns all NL, ID, WS, STRING, and NUMBER
    #             tokens. instances of \NL (slash followed by newline) are
    #             considered line continuations and not processed like a
    #             normal newline.  it does not call any ID callbacks.
    #  NORESOLVE  this state is exactly like the INITIAL state except that
    #             it does not call any of the ID callbacks.
    #  IGNORE     this state eats all tokens except NL.  it does ID callbacks
    #             for ID's that follow # literals.
    states = [ ('RAW',          'inclusive'),
               ('NORESOLVE',    'inclusive'),
               ('IGNORE',       'exclusive' ) ]

    # the lexer understands and tokenizes the following tokens.
    tokens = [
        'NL',
        'WS',
        'ID',
        'STRING',
        'NUMBER'
    ]

    def __init__(self):
        self._lexers = []
        self._callbacks = defaultdict(list)

    def push_lex_context(self, d, state='INITIAL'):
        lineno = self.lexer.lineno
        lexer = lex.lex(object=self)
        lexer.lineno = lineno
        lexer.begin(state)
        lexer.input(d)
        self._lexers.append((lexer, self.file))

    def push_lex_context_file(self, f, state='INITIAL'):
        in_file = open(f, 'r')
        in_data = in_file.read()
        in_file.close()
        lexer = lex.lex(object=self)
        lexer.input(in_data)
        self._lexers.append((lexer, f))

    def pop_lex_context(self):
        if len(self._lexers) == 0:
            return None
        return self._lexers.pop()

    @property
    def lexer(self):
        if len(self._lexers) > 0:
            return self._lexers[-1][0]
        return None

    # this makes the lexer property read-only
    @lexer.setter
    def lexer(self, l):
        pass

    @property
    def file(self):
        if len(self._lexers) > 0:
            return self._lexers[-1][1]
        return None

    # this makes the file property read-only
    @file.setter
    def file(self, f):
        pass

    @property
    def line(self):
        if len(self._lexers) > 0:
            return self._lexers[-1][0].lineno
        return None

    # this makes the line property read-only
    @line.setter
    def line(self, l):
        pass

    def token(self):
        while True:
            if self.lexer is None:
                # we're done
                return None
            t = self.lexer.token()
            if not t:
                self.pop_lex_context()
            else:
                return t

    def scan(self):
        tokens = []
        while True:
            try:
                t = self.token()
                if not t:
                    break
                tokens.append(t)
            except Exception, e:
                import pdb; pdb.set_trace()
                print "%s" % e
        return tokens

    def register_callbacks(self, obj):
        # merge tokens
        self.tokens += obj.tokens

        # hook up callbacks
        for cb in obj.callbacks:
            cb_list = self._callbacks.get(cb[0], [])
            cb_list.append(cb[1])
            self._callbacks[cb[0]] = cb_list

    def _do_callback(self, name, *pargs):
        t = None
        cb_list = self._callbacks.get(name, [])
        for cb in cb_list:
            (handled, t) = cb( *pargs )
            if handled:
                break
        return t

    def t_ANY_NL(self, t):
        r'\n'
        t.lexer.lineno += 1
        return t

    def t_IGNORE_NL(self, t):
        r'\n'
        # we still need to match newlines so that our lineno value gets updated correctly
        t.lexer.lineno += 1
        # eat the newline

    def t_RAW_SLASHNL(self, t):
        r'\\\n'
        # when in RAW state, eat slash-newline combos
        t.value = "\n"
        t.lexer.lineno += 1
        return t

    def t_WS(self, t):
        r'\s+'
        # eat whitespace

    def t_RAW_WS(self, t):
        r'\s'
        # when in 'ppraw' state, don't eat whitespace
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][\w]*'
        # check for a reserved word
        cb_name = '_'.join([t.lexer.lexstate, t.type])
        return self._do_callback(cb_name, self, t)

    def t_HASH(self, t):
        r'\#'
        cb_type = '_'.join([t.lexer.lexstate, t.type])
        return self._do_callback(cb_type, self, t)

    def t_IGNORE_HASH(self, t):
        r'\#'
        cb_type = '_'.join([t.lexer.lexstate, t.type])
        return self._do_callback(cb_type, self, t)

    def t_STRING(self, t):
        r'\"(\\.|[^\"])*\"'
        cb_type = '_'.join([t.lexer.lexstate, t.type])
        return self._do_callback(cb_type, self, t)

    def t_DECIMAL(self, t):
        r'\b(0|[1-9][0-9]*)\b'
        cb_type = '_'.join([t.lexer.lexstate, t.type])
        return self._do_callback(cb_type, self, t)

    def t_KILO(self, t):
        r'\b(0|[1-9][0-9]*)[kK]\b'
        cb_type = '_'.join([t.lexer.lexstate, t.type])
        return self._do_callback(cb_type, self, t)

    def t_HEXC(self, t):
        r'0x[0-9a-fA-F]+'
        cb_type = '_'.join([t.lexer.lexstate, t.type])
        return self._do_callback(cb_type, self, t)

    def t_HEXS(self, t):
        r'\$[0-9a-fA-F]+'
        cb_type = '_'.join([t.lexer.lexstate, t.type])
        return self._do_callback(cb_type, self, t)

    def t_BINARY(self, t):
        r'%[01]+'
        cb_type = '_'.join([t.lexer.lexstate, t.type])
        return self._do_callback(cb_type, self, t)

    def t_IGNORE_CHARS(self, t):
        r'[^\n\#]+'
        # when in IGNORE, we eat all characters except the newlines and # literals
        pass

    def t_error(self, t):
        t.type = t.value[0]
        t.value = t.value[0]
        t.lexer.skip(1)
        return t

    def t_IGNORE_error(self, t):
        t.type = t.value[0]
        t.value = t.value[0]
        t.lexer.skip(1)
        return t


class LexerError(Exception):

    def __init__(self, lexer, **kwargs):
        import pdb; pdb.set_trace()
        super(LexerError, self).__init__(**kwargs)
        # TODO: pull state from lexer

    def __str__(self):
        return super(LexerError, self).__str__()

