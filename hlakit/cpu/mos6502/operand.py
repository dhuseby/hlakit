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

    # the full addressing modes
    ACC, IMP, IMM, ABS, ZP, REL, IND, ABS_X, ABS_Y, ZP_X, ZP_Y, ABS_IDX_IND, \
    ZP_IDX_IND, ZP_IND_IDX, UNK = range(15)
    MODES = [ 'ACC', 'IMP', 'IMM', 'ABS', 'ZP', 'REL', 'IND', 'ABS_X', 'ABS_Y', 
              'ZP_X', 'ZP_Y', 'ABS_IDX_IND', 'ZP_IDX_IND', 'ZP_IND_IDX', 'UNK' ]

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'acc' in tokens.keys():
            return klass(Operand.ACC)
        elif 'imp' in tokens.keys():
            return klass(Operand.IMP)
        elif 'imm' in tokens.keys():
            v = tokens.imm[0]
            op = Operand.IMM
            if isinstance(v, Immediate):
                try:
                    v = v.resolve()
                except:
                    op = Operand.UNK

            return klass(op, value=v)

        elif 'rel' in tokens.keys():
            v = tokens.rel[0]
            op = Operand.REL
            if isinstance(v, Immediate):
                try:
                    v = v.resolve()
                except:
                    op = Operand.UNK

            return klass(op, value=v)

        elif 'addr' in tokens.keys():
            a = tokens.addr[0]
            op = Operand.ABS

            # try to resolve the immediate
            if isinstance(a, Immediate):
                try:
                    a = a.resolve()
                except:
                    op = Operand.UNK

            if op != Operand.UNK:
                if int(a) < 256:
                    op = Operand.ZP

            return klass(op, addr=a)

        elif 'indexed' in tokens.keys():
            (a, r) = tokens.indexed
            ind_x = (str(tokens.indexed[1]).lower() == 'x')
            op = None
           
            # try to resolve the immediate if we get one
            if isinstance(a, Immediate):
                try:
                    a = a.resolve()
                except:
                    op = Operand.UNK

            # figure out which addressing mode to use
            if op != Operand.UNK:
                if int(a) < 256:
                    if ind_x:
                        op = Operand.ZP_X
                    else:
                        op = Operand.ZP_Y
                else:
                    if ind_x:
                        op = Operand.ABS_X
                    else:
                        op = Operand.ABS_Y

            return klass(op, addr=a, reg=r)

        elif 'indirect' in tokens.keys():
            a = tokens.indirect[0]
            op = Operand.IND

            if isinstance(a, Immediate):
                try:
                    a = a.resolve()
                except:
                    op = Operand.UNK

            return klass(op, addr=a)

        elif 'idx_ind' in tokens.keys():
            (a, r) = tokens.idx_ind
            op = Operand.ABS_IDX_IND

            if isinstance(a, Immediate):
                try:
                    a = a.resolve()
                except:
                    op = Operand.UNK

            if op != Operand.UNK:
                if int(a) < 256:
                    op = Operand.ZP_IDX_IND

            return klass(op, addr=a, reg=r)

        elif 'zp_ind' in tokens.keys():
            (a, r) = tokens.zp_ind
            op = Operand.ZP_IND_IDX

            if isinstance(a, Immediate):
                try:
                    a = a.resolve()
                except:
                    op = Operand.UNK

            return klass(op, addr=a, reg=r)
       
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

        # relative
        rel = Group(Optional(Suppress('*')) + \
                    Immediate.exprs()).setResultsName('rel')

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

        expr = Or([acc, imm, rel, addr, indirect, idx_ind, zp_ind, indexed])
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, mode, addr=None, reg=None, value=None):
        self._mode = mode
        self._addr = addr
        self._reg = reg
        self._value = value

    def unresolved(self):
        return (self._mode == self.UNK)

    def get_mode(self):
        return self._mode

    def get_addr(self):
        return self._addr

    def get_reg(self):
        return self._reg

    def get_value(self):
        return self._value

    def __str__(self):
        if self._mode is Operand.ACC:
            return '<accumulator>'
        elif self._mode is Operand.IMP:
            return '<implied>'
        elif self._mode is Operand.IMM:
            return '#' + str(self._value)
        elif self._mode is Operand.ABS:
            return str(self._addr)
        elif self._mode is Operand.ZP:
            return str(self._addr)
        elif self._mode is Operand.REL:
            return str(self._addr)
        elif self._mode is Operand.IND:
            return '(%s)' % self._addr
        elif self._mode is Operand.ABS_X:
            return '%s,x' % self._addr
        elif self._mode is Operand.ABS_Y:
            return '%s,y' % self._addr
        elif self._mode is Operand.ZP_X:
            return '%s,x' % self._addr
        elif self._mode is Operand.ZP_Y:
            return '%s,y' % self._addr
        elif self._mode is Operand.ABS_IDX_IND:
            return '(%s, x)' % self._addr
        elif self._mode is Operand.ZP_IDX_IND:
            return '(%s, x)' % self._addr
        elif self._mode is Operand.ZP_IND_IDX:
            return '(%s), y' % self._addr
        elif self._mode is Operand.UNK:
            return '<unresolved>'
        return 'invalid operand'

    __repr__ = __str__

