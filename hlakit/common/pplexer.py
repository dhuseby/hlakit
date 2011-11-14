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

    tokens      = [ 'PPDEFINE',
                    'PPUNDEF',
                    'PPIFDEF',
                    'PPIFNDEF',
                    'PPELSE',
                    'PPENDIF',
                    'PPINCLUDE',
                    'PPINCBIN',
                    'PPTODO',
                    'PPWARNING',
                    'PPERROR',
                    'PPFATAL',
                    'HASH',
                    'STRING',
                    'BSTRING',
                    'DECIMAL',
                    'KILO',
                    'HEXC',
                    'HEXS',
                    'BINARY',
                    'ID',
                    'NL' ] 

    literals    = '.+-*/~!%><=&^|{}()[]:,'

    # basic conditional compile directives
    t_PPDEFINE  = r'\#(?i)[\t ]*define'
    t_PPUNDEF   = r'\#(?i)[\t ]*undef'
    t_PPIFDEF   = r'\#(?i)[\t ]*ifdef'
    t_PPIFNDEF  = r'\#(?i)[\t ]*ifndef'
    t_PPELSE    = r'\#(?i)[\t ]*else'
    t_PPENDIF   = r'\#(?i)[\t ]*endif'

    # basic include directives
    t_PPINCLUDE = r'\#(?i)[\t ]*include'
    t_PPINCBIN  = r'\#(?i)[\t ]*incbin'

    # common messaging directives
    t_PPTODO    = r'\#(?i)[\t ]*todo'
    t_PPWARNING = r'\#(?i)[\t ]*warning'
    t_PPERROR   = r'\#(?i)[\t ]*error'
    t_PPFATAL   = r'\#(?i)[\t ]*fatal'

    t_HASH      = r'\#'
    t_STRING    = r'\"(\\.|[^\"])*\"'
    t_BSTRING   = r'\<(\\.|[^\>])*\>'
    t_DECIMAL   = r'\b(0|[1-9][0-9]*)\b'
    t_KILO      = r'\b(0|[1-9][0-9]*)[kK]\b'
    t_HEXC      = r'0x[0-9a-fA-F]+'
    t_HEXS      = r'\$[0-9a-fA-F]+'
    t_BINARY    = r'%[01]+'

    def t_PPCONT(self, t):
        r'\\[\t\r ]*\n'
        t.lexer.lineno += t.value.count('\n')
        # eat preprocessor line continuations

    def t_NL(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')
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
        return t

    def t_error(self, t):
        t.type = t.value[0]
        t.value = t.value[0]
        t.lexer.skip(1)
        return t

