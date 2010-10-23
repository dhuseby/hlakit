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

from pyparsing import MatchFirst, CaselessKeyword
from hlakit.common.target import Target
from hlakit.common.type_ import Type
from preprocessor import Preprocessor
from compiler import Compiler
from generator import Generator
from conditionaldecl import ConditionalDecl
from opcode import Opcode

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
        return MatchFirst([CaselessKeyword(c) for c in ConditionalDecl.CONDITIONS])

    def preprocessor(self):
        return Preprocessor()

    def compiler(self):
        return Compiler()

    def generator(self):
        return Generator()



