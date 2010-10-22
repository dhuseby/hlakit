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

class Opcode(object):

    @classmethod
    def new(klass, arg):
        raise ParseFatalException('cannot instantiate base opcode class')

    @classmethod
    def _get_no_operands(klass):
        # the cpu/platform specific version of this must return a parser expr that matches
        # the opcode mnemonics for opcodes that do not have operands so that it can be
        # included in the InstructionLine parsing.
        raise ParseFatalException('must overload this in a cpu/platform specific class')

    @classmethod
    def _get_with_operands(klass):
        # the cpu/platform specific version of this must return a parser expr that matches
        # the opcode mnemonics for opcodes that have operands so that it can be combined
        # with the operand parser expression in the InstructionLine parsing.
        raise ParseFatalException('must overload this in a cpu/platform specific class')

    @classmethod
    def exprs(klass):
        # the cpu/platform specific version of this must return a parser expr that matches
        # all of the possible opcode mnemonics so that variables know what they cannot be
        # called.
        raise ParseFatalException('must overload this in a cpu/platform specific class')


