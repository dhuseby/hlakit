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
from hlakit.common.symboltable import SymbolTable
from hlakit.common.name import Name
from hlakit.common.functioncall import FunctionCall
from hlakit.common.numericvalue import NumericValue
from hlakit.common.immediate import Immediate, UnresolvedSymbolError
from hlakit.common.operand import Operand as CommonOperand
from opcode import Opcode

class Operand(CommonOperand):
    """
    This encapsulates a 6502 operand
    """

    # the full addressing modes
    ACC, IMP, IMM, ABS, ZP, REL, IND, ABS_X, ABS_Y, ZP_X, ZP_Y, \
    IDX_IND, IND_IDX, IDX = range(14)
    MODES = [ 'ACC', 'IMP', 'IMM', 'ABS', 'ZP', 'REL', 'IND', 'ABS_X', 'ABS_Y', 
              'ZP_X', 'ZP_Y', 'IDX_IND', 'IND_IDX', 'IDX' ]

    @classmethod
    def new(klass, **kwargs):
        if 'addr' in kwargs.keys() and kwargs['addr'] != None:
            # create the terminal immediate
            l = Immediate(Immediate.TERMINAL, Name(kwargs['addr']))
            return Operand(kwargs['mode'], addr=l)

        elif 'reg' in kwargs.keys() and kwargs['reg'] != None:
            import pdb; pdb.set_trace()

        elif 'value' in kwargs.keys() and kwargs['value'] != None:
            # create the immediate value
            v = Immediate(Immediate.TERMINAL, kwargs['value'])
            
            # create the instruction line
            return Operand(kwargs['mode'], value=v)
        else:
            # handles instructions lines with no oerands
            return Operand(Operand.IMP)

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
        elif 'ind_idx' in tokens.keys():
            (a, r) = tokens.ind_idx
            k = klass(Operand.IND_IDX, addr=a, reg=r)
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
        ind_idx = Group(Suppress('(') + \
                       Or([NumericValue.exprs(),
                           Immediate.exprs()])+ \
                       Suppress(')') + \
                       Suppress(',') + \
                       CaselessLiteral('y')).setResultsName('ind_idx')

        expr = Or([acc, imm, rel, addr, indirect, idx_ind, ind_idx, indexed])
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, mode=IMP, resolved=False, addr=None, reg=None, value=None):
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

    def emit(self, addr=None):
        if self._mode in (Operand.ACC, Operand.IMP):
            return []

        elif self.get_mode() == Operand.IMM:
            import pdb; pdb.set_trace()
            return [ int(self._value) ]

        elif self.get_mode() == Operand.REL:
            if not self.is_resolved():

                # get the address of the target
                lbl_addr = None
                if isinstance(self._value, Immediate):
                    lbl = self._value.get_args()[0]
                    if lbl.get_address() != None:
                        lbl_addr = lbl.get_address()
                else:
                    lbl_addr = int(self._value)

                # calculate the jump offset
                self._value = -((addr - lbl.get_address()) + 2)

            b = pack('<b', int(self._value))
            return [ ord(a) for a in b ]

        elif self.get_mode() == Operand.ABS:
            b = pack('<H', int(self._addr))
            return [ ord(a) for a in b ]

        elif self.get_mode() in (Operand.ZP, Operand.ZP_X, Operand.ZP_Y, Operand.IDX_IND, Operand.IND_IDX):
            return [ int(self._addr) ]

        elif self.get_mode() in (Operand.IND, Operand.ABS_X, Operand.ABS_Y):
            b = pack('<H', int(self._addr))
            return [ ord(a) for a in b ]

        raise ParseFatalException('cannot emit operand')

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
                if (int(self._value) < -126) or (int(self._value) > 129):
                    raise RuntimeError('invalid relative jump amount')
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

                if int(self._addr) >= 256:
                    raise ParseFatalException('indexed indirect addressing mode with non-zp address')
            except:
                pass

        elif self.get_mode() == Operand.IND_IDX:
            try:
                # resolve immediate to the NumericValue for indirect, indexed
                self._addr = self._addr.resolve()
                self._resolved = True

                if int(self._addr) >= 256:
                    raise ParseFatalException('indirect indexed addressing mode with non-zp address')
            except:
                pass
        
        return self.is_resolved()


    def __str__(self):
        if self._mode is Operand.IMM:
            return '#' + str(self._value)
        elif self._mode is Operand.ABS:
            return str(self._addr)
        elif self._mode is Operand.ZP:
            return str(self._addr)
        elif self._mode is Operand.REL:
            if isinstance(self._value, int):
                return '*' + str(self._value)
            else:
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
        elif self._mode is Operand.IDX_IND:
            return '(%s, x)' % self._addr
        elif self._mode is Operand.IND_IDX:
            return '(%s), y' % self._addr

        return ''

    __repr__ = __str__

