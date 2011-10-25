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

class Parser(object):

    def __init__(self, tokens=[]):
        self.tokens = tokens
    
    def p_program(self, p):
        '''program : core_statement
                   | program core_statement'''
        if len(p) == 2:
            p[0] = ('program', p[1])
        elif len(p) == 3:
            p[0] = ('program', p[1], p[2])

    def p_core_statement(self, p):
        '''core_statement : '.'
                     | '+'
                     | '-'
                     | '*'
                     | '/'
                     | '~'
                     | '!'
                     | '%'
                     | '>'
                     | '<'
                     | '='
                     | '&'
                     | '^'
                     | '|'
                     | '{'
                     | '}'
                     | '('
                     | ')'
                     | '['
                     | ']'
                     | ':'
                     | ','
                     | STRING
                     | DECIMAL
                     | KILO
                     | HEXC
                     | HEXS
                     | BINARY
                     | HASH
                     | DHASH
                     | RSHIFT
                     | LSHIFT
                     | GTE
                     | LTE
                     | NE
                     | EQ
                     | ID
                     | WS
                     | NL
                     | COMMENT
                     | TYPE
                     | STRUCT
                     | TYPEDEF
                     | SHARED
                     | NORETURN
                     | RETURN
                     | INLINE
                     | FUNCTION
                     | INTERRUPT
                     | LO
                     | HI
                     | SIZEOF
                     | IF
                     | ELSE
                     | WHILE
                     | DO
                     | FOREVER
                     | SWITCH
                     | CASE
                     | DEFAULT
                     | REG
                     | NEAR
                     | FAR '''
        p[0] = ('statement', p[1])

    # must have a p_error rule
    def p_error(self, p):
        print "Syntax error in input!"

