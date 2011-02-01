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
from hlakit.common.instructionline import InstructionLine as CommonInstructionLine
from opcode import Opcode
from operand import Operand

class InstructionLine(CommonInstructionLine):
    """
    This encapsulates a single line of assembly code
    """

    @classmethod
    def new(klass, opcode, **kwargs):
        # we overload this so that we are creating 6502 versions of 
        # the Opcode/Operand classes
        il = klass(Opcode.new(opcode), Operand.new(**kwargs))
        if 'fn' in kwargs.keys():
            il.set_fn(kwargs['fn'])
        return il

    @classmethod
    def exprs(klass):
        # we overload this so that we are getting the 6502 versions of the
        # parser expressions...
        opcode_no_operands = Opcode._get_no_operands()
        opcode_with_operands = Opcode._get_with_operands()
        operands = Operand.exprs()
     
        expr = Or([opcode_no_operands.setResultsName('opcode'),
                   opcode_with_operands.setResultsName('opcode') + \
                   operands.setResultsName('operand')])
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, opcode, operand):
        # if no operand is supplied, then we create an Operand with the implied
        # addressing mode so that all 6502 addressing modes are possible
        if operand is None:
            operand = Operand()

        super(InstructionLine, self).__init__(opcode, operand)

    def generate(self, addr=None):
        # we need to figure out what the 1-3 bytes are for this
        # instruction line
       
        # reset the bytes
        bytes = []
        
        # get the byte for the opcode...there is no operand
        bytes.append(self.get_opcode().emit(self.get_operand().get_mode()))

        # now get the operand bytes
        bytes.extend(self.get_operand().emit(addr))

        return bytes

