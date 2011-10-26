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

class PPParser(object):

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
                        | HASH pp_incbin
                        | HASH pp_define
                        | HASH pp_undef
                        | HASH pp_startblock
                        | HASH pp_endblock
                        | HASH pp_msg '''
        p[0] = ('pp_statement', p[2])

    def p_pp_startblock(self, p):
        '''pp_startblock : PP_IFDEF ID
                         | PP_IFNDEF ID'''
       
        """
        defined = (SymbolTable().lookup_symbol(p[2]) != None)

        if ((p[1] == 'PP_IFDEF') and defined) or ((p[1] == 'PP_IFNDEF') and not defined):
            p.lexer.push_state('ifdefin')
        else:
            p.lexer.push_state('ifdefout')
        """

        p[0] = ('pp_startblock', p[1], p[2])

    def p_pp_endblock(self, p):
        '''pp_endblock : PP_ELSE
                       | PP_ENDIF'''
        
        """
        # figure out which state we're current in
        cin = (p.lexer.current_state() == 'ifdefin')

        # always pop state at the end of an #ifdef block
        p.lexer.pop_state()

        # if we're encountering an #else, we need to swap
        # to the other state
        if p[2] == 'PP_ELSE':
            if cin:
                p.lexer.push_state('ifdefout')
            else:
                p.lexer.push_state('ifdefin')
        """
        p[0] = ('pp_endblock', p[1])

    def p_pp_define(self, p):
        '''pp_define : PP_DEFINE'''
        p[0] = ('pp_define', )

        
        """
        macro_parser = Session().macro_parser()

        # tell the lexer to return newline tokens
        p.lexer.set_eat_nl(False)

        # returns a tuple ('macro', <id>, <macro object>)
        macro = macro_parser.parse(debug=Session().is_debug(), lexer=p.lexer)

        # tell the lexer to eat newline tokens
        p.lexer.set_eat_nl(True)

        # add the symbol to the symbol table
        # SymbolTable().new_symbol(macro[1], macro[2])

        # add it to the graph
        p[0] = ('pp_define', macro)
        """

    def p_pp_undef(self, p):
        '''pp_undef : PP_UNDEF'''
        p[0] = ('pp_undef', )

        """
        # remove the symbol from the symbol table
        # SymbolTable().remove_symbol(p[2])

        p[0] = ('pp_undef', p[2])
        """

    def p_pp_include(self, p):
        '''pp_include : PP_INCLUDE STRING
                      | PP_INCLUDE BSTRING'''
        p[0] = ('pp_include', p[2])
        print 'INCLUDING: %s' % p[2]

    def p_pp_msg(self, p):
        '''pp_msg : PP_TODO STRING
                  | PP_WARNING STRING
                  | PP_ERROR STRING
                  | PP_FATAL STRING'''
        print '%s: %s' % (p[1].upper(), p[2])

    def p_pp_incbin(self, p):
        '''pp_incbin : PP_INCBIN STRING
                     | PP_INCBIN BSTRING'''
        p[0] = ('pp_incbin', p[2])

    def p_base_statement(self, p):
        '''base_statement : STRING
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
        p[0] = ('base_statement', p[1])

    # must have a p_error rule
    def p_error(self, p):
        print "Syntax error in input!"

