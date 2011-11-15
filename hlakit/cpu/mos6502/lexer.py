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

from hlakit.common.lexer import Lexer as CommonLexer
from hlakit.common.types import Types
from hlakit.common.basetype import BaseType

class Lexer(CommonLexer):

    # base types
    types = {
        'byte':         'TYPE',
        'char':         'TYPE',
        'bool':         'TYPE',
        'word':         'TYPE',
        'pointer':      'TYPE'
    }

    # 6502 conditional tokens 
    conditionals = {
        'is':           'IS',
        'has':          'HAS',
        'no':           'NO',
        'not':          'NOT',
        'plus' :        'POSITIVE',     # N = 0
        'positive':     'POSITIVE',     # N = 0
        'minus':        'NEGATIVE',     # N = 1
        'negative':     'NEGATIVE',     # N = 1
        'greater':      'GREATER',      # N = 0, Z = 0, C = 1
        'less':         'LESS',         # N = 1, Z = 0, C = 0
        'overflow':     'OVERFLOW',     # V = 1
        'carry':        'CARRY',        # C = 1
        'nonzero':      'TRUE',         # Z = 0
        'set':          'TRUE',         # Z = 0
        'true':         'TRUE',         # Z = 0
        '1':            'TRUE',         # Z = 0
        'zero':         'FALSE',        # Z = 1
        'unset':        'FALSE',        # Z = 1
        'false':        'FALSE',        # Z = 1
        '0':            'FALSE',        # Z = 1
        'clear':        'FALSE',        # Z = 1
        'equal':        'EQUAL'         # N = 0, Z = 1, C = 1
    }

    # opcodes
    opcodes = {
        'adc':          'ADC', 
        'and':          'AND', 
        'asl':          'ASL', 
        'bcc':          'BCC', 
        'bcs':          'BCS', 
        'beq':          'BEQ', 
        'bit':          'BIT', 
        'bmi':          'BMI', 
        'bne':          'BNE', 
        'bpl':          'BPL', 
        'brk':          'BRK', 
        'bvc':          'BVC', 
        'bvs':          'BVS', 
        'clc':          'CLC', 
        'cld':          'CLD', 
        'cli':          'CLI', 
        'clv':          'CLV', 
        'cmp':          'CMP', 
        'cpx':          'CPX', 
        'cpy':          'CPY', 
        'dec':          'DEC', 
        'dex':          'DEX', 
        'dey':          'DEY', 
        'eor':          'EOR', 
        'inc':          'INC', 
        'inx':          'INX', 
        'iny':          'INY', 
        'jmp':          'JMP', 
        'jsr':          'JSR', 
        'lda':          'LDA', 
        'ldx':          'LDX', 
        'ldy':          'LDY', 
        'lsr':          'LSR', 
        'nop':          'NOP', 
        'ora':          'ORA', 
        'pha':          'PHA', 
        'php':          'PHP', 
        'pla':          'PLA', 
        'plp':          'PLP', 
        'rol':          'ROL', 
        'ror':          'ROR', 
        'rti':          'RTI', 
        'rts':          'RTS', 
        'sbc':          'SBC', 
        'sec':          'SEC', 
        'sed':          'SED', 
        'sei':          'SEI', 
        'sta':          'STA', 
        'stx':          'STX', 
        'sty':          'STY', 
        'tax':          'TAX', 
        'tay':          'TAY', 
        'tsx':          'TSX', 
        'txa':          'TXA', 
        'txs':          'TXS', 
        'tya':          'TYA'
    }

    # 6502 tokens list
    tokens = CommonLexer.tokens \
             + list(set(types.values())) \
             + list(set(conditionals.values())) \
             + list(set(opcodes.values())) \
             + [ 'REG' ]

    # registers on the 6502
    t_REG = r'(?i)reg\.(a|x|y)'

    # override t_INTERRUPT to be 6502 specific
    t_INTERRUPT = r'interrupt\.(start|nmi|irq)'

    # identifier
    def t_ID(self, t):
        r'[a-zA-Z_][\w]*'

        value = t.value.lower()

        # case insensitive
        t.type = self.conditionals.get(value, None) # check for conditionals
        if t.type != None:
            t.value = value
            return t

        # case insensitive
        t.type = self.opcodes.get(value, None) # check for opcode words
        if t.type != None:
            t.value = value
            return t

        return super(Lexer, self).t_ID(t)

    def __init__(self):
        super(Lexer, self).__init__()

        # build the type records for the basic types
        for t in self.types.iterkeys():
            Types().new_type(t, BaseType(t))

