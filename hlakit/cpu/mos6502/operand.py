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
from hlakit.common.immediate import Immediate, UnresolvedSymbolError
from opcode import Opcode

class Operand(object):
    """
    This encapsulates a 6502 operand
    """

    # the full addressing modes
    ACC, IMP, IMM, ABS, ZP, REL, IND, IDX, ABS_X, ABS_Y, ZP_X, ZP_Y, IDX_IND, \
    ABS_IDX_IND, ZP_IDX_IND, ZP_IND_IDX = range(16)
    MODES = [ 'ACC', 'IMP', 'IMM', 'ABS', 'ZP', 'REL', 'IND', 'IDX', 'ABS_X', 'ABS_Y', 
              'ZP_X', 'ZP_Y', 'IDX_IND', 'ABS_IDX_IND', 'ZP_IDX_IND', 'ZP_IND_IDX' ]

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'acc' in tokens.keys():
            k = klass(Operand.ACC)
        elif 'imp' in tokens.keys():
            k = klass(Operand.IMP)
        elif 'imm' in tokens.keys():
            k = klass(Operand.IMM, value=tokens.imm[0])
        elif 'rel' in tokens.keys():
            k = klass(Operand.REL, value=tokens.rel[0])
        elif 'addr' in tokens.keys():
            k = klass(Operand.ABS, addr=tokens.addr[0])
        elif 'indexed' in tokens.keys():
            (a, r) = tokens.indexed
            k = klass(Operand.IDX, addr=a, reg=r)
        elif 'indirect' in tokens.keys():
            k = klass(Operand.IND, addr=tokens.indirect[0])
        elif 'idx_ind' in tokens.keys():
            (a, r) = tokens.idx_ind
            k = klass(Operand.IDX_IND, addr=a, reg=r)
        elif 'zp_ind' in tokens.keys():
            (a, r) = tokens.zp_ind
            k = klass(Operand.ZP_IND_IDX, addr=a, reg=r)
        else:
            raise ParseFatalException('invalid operand')

        # try to resolve the operand
        k.resolve()

        return k

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
        rel = Group(Suppress('*') + \
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

    def __init__(self, mode, resolved=False, addr=None, reg=None, value=None):
        self._mode = mode
        self._addr = addr
        self._reg = reg
        self._value = value
        self._resolved = resolved

    def is_resolved(self):
        return self._resolved

    def set_resolved(self, resolved):
        self._resolved = resolved

    def get_mode(self):
        return self._mode

    def get_addr(self):
        return self._addr

    def get_reg(self):
        return self._reg

    def get_value(self):
        return self._value

    def set_scope(self, scope):
        if hasattr(self._addr, 'set_scope'):
            self._addr.set_scope(scope)
        if hasattr(self._value, 'set_scope'):
            self._value.set_scope(scope)

    def get_scope(self):
        return self._scope

    def resolve(self):
        # don't try to resolve if we're already resolved
        if self.is_resolved():
            return True

        if self._mode is Operand.ACC:
            self._resolved = True

        elif self._mode is Operand.IMP:
            self._resolved = True

        elif self.get_mode() == Operand.IMM:
            try:
                # resolve immediate to NumericValue
                self._value = self._value.resolve()
                self._resolved = True
            except:
                pass

        elif self.get_mode() == Operand.REL:
            try:
                # resolve immediate to the NumericValue that represnts
                # the relative offset to jump to
                self._value = self._value.resolve()
                self._resolved = True
                if (int(self._addrs) < -128) or (int(self._addr) > 127):
                    raise ParseFatalException('invalid relative jump amount')
            except:
                pass

        elif self.get_mode()  == Operand.ABS:
            try:
                # resolve immediate to the NumericValue of the address
                self._addr = self._addr.resolve()
                self._resolved = True
                if int(self._addr) < 256:
                    self._mode = Operand.ZP
            except:
                pass

        elif self.get_mode() == Operand.IDX:
            ind_x = (self._reg.lower() == 'x')
            try:
                # resolve immediate to the NumericValue of the base address
                self._addr = self._addr.resolve()
                self._resolved = True

                # figure out which exact addressing mode we're using
                if int(self._addr) < 256:
                    if ind_x:
                        self._mode = Operand.ZP_X
                    else:
                        self._mode = Operand.ZP_Y
                else:
                    if ind_x:
                        self._mode = Operand.ABS_X
                    else:
                        self._mode = Operand.ABS_Y
            except:
                pass

        elif self.get_mode() == Operand.IND:
            try:
                # resolve immediate to the NumericValue for indirect jump
                self._addr = self._addr.resolve()
                self._resolved = True
            except:
                pass

        elif self.get_mode() == Operand.IDX_IND:
            try:
                # resolve immediate to the NumericValue for indexed, indirect
                self._addr = self._addr.resolve()
                self._resolved = True

                # figure out which exact addressing mode we're using
                if int(self._addr) < 256:
                    self._mode = Operand.ZP_IDX_IND
                else:
                    self._mode = Operand.ABS_IDX_IND
            except:
                pass

        elif self.get_mode() == Operand.ZP_IND_IDX:
            try:
                # resolve immediate to the NumericValue for indirect, indexed
                self._addr = self._addr.resolve()
                self._resolved = True
            except:
                pass
        
        return self.is_resolved()


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
            return str(self._value)
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

        # IDX, IDX_IND
        return '<unresolved>'

    __repr__ = __str__

