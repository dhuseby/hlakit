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

from hlakit.common.generator import Generator as CommonGenerator
from interrupt import InterruptStart, InterruptNMI, InterruptIRQ
from instructionline import InstructionLine
from conditionaldecl import ConditionalDecl

class Generator(CommonGenerator):

    def _process_instruction_line(self, line):
        romfile = self.romfile()
        opcode = line.get_opcode()
        operand = line.get_operand()

        # get the bytes for the opcode and operand
        bytes = []
        bytes.append(opcode.emit(operand.get_mode()))
        bytes.extend(operand.emit(romfile))

        # add the bytes to the romfile
        romfile.emit(bytes, str(line))

    def _process_token(self, token):

        # get the rom file
        romfile = self.romfile()

        # handle 6502 specific token
        if isinstance(token, InterruptStart):
            romfile.set_reset_interrupt(token.get_fn())
            return (None, 0)
        
        elif isinstance(token, InterruptNMI):
            romfile.set_nmi_interrupt(token.get_fn())
            return (None, 0)
        
        elif isinstance(token, InterruptIRQ):
            romfile.set_irq_interrupt(token.get_fn())
            return (None, 0)
        
        elif isinstance(token, InstructionLine):
            return token.generate()
        
        elif isinstance(token, ConditionalDecl):
            import pdb; pdb.set_trace()
        
        else:
            # pass the token along to the generic generator
            return super(Generator, self)._process_token(token)

    def _initialize_rom(self):
        return super(Generator, self)._initialize_rom()


