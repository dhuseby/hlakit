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

import copy
from session import Session
from symboltable import SymbolTable

class PPLexer(object):

    # basic preprocessor tokens
    preprocessor = {
        'define':       'PP_DEFINE',
        'undef':        'PP_UNDEF',
        'ifdef':        'PP_IFDEF',
        'ifndef':       'PP_IFNDEF',
        'else':         'PP_ELSE',
        'endif':        'PP_ENDIF',
        'include':      'PP_INCLUDE',
        'incbin':       'PP_INCBIN',
        'todo':         'PP_TODO',
        'warning':      'PP_WARNING',
        'error':        'PP_ERROR',
        'fatal':        'PP_FATAL'
    }

    rtokens     = [ 'HASH',
                    'STRING',
                    'BSTRING',
                    'DECIMAL',
                    'KILO',
                    'HEXC',
                    'HEXS',
                    'BINARY',
                    'ID',
                    'WS',
                    'NL',
                    'BS' ] 

    # the tokens list
    tokens      = rtokens \
                + list(set(preprocessor.values()))

    literals    = '.+-*/~!%><=&^|{}()[]:,'

    t_HASH      = r'\#'
    t_STRING    = r'\"(\\.|[^\"])*\"'
    t_BSTRING   = r'\<(\\.|[^\>])*\>'
    t_DECIMAL   = r'\b(0|[1-9][0-9]*)\b'
    t_KILO      = r'\b(0|[1-9][0-9]*)[kK]\b'
    t_HEXC      = r'0x[0-9a-fA-F]+'
    t_HEXS      = r'\$[0-9a-fA-F]+'
    t_BINARY    = r'%[01]+'

    def t_NL(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_BS(self, t):
        r'\\'
        return t

    def t_WS(self, t):
        r'\s+'
        # eat whitespace

    def t_COMMENT(self, t):
        r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
        t.lexer.lineno += t.value.count("\n")
        # eat comments

    def t_ID(self, t):
        r'[a-zA-Z_][\w]*'

        value = t.value.lower()

        t.type = self.preprocessor.get(value, None) # check for preprocessor words
        if t.type != None:
            t.value = value
            return t

        """
        # the token is a normal ID...we need to expand it if it is a macro name
        exp = SymbolTable().lookup_symbol(t.value)
        ret = []
        if exp != None:

            # so this is where it gets tricky...we need to return the first token
            # and splice the rest into the lexer's stream at the correct place

            # now splice in the new text and adjust things
            toklen = len(t.value)
            splice_start = t.lexer.lexpos - toklen 
            splice_end = t.lexer.lexpos

            # build a temporary lexer so we can get the first token of the macro value string
            splice_str = ' '.join(exp.value)
            tmplexer = Session().pp_lexer(Session().is_debug())
            tmplexer.input(splice_str)

            # get the first token
            tmptok = tmplexer.token()

            # copy it's type and value to the token we're going to return
            t.original_value = t.value
            t.type = tmptok.type
            t.value = tmptok.value
           
            # splice the string in and adjust the lexpos
            t.lexer.lexdata = t.lexer.lexdata[:splice_start] + splice_str + t.lexer.lexdata[splice_end:]
            # adjust the current lexpos
            t.lexer.lexlen = len(t.lexer.lexdata)
            t.lexer.lexpos = min((splice_start + len(t.value)), (t.lexer.lexlen - 1))

            # return the first token
            return t
        """

        t.type = 'ID'
        return t

    def t_error(self, t):
        t.type = t.value[0]
        t.value = t.value[0]
        t.lexer.skip(1)
        return t

    def __init__(self):
        pass

