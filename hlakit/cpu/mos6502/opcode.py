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
        self._op = op.lower()

    def get_op(self):
        return self._op

    def is_relative(self):
        return self._op in self.RELATIVE

    def __str__(self):
        return '%s' % self._op

    def __hash__(self):
        return hash(self.__str__())

    __repr__ = __str__

