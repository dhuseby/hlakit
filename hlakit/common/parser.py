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
from types import Types

class Parser(object):

    def __init__(self, tokens=[]):
        self.tokens = tokens
    
    def p_program(self, p):
        '''program : common_statement
                   | program common_statement'''
        if len(p) == 2:
            if p[1] is None:
                p[0] = ('program', [])
            else:
                p[0] = ('program', [ p[1] ])
        elif len(p) == 3:
            if p[2] is None:
                p[0] = p[1]
            else:
                p[0] = ('program', p[1][1] + [ p[2] ])

    def p_common_statement(self, p):
        '''common_statement : core_statement
                            | core_pp_statement
                            | typedef_statement
                            | variable_statement
                            | function_statement
                            | interrupt_statement
                            | macro_statement'''
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

    def p_interrupt_statement(self, p):
        '''interrupt_statement : INTERRUPT intr_type noreturn ID '(' ')' '{' function_body '}' '''
        #                    name  body  noreturn type
        p[0] = ('interrupt', p[4], p[8], p[3],    p[2])
        SymbolTable().new_symbol(p[4], p[0])

    # interrupt types are CPU/platform specific
    def p_intr_type(self, p):
        '''intr_type :'''
        pass

    def p_macro_statement(self, p):
        '''macro_statement : INLINE ID '(' id_list ')' '{' function_body '}' '''
        #                name  body  params
        p[0] = ('macro', p[2], p[7], p[4])
        SymbolTable().new_symbol(p[2], p[0])

    def p_function_statement(self, p):
        '''function_statement : FUNCTION noreturn ID '(' ')' '{' function_body '}' '''
        #                   name  body  noreturn
        p[0] = ('function', p[3], p[7], p[2])
        SymbolTable().new_symbol(p[3], p[0])

    def p_function_body(self, p):
        '''function_body : function_body_statement
                         | function_body function_body_statement'''
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = [ p[1] ]
        else:
            if p[2] is None:
                p[0] = p[1]
            else:
                p[0] = p[1] + [ p[2] ]

    def p_function_body_statement(self, p):
        '''function_body_statement : RETURN
                                   | empty'''
        if p[1] != None:
            p[0] = p[1]

    def p_function_call(self, p):
        '''function_call : ID '(' ')' 
                         | ID '(' param_list ')' '''
        fn = SymbolTable().lookup_symbol(p[1])
        if fn is None:
            raise Exception('calling undeclared function: %s' % p[1])

        if len(p) == 4:
            p[0] = ('%s_call' % fn[0], p[1], None)
        elif len(p) == 5:
            if fn[0] != 'macro':
                raise Exception('only inline macros can have parameters')
            if len(fn[3]) != len(p[3]):
                raise Exception('missing parameters in call to macro %s' % p[1])
            p[0] = ('macro_call', p[1], p[3] )

    def p_noreturn(self, p):
        '''noreturn : NORETURN
                    | empty'''
        p[0] = (p[1] == 'noreturn')

    def p_typedef_statement(self, p):
        '''typedef_statement : TYPEDEF type_statement seen_typedef ID
                             | TYPEDEF type_statement seen_typedef ID '[' number ']' '''
        # we need to update the type alias if it is an array
        if len(p) == 8:
            shape = Types().lookup_type(p[4])
            Types().update_type(p[4], ('alias', shape[1], p[6]) )

    def p_seen_typedef(self, p):
        '''seen_typedef :'''

        # get the type_statement from the parser's sym stack
        type_name = p.parser.symstack[-1].value
        type_shape = None
        if isinstance(type_name, tuple):
            type_shape = type_name[2]
            type_name = ' '.join(type_name[0:2])

        if type_shape != None:
            # this is a typedef with an inline struct shape...we need to declare the
            # struct type first before we can alias it
            Types().new_type(type_name, ('type', type_shape, None))

        # this is a normal alias
        # the lexer's look ahead token should be an ID that is the type's new name
        next_token = p.lexer.look_ahead_token
        if next_token.type == 'ID':
            Types().new_type(next_token.value, ('alias', type_name, None))

    def p_struct_statement(self, p):
        '''struct_statement : STRUCT ID struct_body '''
        p[0] = ('struct', p[2], p[3])

    def _size_values(self, val):
        lengths = self._size_value(val)
        if not self._check_sizes(lengths):
            raise Exception('dynamically sized arrays do not all have the same size')
        lengths = self._collapse_sizes(lengths)
        return lengths

    def _collapse_sizes(self, val):
        if not isinstance(val, list):
            return [ val ]
        v = [ val[0] ]
        if (len(val) > 1) and isinstance(val[1], list):
            if len(val[1]) > 0:
                v.extend(self._collapse_sizes(val[1][0]))
        return v

    def _check_sizes(self, val):
        if not isinstance(val, list):
            return True

        expected = val[0]
        if (len(val) > 1) and isinstance(val[1], list):
            if expected != len(val[1]):
                return False
            ret = True
            for v in val[1]:
                ret &= self._check_sizes(v)
            return ret
        else:
            for v in val[1:]:
                if expected != v:
                    return False
        return True


    def _size_value(self, val):
        lengths = []

        l = 0
        lens = []
        for i in xrange(0, len(val)):
            if val[i][0] == 'value':
                l += 1
                if isinstance(val[i][1], list):
                    lens.append(self._size_value(val[i][1]))

        if len(lens) > 0:
            lengths.append(l)
            lengths.append(lens)
            return lengths
        else:
            return l

    def p_variable_statement(self, p):
        '''variable_statement : shared type_statement name address assignment_statement
                              | shared type_statement name array_lengths address assignment_statement'''

        type_name = p[2]
        if isinstance(p[2], tuple):
            type_name = ' '.join(p[2][0:2])

        if len(p) == 6:
            if p[3] is None:
                # this is a struct type declaration
                Types().new_type(type_name, ('type', p[2][2], None) )
            else:
                if isinstance(p[2], tuple):
                    # type is a struct...
                    struct_shape = p[2][2]
                    if struct_shape is None:
                        if Types().lookup_type(type_name) is None:
                            raise Exception('unknown struct type: %s' % type_name)
                    else:
                        if Types().lookup_type(type_name) != None:
                            raise Exception('redeclaration of struct type: %s' % type_name)
                        # need to create the type entry
                        Types().new_type(type_name, ('type', struct_shape, None) )
    
                #                   name  type       array  array len  shared  address  value
                p[0] = ('variable', p[3], type_name, False, None,      p[1],   p[4],    p[5])
        elif len(p) == 7:
            arrlen = p[4]
            sizes = False
            for l in arrlen:
                sizes &= (l != None)
            if sizes is False:
                if p[6] is None:
                    raise Exception('dynamic sized array declared without a value')
                arrlen = self._size_values(p[6])

            #                   name    type       array  array len  shared  address  value
            p[0] = ('variable', p[3],   type_name, True,  arrlen,    p[1],   p[5],    p[6])

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

    def p_array_lengths(self, p):
        '''array_lengths : '[' array_length ']'
                         | array_lengths '[' array_length ']' '''
        if len(p) == 4:
            p[0] = [ p[2] ]
        elif len(p) == 5:
            p[0] = p[1] + [ p[3] ]

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
        '''struct_values : label_list value_statement
                         | struct_values ',' label value_statement'''
        if len(p) == 3:
            if p[1] is None:
                p[0] = [ ('value', p[2]) ]
            else:
                p[0] = p[1] + [ ('value', p[2]) ]
        elif len(p) == 5:
            if p[3] is None:
                p[0] = p[1] + [ ('value', p[4]) ]
            else:
                p[0] = p[1] + [ p[3], ('value', p[4]) ]

    def p_label_list(self, p):
        '''label_list : label
                      | label_list label'''
        if len(p) == 2:
            if p[1] != None:
                p[0] = [ p[1] ]
        elif len(p) == 3:
            if p[2] is None:
                p[0] = p[1]
            else:
                p[0] = p[1] + [ p[2] ]

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

    def p_param_list(self, p):
        '''param_list : param
                      | param_list ',' param'''
        if len(p) == 2:
            p[0] = [ p[1] ]
        elif len(p) == 4:
            p[0] = p[1] + [ p[3] ]

    def p_param(self, p):
        '''param : selector
                 | HASH immediate_expression'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/')
    )

    def p_immediate_expression(self, p):
        '''immediate_expression : immediate_expression '+' immediate_expression
                                | immediate_expression '-' immediate_expression
                                | immediate_expression '*' immediate_expression
                                | immediate_expression '/' immediate_expression
                                | '(' immediate_expression ')'
                                | immediate_fn
                                | value
                                | number'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1] == '(':
                p[0] = p[1]
            else:
                p[0] = (p[2], p[1], p[3])


    def p_immediate_fn(self, p):
        '''immediate_fn : LO '(' immediate_expression ')'
                        | HI '(' immediate_expression ')'
                        | NYLO '(' immediate_expression ')'
                        | NYHI '(' immediate_expression ')'
                        | SIZEOF '(' immediate_expression ')' '''
        p[0] = (p[1], p[3])

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

    def p_value(self, p):
        '''value : number
                 | selector'''
        p[0] = p[1]

    def p_selector(self, p):
        '''selector : ID
                    | selector '.' ID'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ''.join(p[1:])


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

