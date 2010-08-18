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
from hlakit.common.functioncall import FunctionCall
from hlakit.common.numericvalue import NumericValue
from hlakit.common.immediate import Immediate
from opcode import Opcode

class Operand(object):
    """
    This encapsulates a 6502 operand
    """

    IMP, ACC, IMM, ADDR, INDEXED, INDIRECT, IDX_IND, ZP_IND = range(8)

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'imp' in tokens.keys():
            return klass(Operand.IMP)
        elif 'acc' in tokens.keys():
            return klass(Operand.ACC)
        elif 'imm' in tokens.keys():
            return klass(Operand.IMM, value=tokens.imm[0])
        elif 'addr' in tokens.keys():
            return klass(Operand.ADDR, addr=tokens.addr[0])
        elif 'indexed' in tokens.keys():
            return klass(Operand.INDEXED, addr=tokens.indexed[0], reg=tokens.indexed[1])
        elif 'indirect' in tokens.keys():
            return klass(Operand.INDIRECT, addr=tokens.indirect[0])
        elif 'idx_ind' in tokens.keys():
            return klass(Operand.IDX_IND, addr=tokens.idx_ind[0], reg=tokens.idx_ind[1])
        elif 'zp_ind' in tokens.keys():
            return klass(Operand.ZP_IND, addr=tokens.zp_ind[0], reg=tokens.zp_ind[1])
       
        raise ParseFatalException('invalid operand')

    @classmethod
    def exprs(klass):
        ops = Session().opcodes()
        kws = Session().keywords()
        conds = Session().conditions()
        variable_ref = Group(delimitedList(Name.exprs(), '.'))

        # accumulator
        acc = Group(Suppress(CaselessLiteral('reg') + \
                    Literal('.')) + \
                    CaselessLiteral('a')).setResultsName('acc')

        # immediate operand
        imm  = Group(Suppress('#') + \
                     Immediate.exprs()).setResultsName('imm')

        # zero page and full absolute address
        addr = Group(Or([NumericValue.exprs(),
                         Immediate.exprs()])).setResultsName('addr')

        # zero page, x/y and absolute, x/y
        indexed = Group(Or([NumericValue.exprs(),
                            Immediate.exprs()]) + \
                        Suppress(',') + \
                        oneOf('x y', caseless=True)).setResultsName('indexed')

        # indirect is only valie for JMP
        indirect = Group(Suppress('(') + \
                         Or([NumericValue.exprs(),
                             Immediate.exprs()]) + \
                         Suppress(')')).setResultsName('indirect')
        
        # indexed indirect
        idx_ind = Group(Suppress('(') + \
                        Or([NumericValue.exprs(),
                            Immediate.exprs()])+ \
                        Suppress(',') + \
                        CaselessLiteral('x') + \
                        Suppress(')')).setResultsName('idx_ind')

        # indirect indexed
        zp_ind = Group(Suppress('(') + \
                       Or([NumericValue.exprs(),
                           Immediate.exprs()])+ \
                       Suppress(')') + \
                       Suppress(',') + \
                       CaselessLiteral('y')).setResultsName('zp_ind')

        expr = Or([acc, imm, addr, indirect, idx_ind, zp_ind, indexed])
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, mode, addr=None, reg=None, value=None):
        self._mode = mode
        self._addr = addr
        self._reg = reg
        self._value = value

    def get_mode(self):
        return self._mode

    def get_addr(self):
        return self._addr

    def get_reg(self):
        return self._reg

    def get_value(self):
        return self._value

    def __str__(self):
        if self._mode is Operand.IMP:
            return '<implied>'
        elif self._mode is Operand.ACC:
            return '<accumulator>'
        elif self._mode is Operand.ADDR:
           return str(self._addr)
        elif self._mode is Operand.IMM:
            return '#' + str(self._value)
        elif self._mode is Operand.INDEXED:
            return '%s,%s' % (self._addr, self._reg)
        elif self._mode is Operand.INDIRECT:
            return '(%s)' % (self._addr)
        elif self._mode is Operand.IDX_IND:
            return '(%s,%s)' % (self._addr, self._reg)
        elif self._mode is Operand.ZP_IND:
            return '(%s),%s' % (self._addr, self._reg)
        return 'invalid operand'

    __repr__ = __str__

