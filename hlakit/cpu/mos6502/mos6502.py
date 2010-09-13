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
from hlakit.common.generator import Generator
from hlakit.common.type_ import Type
from hlakit.common.label import Label
from hlakit.common.function import Function
from hlakit.common.functiondecl import FunctionDecl
from hlakit.common.functioncall import FunctionCall
from hlakit.common.functionreturn import FunctionReturn
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd
from interrupt import InterruptStart, InterruptNMI, InterruptIRQ
from instructionline import InstructionLine
from conditional import Conditional
from opcode import Opcode

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

    def _next_state(self, token):

        # we have to handle the InstructionLine here because it is
        # a CPU specific token and the base compiler doesn't know
        # anything about it.
        if self._state == self.INSIDE:
            if isinstance(token, InstructionLine):
                self._fn.append_token(token)
                return None

        # if we aren't inside of a function decl or the token
        # wasn't an InstructionLine, then call the base class
        # to handle the token.
        return super(MOS6502Compiler, self)._next_state(token)

class MOS6502Generator(Generator):

    def _process_token(self, token):

        # handle 6502 specific token
        if isinstance(token, InterruptStart):
            pass
        elif isinstance(token, InterruptNMI):
            pass
        elif isinstance(token, InterruptIRQ):
            pass
        elif isinstance(token, InstructionLine):
            pass
        elif isinstance(token, Conditional):
            pass
        else:
            # pass the token along to the generic generator
            super(MOS6502Generator, self)._process_token(token)

    def _initialize_rom(self):
        return super(MOS6502Generator, self)._initialize_rom()

    def _finalize_rom(self):
        pass

    def build_rom(self, tokens):

        # initialize the rom output pass
        self._initialize_rom()

        # process each of the tokens
        for t in tokens:
            self._process_token(t)

        # finalize the rom output pass
        self._finalize_rom()


class MOS6502(Target):

    BASIC_TYPES = [ 'byte', 'char', 'bool', 'word', 'pointer' ]

    def __init__(self):

        # init the base class 
        super(MOS6502, self).__init__()

    def opcodes(self):
        return Opcode.exprs()

    def keywords(self):
        return super(MOS6502, self).keywords()

    def basic_types(klass):
        # these are the basic type identifiers
        return [ Type(t) for t in MOS6502.BASIC_TYPES ]

    def basic_types_names(self):
        return MatchFirst([CaselessKeyword(t) for t in MOS6502.BASIC_TYPES])

    def conditions(self):
        return MatchFirst([CaselessKeyword(c) for c in Conditional.CONDITIONS])

    def preprocessor(self):
        return MOS6502Preprocessor()

    def compiler(self):
        return MOS6502Compiler()

    def generator(self):
        return MOS6502Generator()



