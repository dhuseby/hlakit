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
        '''program : cpu_statement
                   | program cpu_statement'''
        super(Parser, self).p_program(p)

    def p_cpu_statement(self, p):
        '''cpu_statement : common_statement
                         | mos6502_statement'''
        p[0] = p[1]

    def p_mos6502_statement(self, p):
        '''mos6502_statement : mos6502_token
                             | mos6502_statement mos6502_token'''
        super(Parser, self).p_common_statement(p)

    def p_mos6502_token(self, p):
        '''mos6502_token : A
                         | X
                         | Y
                         | IS
                         | HAS
                         | NO
                         | NOT
                         | POSITIVE
                         | NEGATIVE
                         | GREATER
                         | LESS
                         | OVERFLOW
                         | CARRY
                         | TRUE
                         | FALSE
                         | EQUAL
                         | ADC
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

    # must have a p_error rule
    def p_error(self, p):
        import pdb; pdb.set_trace()
        print "Syntax error in input!"

