"""
HLAKit
Copyright (c) 2010 David Huseby. All rights reserved.

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

from pyparsing import *
from struct import pack, unpack
from hlakit.common.session import Session
from hlakit.common.name import Name

class Opcode(object):
    """
    This encapsulates a 6502 opcode
    """
    OPCODES = [ 'adc', 'and', 'asl', 'bcc', 'bcs', 'beq', 'bit', 'bmi', 
                'bne', 'bpl', 'brk', 'bvc', 'bvs', 'clc', 'cld', 'cli', 
                'clv', 'cmp', 'cpx', 'cpy', 'dec', 'dex', 'dey', 'eor', 
                'inc', 'inx', 'iny', 'jmp', 'jsr', 'lda', 'ldx', 'ldy', 
                'lsr', 'nop', 'ora', 'pha', 'php', 'pla', 'plp', 'rol', 
                'ror', 'rti', 'rts', 'sbc', 'sec', 'sed', 'sei', 'sta', 
                'stx', 'sty', 'tax', 'tay', 'tsx', 'txa', 'txs', 'tya']

    OPERANDS =[ 'adc', 'and', 'asl', 'bcc', 'bcs', 'beq', 'bit', 'bmi', 
                'bne', 'bpl', 'bvc', 'bvs', 'cmp', 'cpx', 'cpy', 'dec', 
                'eor', 'inc', 'jmp', 'jsr', 'lda', 'ldx', 'ldy', 'lsr', 
                'ora', 'rol', 'ror', 'sbc', 'sta', 'stx', 'sty']

    IMPLIED = [ 'brk', 'clc', 'cld', 'cli', 'clv', 'dex', 'dey', 'inx', 
                'iny', 'nop', 'pha', 'php', 'pla', 'plp', 'rti', 'rts', 
                'sec', 'sed', 'sei', 'tax', 'tay', 'tsx', 'txa', 'txs', 
                'tya']

    RELATIVE =[ 'bcc', 'bcs', 'beq', 'bmi', 'bne', 'bpl', 'bvc', 'bvs' ]


    # this table contains the binary opcode value for the given pneumonic and 
    # addressing mode.  the opcodes are in the following order: 
    # ACC, IMP, IMM, ABS, ZP, REL, IND, ABS_X, ABS_Y, ZP_X, ZP_Y, IDX_IND, IND_IDX.
    BCODES = {
        'adc': [],
        'and': [],
        'asl': [],
        'bcc': [],
        'bcs': [],
        'beq': [],
        'bit': [],
        'bmi': [],

        'bne': [None, None, None, None, None, 0xD0, None, None, None, None, None, None, None],
        'bpl': [],
        'brk': [],
        'bvc': [],
        'bvs': [],
        'clc': [],
        'cld': [],
        'cli': [],

        'clv': [],
        'cmp': [],
        'cpx': [],
        'cpy': [],
        'dec': [],
        'dex': [],
        'dey': [],
        'eor': [],

        'inc': [],
        'inx': [None, 0xE8, None, None, None, None, None, None, None, None, None, None, None],
        'iny': [],
        'jmp': [None, None, None, 0x4C, None, None, 0x6C, None, None, None, None, None, None],
        'jsr': [],
        'lda': [None, None, 0xA9, 0xAD, 0xA5, None, None, 0xBD, 0xB9, 0xB5, None, 0xA1, 0xB1],
        'ldx': [None, None, 0xA2, 0xAE, 0xA6, None, None, None, 0xBE, None, 0xB6, None, None],
        'ldy': [None, None, 0xA0, 0xAC, 0xA4, None, None, 0xBC, None, 0xB4, None, None, None],

        'lsr': [],
        'nop': [None, 0xEA, None, None, None, None, None, None, None, None, None, None, None],
        'ora': [],
        'pha': [],
        'php': [],
        'pla': [],
        'plp': [],
        'rol': [],

        'ror': [],
        'rti': [],
        'rts': [],
        'sbc': [],
        'sec': [],
        'sed': [],
        'sei': [],
        'sta': [None, None, None, 0x8D, 0x85, None, None, 0x9D, 0x99, 0x95, None, 0x81, 0x91],

        'stx': [None, None, None, 0x8E, 0x86, None, None, None, None, None, 0x96, None, None],
        'sty': [None, None, None, 0x8C, 0x84, None, None, None, None, 0x94, None, None, None],
        'tax': [],
        'tay': [],
        'tsx': [],
        'txa': [],
        'txs': [],
        'tya': []
    }

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'op' not in tokens.keys():
            raise ParseFatalException('opcode missing')

        return klass(tokens.op)

    @classmethod
    def no_operands(klass):
        expr = MatchFirst([CaselessKeyword(op).setResultsName('op') for op in Opcode.IMPLIED])
        expr.setParseAction(klass.parse)
        return expr

    @classmethod
    def operands(klass):
        expr = MatchFirst([CaselessKeyword(op).setResultsName('op') for op in Opcode.OPERANDS])
        expr.setParseAction(klass.parse)
        return expr

    @classmethod
    def exprs(klass):
        expr = MatchFirst([CaselessKeyword(op).setResultsName('op') for op in Opcode.OPCODES])
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, op=None):
        op = op.lower()
        if (op not in self.OPCODES) and \
           (op not in self.OPERANDS) and \
           (op not in self.IMPLIED) and \
           (op not in self.RELATIVE):
               raise ParseFatalException('invalid opcode')
        self._op = op

    def get_op(self):
        return self._op

    def emit(self, mode):
        return pack('<B', self.BCODES[self._op][mode])

    def is_relative(self):
        return self._op in self.RELATIVE

    def __str__(self):
        return '%s' % self._op

    def __hash__(self):
        return hash(self.__str__())

    __repr__ = __str__

