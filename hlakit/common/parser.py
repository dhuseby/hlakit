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
        '''core_statement : pp_statement
                          | base_statement'''
        p[0] = ('core_statement', p[1])

    def p_pp_statement(self, p):
        '''pp_statement : HASH pp_include
                        | HASH cp_msg'''
        p[0] = ('pp_statement', p[2])

    """
    def p_pp_define(self, p):
        '''pp_define : PP_DEFINE ID'''
        pass

    def p_pp_undef(self, p):
        '''pp_undef : PP_UNDEF ID'''
        pass
    """

    def p_pp_include(self, p):
        '''pp_include : PP_INCLUDE STRING
                      | PP_INCLUDE BSTRING'''
        p[0] = ('pp_include', p[2])
        print 'INCLUDING: %s' % p[2]

    def p_cp_msg(self, p):
        '''cp_msg : CP_TODO STRING
                  | CP_WARNING STRING
                  | CP_ERROR STRING
                  | CP_FATAL STRING'''
        print '%s: %s' % (p[1].upper(), p[2])

    def p_base_statement(self, p):
        '''base_statement : PP_IFDEF
                     | PP_IFNDEF
                     | PP_ELSE
                     | PP_ENDIF
                     | CP_INCBIN
                     | '.'
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
                     | BSTRING
                     | DECIMAL
                     | KILO
                     | HEXC
                     | HEXS
                     | BINARY
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
        p[0] = ('base_statement', p[1])

    # must have a p_error rule
    def p_error(self, p):
        print "Syntax error in input!"

