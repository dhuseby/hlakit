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

from symboltable import SymbolTable
from ppmacro import PPMacro

class PPParser(object):

    def __init__(self, tokens=[]):
        self.tokens = tokens
        self._enabled = [ True ]
        self._depth = 0

    def is_enabled(self):
        return self._enabled[-1]

    def p_program(self, p):
        '''program : common_statement
                   | program common_statement'''
        if len(p) == 2:
            p[0] = ('program', [ p[1] ])
        elif len(p) == 3:
            p[0] = ('program', p[1][1] + [ p[2] ])

    def p_common_statement(self, p):
        '''common_statement : pp_statement
                            | pp_block_statement
                            | base_statement'''
        if self.is_enabled():
            p[0] = p[1]

    def p_pp_statement(self, p):
        '''pp_statement : HASH pp_include
                        | HASH pp_incbin
                        | HASH pp_define
                        | HASH pp_undef
                        | HASH pp_msg '''
        p[0] = p[2]

    def p_pp_block_statement(self, p):
        '''pp_block_statement : pp_block_start pp_block_body pp_block_else pp_block_body pp_block_end
                              | pp_block_start pp_block_body pp_block_end'''
        if len(p) == 4:
            p[0] = ('pp_block_statement', p[1], ('pp_block_body', p[2]), p[3])
        elif len(p) == 6:
            p[0] = ('pp_block_statement', p[1], ('pp_block_body', p[2]), p[3], ('pp_block_body', p[4]), p[5])

    def p_pp_block_start(self, p):
        '''pp_block_start : HASH PP_IFDEF ID NL
                          | HASH PP_IFNDEF ID NL '''

        # only execute the logic if we're enabled
        if self.is_enabled():
            # check to see if the symbol is defined
            defined = (SymbolTable().lookup_symbol(p[3]) != None)

            # execute the ifdef/ifndef logic
            if ((defined == False) and (p[2] == 'ifdef')) or (defined and (p[2] == 'ifndef')):
                self._enabled.append(False)
            else:
                self._enabled.append(True)
        else:
            # we're disabled so push a False to track depth while keeping disabled state
            self._enabled.append(False)

        p[0] = ('pp_block_start', p[2], p[3])

    def p_pp_block_else(self, p):
        '''pp_block_else : HASH PP_ELSE NL '''

        if len(self._enabled) == 1:
            #TODO report an error
            pass

        # remove the top item in the list
        old_state = self._enabled.pop()

        # only execute the logic if this is a top level else
        if self.is_enabled():
            # flip the enabled state
            self._enabled.append(not old_state)
        else:
            # we're disabled so push a False to track depth while keeping disabled state
            self._enabled.append(False)

        p[0] = ('pp_block_else', p[2])

    def p_pp_block_end(self, p):
        '''pp_block_end : HASH PP_ENDIF NL '''

        if len(self._enabled) == 1:
            #TODO report an error
            pass

        # pop the current state off of the stack
        self._enabled.pop()

        p[0] = ('pp_block_end', p[2])

    def p_pp_block_body(self, p):
        '''pp_block_body : common_statement
                         | pp_block_body common_statement'''
        if len(p) == 2:
            p[0] = [ p[1] ]
        elif len(p) == 3:
            p[0] = p[1] + [ p[2] ]

    def p_pp_define(self, p):
        '''pp_define : PP_DEFINE ID pp_define_body
                     | PP_DEFINE ID '(' pp_define_params ')' pp_define_body'''

        name = p[2]
        value = None
        params = None

        if len(p) == 4:
            value = p[3]
            p[0] = ('pp_define', p[2], p[3])
        elif len(p) == 7:
            value = p[6]
            params = p[4]
            p[0] = ('pp_define_macro', p[2], p[4], p[6])

        SymbolTable().new_symbol( name, PPMacro(name, value, params) )

    def p_pp_define_params(self, p):
        '''pp_define_params : ID
                            | pp_define_params ',' ID'''
        if len(p) == 2:
            p[0] = [ p[1] ]
        elif len(p) == 4:
            p[0] = p[1] + [ p[3] ]

    def p_pp_define_body(self, p):
        '''pp_define_body : statement
                          | pp_define_body BS NL statement'''
        if len(p) == 2:
            p[0] = [ p[1] ]
        elif len(p) == 5:
            p[0] = p[1] + [ p[4] ]

    def p_pp_undef(self, p):
        '''pp_undef : PP_UNDEF ID NL'''
        p[0] = ('pp_undef', )

    def p_pp_include(self, p):
        '''pp_include : PP_INCLUDE STRING NL
                      | PP_INCLUDE BSTRING NL'''
        p[0] = ('pp_include', p[2][1:-1])
        print 'INCLUDING: %s' % p[2]

    def p_pp_msg(self, p):
        '''pp_msg : PP_TODO STRING NL
                  | PP_WARNING STRING NL
                  | PP_ERROR STRING NL
                  | PP_FATAL STRING NL'''
        print '%s: %s' % (p[1].upper(), p[2])

    def p_pp_incbin(self, p):
        '''pp_incbin : PP_INCBIN STRING NL
                     | PP_INCBIN BSTRING NL'''
        p[0] = ('pp_incbin', p[2])

    def p_base_statement(self, p):
        '''base_statement : base_token
                          | base_statement base_token'''
        if len(p) == 2:
            p[0] = ('base_statement', [ p[1] ])
        elif len(p) == 3:
            p[0] = ('base_statement', p[1][1] + [ p[2] ])

    def p_base_token(self, p):
        '''base_token     : STRING
                          | BSTRING
                          | DECIMAL
                          | KILO
                          | HEXC
                          | HEXS
                          | BINARY
                          | ID
                          | WS
                          | NL
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
                          | ',' '''
        p[0] = p[1]

    # must have a p_error rule
    def p_error(self, p):
        print "Syntax error in input!"

