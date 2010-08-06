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

import os
from pyparsing import *
from hlakit.common.target import Target
from hlakit.common.preprocessor import Preprocessor
from hlakit.common.compiler import Compiler
from interrupt import InterruptStart, InterruptNMI, InterruptIRQ
from instructionline import InstructionLine
from conditional import Conditional

class MOS6502Preprocessor(Preprocessor):

    @classmethod
    def first_exprs(klass):
        e = []

        # start with the first base preprocessor rules 
        e.extend(Preprocessor.first_exprs())

        # add in 6502 specific preprocessor parse rules
        e.append(('interruptstart', InterruptStart.exprs()))
        e.append(('interruptnmi', InterruptNMI.exprs()))
        e.append(('interruptirq', InterruptIRQ.exprs()))
        
        return e

class MOS6502Compiler(Compiler):

    @classmethod
    def first_exprs(klass):
        e = []

        # add in 6502 specific compiler parse rules
        e.append(('instructionline', InstructionLine.exprs()))
        e.append(('conditional', Conditional.exprs()))

        # start with the first base compiler rules 
        e.extend(Compiler.first_exprs())
       
        return e

class MOS6502(Target):

    def __init__(self):

        # init the base class 
        super(MOS6502, self).__init__()

    def preprocessor(self):
        return MOS6502Preprocessor()

    def compiler(self):
        return MOS6502Compiler()

    def linker(self):
        return None



