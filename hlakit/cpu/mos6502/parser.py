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

from hlakit.common.parser import Parser as CommonParser

class Parser(CommonParser):

    def __init__(self, tokens=[]):
        self.tokens = tokens

    def p_program(self, p):
        '''program : empty
                   | common_statement
                   | program common_statement'''
        super(Parser, self).p_program(p)

    def p_function_body_statement(self, p):
        '''function_body_statement : assembly_statement
                                   | conditional_statement
                                   | function_call
                                   | RETURN
                                   | empty'''
        if p[1] != None:
            p[0] = p[1]

    def p_conditional_statement(self, p):
        '''conditional_statement : if_statement
                                 | while_statement
                                 | do_while_statement
                                 | forever_statement
                                 | switch_statement'''
        p[0] = p[1]

    def p_if_statement(self, p):
        '''if_statement : IF '(' conditional_clause ')' function_body_statement else_statement
                        | IF '(' conditional_clause ')' '{' function_body '}' else_statement '''
        if len(p) == 7:
            if p[6] is None:
                p[0] = ('if', p[3], [ p[5] ])
            else:
                p[0] = ('if', p[3], [ p[5] ], p[6])
        else:
            if p[8] is None:
                p[0] = ('if', p[3], p[6])
            else:
                p[0] = ('if', p[3], p[6], p[8])

    def p_else_statement(self, p):
        '''else_statement : ELSE function_body_statement
                          | ELSE '{' function_body '}'
                          | empty'''
        if len(p) == 3:
            p[0] = [ p[2] ]
        elif len(p) == 5:
            p[0] = p[3]

    def p_while_statement(self, p):
        '''while_statement : WHILE '(' conditional_clause ')' function_body_statement
                           | WHILE '(' conditional_clause ')' '{' function_body '}' '''
        if len(p) == 6:
            p[0] = ('while', p[3], p[5])
        else:
            p[0] = ('while', p[3], p[6])

    def p_do_while_statement(self, p):
        '''do_while_statement : DO function_body_statement WHILE '(' conditional_clause ')'
                              | DO '{' function_body '}' WHILE '(' conditional_clause ')' '''
        if len(p) == 7:
            p[0] = ('do_while', p[5], p[2])
        else:
            p[0] = ('do_while', p[7], p[3])

    def p_forever_statement(self, p):
        '''forever_statement : FOREVER function_body_statement
                             | FOREVER '{' function_body '}' '''
        if len(p) == 3:
            p[0] = ('forever', p[2])
        else:
            p[0] = ('forever', p[3])

    def p_switch_statement(self, p):
        '''switch_statement : SWITCH '(' REG ')' '{' switch_body '}' '''
        if p[3].lower() not in ('reg.a','reg.x','reg.y'):
            raise Exception('invalid switch register')
        p[0] = ('switch', p[3], p[8])

    def p_switch_body(self, p):
        '''switch_body : switch_block
                       | switch_body switch_block'''
        if len(p) == 2:
            p[0] = [ p[1] ]
        else:
            p[0] = p[1] + [ p[2] ]

    def p_switch_block(self, p):
        '''switch_block : case_block
                        | default_block'''
        p[0] = p[1]

    def p_case_block(self, p):
        '''case_block : CASE function_body_statement
                      | CASE '{' function_body '}' '''
        if len(p) == 3:
            p[0] = [ p[2] ]
        else:
            p[0] = p[3]

    def p_default_block(self, p):
        '''default_block : DEFAULT function_body_statement
                         | DEFAULT '{' function_body '}' '''
        if len(p) == 3:
            p[0] = [ p[2] ]
        else:
            p[0] = p[3]

    def p_assembly_statement(self, p):
        '''assembly_statement : opcode operands'''
        p[0] = ('asm', p[1], p[2])

    def p_opcode(self, p):
        '''opcode : ADC
                  | AND
                  | ASL
                  | BCC
                  | BCS
                  | BEQ
                  | BIT
                  | BMI
                  | BNE
                  | BPL
                  | BRK
                  | BVC
                  | BVS
                  | CLC
                  | CLD
                  | CLI
                  | CLV
                  | CMP
                  | CPX
                  | CPY
                  | DEC
                  | DEX
                  | DEY
                  | EOR
                  | INC
                  | INX
                  | INY
                  | JMP
                  | JSR
                  | LDA
                  | LDX
                  | LDY
                  | LSR
                  | NOP
                  | ORA
                  | PHA
                  | PHP
                  | PLA
                  | PLP
                  | ROL
                  | ROR
                  | RTI
                  | RTS
                  | SBC
                  | SEC
                  | SED
                  | SEI
                  | STA
                  | STX
                  | STY
                  | TAX
                  | TAY
                  | TSX
                  | TXA
                  | TXS
                  | TYA '''
        p[0] = p[1]

    def p_operands(self, p):
        '''operands : immediate
                    | indirect
                    | abs_zp_r
                    | abs_zp_idx
                    | abs_zp_ind
                    | zp_ind
                    | empty'''
        p[0] = p[1]

    def p_immediate(self, p):
        '''immediate : param'''
        p[0] = ('immediate', p[1])

    def p_indirect(self, p):
        '''indirect : '(' value ')' '''
        p[0] = ('indirect', p[2])

    def p_abs_zp_r(self, p):
        '''abs_zp_r : value'''
        #TODO: detect if the operand is absolute, zero page, or relative
        #      based on the operand and the number value
        p[0] = ('absolute', p[1])

    def p_abs_zp_idx(self, p):
        '''abs_zp_idx : value ',' ID'''
        if p[3].lower() not in ('x', 'y'):
            raise Exception('invalid register name in absolute, indexed operand')
        p[0] = ('abs_idx', p[1], p[3])

    def p_abs_zp_ind(self, p):
        '''abs_zp_ind : '(' value ',' ID ')' '''
        if p[4].lower() != 'x':
            raise Exception('not using X register in absolute indexed indirect operand')
        p[0] = ('abs_ind', p[2], p[4])

    def p_zp_ind(self, p):
        '''zp_ind : '(' value ')' ',' ID'''
        if p[5].lower() != 'y':
            raise Exception('not using Y register in zp indirect indexed operand')
        p[0] = ('zp_ind', p[2], p[5])

    def p_conditional_clause(self, p):
        '''conditional_clause : distance modifier condition'''
        p[0] = ('conditional_clause', p[3], p[2], p[1])

    def p_distance(self, p):
        '''distance : NEAR
                    | FAR 
                    | empty'''
        p[0] = p[1]

    def p_modifer(self, p):
        '''modifier : IS
                    | HAS
                    | NO
                    | NOT
                    | empty'''
        p[0] = p[1]

    def p_condition(self, p):
        '''condition : POSITIVE
                     | NEGATIVE
                     | GREATER
                     | LESS
                     | OVERFLOW
                     | CARRY
                     | TRUE
                     | FALSE
                     | EQUAL '''
        p[0] = p[1]

    # must have a p_error rule
    def p_error(self, p):
        import pdb; pdb.set_trace()
        print "Syntax error in input!"

