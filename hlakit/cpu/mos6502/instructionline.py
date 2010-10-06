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
from hlakit.common.label import Label
from hlakit.common.immediate import Immediate
from hlakit.common.name import Name
from opcode import Opcode
from operand import Operand

class InstructionLine(object):
    """
    This encapsulates a single line of assembly code
    """

    @classmethod
    def new(klass, opcode, mode=None, lbl=None, addr=None, reg=None, value=None):
        if lbl != None:
            # generate a label and use it as the addr in the operand
            name = str(lbl)
            if isinstance(lbl, Label):
                name = str(lbl.get_name())
            l = Immediate(Immediate.TERMINAL, Name(name))
            
            # create the instruction line
            return klass(Opcode(opcode), Operand(mode, addr=l))

        elif addr != None:
            import pdb; pdb.set_trace()
        elif reg != None:
            import pdb; pdb.set_trace()
        elif value != None:
            # create the immediate value
            v = Immediate(Immediate.TERMINAL, value)
            
            # create the instruction line
            return klass(Opcode(opcode), Operand(mode, value=v))

            pass
        else:
            # handles instructions lines with no oerands
            return klass(Opcode(opcode), None)

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []
        
        opcode = None
        if 'opcode' in tokens.keys():
            opcode = tokens.opcode
        else:
            raise ParseFatalException('instruction line missing opcode')

        operand = None
        if 'operand' in tokens.keys():
            operand = tokens.operand
        else:
            operand = Operand(Operand.IMP)

        return klass(tokens.opcode, operand)

    @classmethod
    def exprs(klass):
     
        expr = Or([Opcode.no_operands().setResultsName('opcode'),
                   Opcode.operands().setResultsName('opcode') + \
                   Operand.exprs().setResultsName('operand')])
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, opcode, operand):
        self._opcode = opcode
        self._operand = operand

    def get_opcode(self):
        return self._opcode

    def get_operand(self):
        return self._operand

    def __str__(self):
        s = str(self._opcode)
        if self._operand:
            s += ' %s' % self._operand
        return s

    __repr__ = __str__

