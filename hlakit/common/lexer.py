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

from session import Session
from types import Types

class Lexer(object):

    # incbin is handled in the compiler phase
    preprocessor = {
        'incbin':       'PP_INCBIN',
    }

    # hla reserved tokens
    reserved = {
        'byte':         'TYPE',
        'char':         'TYPE',
        'bool':         'TYPE',
        'word':         'TYPE',
        'dword':        'TYPE',
        'pointer':      'TYPE',
        'struct':       'STRUCT',
        'typedef':      'TYPEDEF',
        'shared':       'SHARED',
        'noreturn':     'NORETURN',
        'return':       'RETURN',
        'inline':       'INLINE',
        'function':     'FUNCTION',
        'interrupt':    'INTERRUPT',
        'lo':           'LO',
        'hi':           'HI',
        'nylo':         'NYLO',
        'nyhi':         'NYHI',
        'sizeof':       'SIZEOF',
        'if':           'IF',
        'else':         'ELSE',
        'while':        'WHILE',
        'do':           'DO',
        'forever':      'FOREVER',
        'switch':       'SWITCH',
        'case':         'CASE',
        'default':      'DEFAULT',
        'reg':          'REG',
        'near':         'NEAR',
        'far':          'FAR'
        }

    rtokens = [ 'STRING', 
                'BSTRING',
                'DECIMAL', 
                'KILO', 
                'HEXC', 
                'HEXS', 
                'BINARY', 
                'HASH',
                'RSHIFT',
                'LSHIFT',
                'GTE',
                'LTE',
                'NE',
                'EQ',
                'ID',
                'WS',
                'NL' ] 

    # the tokens list
    tokens      = rtokens \
                + list(set(preprocessor.values())) \
                + list(set(reserved.values()))

    literals    = '.+-*/~!%><=&^|{}()[]:,'

    t_HASH      = r'\#'
    t_STRING    = r'\"(\\.|[^\"])*\"'
    t_BSTRING   = r'\<(\\.|[^\>])*\>'
    t_DECIMAL   = r'(0|[1-9][0-9]*)'
    t_KILO      = r'(0|[1-9][0-9]*)[kK]'
    t_HEXC      = r'0x[0-9a-fA-F]+'
    t_HEXS      = r'\$[0-9a-fA-F]+'
    t_BINARY    = r'%[01]+'
    t_RSHIFT    = r'>>'
    t_LSHIFT    = r'<<'
    t_GTE       = r'>='
    t_LTE       = r'<='
    t_NE        = r'!='
    t_EQ        = r'=='

    def t_NL(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')
        # eat newlines

    def t_WS(self, t):
        r'\s+'
        # eat whitespace

    def t_ID(self, t):
        r'[a-zA-Z_][\w]*'

        # case insensitive
        t.type = self.preprocessor.get(t.value.lower(), None) # check for preprocessor words
        if t.type != None:
            t.value = t.value.lower()
            t.lexer.look_ahead_token = t
            return t

        # case sensitive
        t.type = self.reserved.get(t.value, None) # check for reserved words
        if t.type != None:
            t.lexer.look_ahead_token = t
            return t

        # case sensitive, check to see if this is a type name
        shape = Types().lookup_type(t.value)
        if shape != None:
            t.type = 'TYPE'
        else:
            t.type = 'ID'

        t.lexer.look_ahead_token = t
        return t

    def t_COMMENT(self, t):
        r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
        t.lexer.lineno += t.value.count("\n")
        # eat comments

    def t_error(self, t):
        t.type = t.value[0]
        t.value = t.value[0]
        t.lexer.skip(1)
        return t

    def __init__(self):
        pass

