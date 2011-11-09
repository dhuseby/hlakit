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

class Parser(object):

    def __init__(self, tokens=[]):
        self.tokens = tokens
    
    def p_program(self, p):
        '''program : common_statement
                   | program common_statement'''
        if len(p) == 2:
            p[0] = ('program', [ p[1] ])
        elif len(p) == 3:
            p[0] = ('program', p[1][1] + [ p[2] ])

    def p_common_statement(self, p):
        '''common_statement : core_statement
                            | core_pp_statement
                            | typedef_statement
                            | variable_statement'''
        if p[1] != None:
            p[0] = p[1]

    def p_core_pp_statement(self, p):
        '''core_pp_statement : HASH PP_INCBIN filename'''
        print "Including binary file: %s..." % p[3]

    def p_core_statement(self, p):
        '''core_statement : common_token
                          | core_statement common_token'''
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
                return
            if isinstance(p[1], list):
                p[0] = p[1]
            else:
                p[0] = [ p[1] ]
        elif len(p) == 3:
            if p[2] is None:
                p[0] = p[1]
                return
            if isinstance(p[2], list):
                p[0] = p[1] + p[2]
            else:
                p[0] = p[1] + [ p[2] ]

    def p_typedef_statement(self, p):
        '''typedef_statement : TYPEDEF type_statement ID
                             | TYPEDEF type_statement ID '[' number ']' '''
        if len(p) == 4:
            p[0] = ('typedef', p[3], p[2])
        elif len(p) == 7:
            p[0] = ('typedef', p[3], p[2], p[5])

    def p_struct_statement(self, p):
        '''struct_statement : STRUCT ID struct_body '''
        p[0] = ('struct', p[2], p[3])

    def p_variable_statement(self, p):
        '''variable_statement : shared type_statement name address assignment_statement
                              | shared type_statement name '[' array_length ']' address assignment_statement'''

        #TODO: handle the special case where the name is None, that only happens when
        #      a struct type is being declared like so:
        # struct foo {
        #     byte blah
        #     byte foo
        # }
        if len(p) == 6:
            #                   name    type    array   array len   shared  address value
            p[0] = ('variable', p[3],   p[2],   False,  None,       p[1],   p[4],   p[5])
        elif len(p) == 9:
            #                   name    type    array   rray len   shared  address value
            p[0] = ('variable', p[3],   p[2],   True,   p[5],       p[1],   p[4],   p[5])

    def p_shared(self, p):
        '''shared : SHARED
                  | empty'''
        if p[1] is None:
            p[0] = False
        else:
            p[0] = True

    def p_name(self, p):
        '''name : ID
                | empty'''
        p[0] = p[1]

    def p_array_length(self, p):
        '''array_length : number
                        | empty'''
        p[0] = p[1]

    def p_address(self, p):
        '''address : ':' number
                   | empty'''
        if len(p) == 3:
            p[0] = p[2]

    def p_assignment_statement(self, p):
        '''assignment_statement : '=' value_statement
                                | empty'''
        if len(p) == 3:
            p[0] = p[2]

    def p_value_statement(self, p):
        '''value_statement : number
                           | STRING
                           | '{' struct_values '}' '''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = p[2]

    def p_struct_values(self, p):
        '''struct_values : label value_statement
                         | struct_values ',' label value_statement'''
        if len(p) == 3:
            if p[1] is None:
                p[0] = [ ('value', p[2]) ]
            else:
                p[0] = [ p[1], ('value', p[2]) ]
        elif len(p) == 5:
            if p[3] is None:
                p[0] = p[1] + [ ('value', p[4]) ]
            else:
                p[0] = p[1] + [ p[3], ('value', p[4]) ]

    def p_label(self, p):
        '''label : ID ':'
                 | empty'''
        if len(p) == 3:
            p[0] = ('label', p[1])

    def p_type_statement(self, p):
        '''type_statement : TYPE
                          | struct_statement'''
        p[0] = p[1]

    def p_struct_body(self, p):
        '''struct_body : '{' struct_members '}'
                       | empty '''
        if len(p) == 4:
            p[0] = p[2]

    def p_struct_members(self, p):
        '''struct_members : struct_member
                          | struct_members struct_member'''
        if len(p) == 2:
            p[0] = [ p[1] ]
        elif len(p) == 3:
            p[0] = p[1] + [ p[2] ]

    def p_struct_member(self, p):
        '''struct_member : type_statement id_list'''
        p[0] = ('member', p[1], p[2])

    def p_id_list(self, p):
        '''id_list : ID
                   | id_list ',' ID'''
        if len(p) == 2:
            p[0] = [ ('id', p[1]) ]
        elif len(p) == 4:
            p[0] = p[1] + [ ('id', p[3]) ]

    def p_number(self, p):
        '''number : DECIMAL
                  | KILO
                  | HEXC
                  | HEXS
                  | BINARY'''
        p[0] = p[1]

    def p_filename(self, p):
        '''filename : STRING
                    | BSTRING'''
        p[0] = p[1]


    def p_common_token(self, p):
        '''common_token : '.'
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
                        | RSHIFT
                        | LSHIFT
                        | GTE
                        | LTE
                        | NE
                        | EQ
                        | ID
                        | WS
                        | NL
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
        if p[1] != '\n':
            p[0] = p[1]

    def p_empty(self, p):
        '''empty :'''
        pass

    # must have a p_error rule
    def p_error(self, p):
        print "Syntax error in input!"

