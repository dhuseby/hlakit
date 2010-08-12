"""
HLAKit Tests
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
import sys
from types import NoneType
import unittest
from pyparsing import ParseException, ParseFatalException
from cStringIO import StringIO
from tests.utils import build_code_block 
from hlakit.common.name import Name
from hlakit.common.session import Session
from hlakit.common.symboltable import SymbolTable
from hlakit.common.typeregistry import TypeRegistry
from hlakit.common.codeblock import CodeBlock
from hlakit.common.codeline import CodeLine
from hlakit.common.numericvalue import NumericValue
from hlakit.cpu.mos6502 import MOS6502Preprocessor, MOS6502Compiler
from hlakit.cpu.mos6502.interrupt import InterruptStart, InterruptNMI, InterruptIRQ
from hlakit.cpu.mos6502.register import Register
from hlakit.cpu.mos6502.opcode import Opcode
from hlakit.cpu.mos6502.operand import Operand
from hlakit.cpu.mos6502.instructionline import InstructionLine
from hlakit.cpu.mos6502.conditional import Conditional
from hlakit.common.functiontype import FunctionType
from hlakit.common.functionparameter import FunctionParameter
from hlakit.common.function import Function
from hlakit.common.functioncall import FunctionCall
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd
from hlakit.common.immediate import Immediate

class MOS6502PreprocessorTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the 6502 Preprocessor
    """

    def setUp(self):
        Session().parse_args(['--cpu=6502'])

    def tearDown(self):
        Session().preprocessor().reset_state()

    def test6502Preprocessor(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        self.assertTrue(isinstance(session._target.preprocessor(), MOS6502Preprocessor))

    pp_intstart = '#interrupt.start %s\n'
    pp_intnmi = '#interrupt.nmi %s\n'
    pp_intirq = '#interrupt.irq %s\n'

    def testInterruptStart(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_intstart % 'start'))
        self.assertTrue(isinstance(pp.get_output()[1], InterruptStart))
        self.assertEquals(pp.get_output()[1].get_fn(), 'start')

    def testBadInterruptStart(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_intstart % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testInterruptNMI(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_intnmi % 'vblank'))
        self.assertTrue(isinstance(pp.get_output()[1], InterruptNMI))
        self.assertEquals(pp.get_output()[1].get_fn(), 'vblank')

    def testBadInterruptNMI(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_intnmi % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testInterruptIRQ(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_intirq % 'timer'))
        self.assertTrue(isinstance(pp.get_output()[1], InterruptIRQ))
        self.assertEquals(pp.get_output()[1].get_fn(), 'timer')

    def testBadInterruptStart(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_intirq % ''))
            self.assertTrue(False)
        except ParseException:
            pass


class MOS6502CompilerTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the MOS6502 CPU compiler.
    """

    def setUp(self):
        Session().parse_args(['--cpu=6502'])

    def tearDown(self):
        Session().compiler().reset_state()
        TypeRegistry().reset_state()
        SymbolTable().reset_state()

    def testCompiler(self):
        session = Session()
        self.assertTrue(isinstance(session.compiler(), MOS6502Compiler))

    def testLineNoOperand(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('clc')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), NoneType))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'clc')

    def testTwoLinesNoOperand(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('clc'), CodeLine('cli')])])
        self.assertEquals(len(cc.get_output()), 2)
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), NoneType))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'clc')
        self.assertTrue(isinstance(cc.get_output()[1], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[1].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[1].get_operand(), NoneType))
        self.assertEquals(str(cc.get_output()[1].get_opcode().get_op()), 'cli')


    def testLineAddr(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('ldx $D010')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'ldx')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.ADDR)
        self.assertEquals(int(cc.get_output()[0].get_operand().get_addr()), 0xD010)

    def testLineImm(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('ldx #$22')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'ldx')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value().get_args()[0]), 0x22)

    def testLineIndexed(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc $2200,x')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.INDEXED)
        self.assertEquals(int(cc.get_output()[0].get_operand().get_addr()), 0x2200)
        self.assertEquals(str(cc.get_output()[0].get_operand().get_reg()), 'x')

    def testLineIndexedIndirect(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('jmp ($2200,x)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'jmp')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IDX_IND)
        self.assertEquals(int(cc.get_output()[0].get_operand().get_addr()), 0x2200)
        self.assertEquals(str(cc.get_output()[0].get_operand().get_reg()), 'x')

    def testLineZPIndexedIndirect(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('lsr ($22),y')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'lsr')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.ZP_IND)
        self.assertEquals(int(cc.get_output()[0].get_operand().get_addr()), 0x22)
        self.assertEquals(str(cc.get_output()[0].get_operand().get_reg()), 'y')

    def testImmNumber(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #1')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], NumericValue))

    def testImmVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #foo')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Name))

    def testImmMath(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #(1+1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.ADD)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], NumericValue))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[1], NumericValue))

    def testImmSignNumber(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #-1')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.SIGN)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], NumericValue))

    def testImmSignVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #-foo')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.SIGN)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Name))

    def testImmSignMath(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #-(1+1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.SIGN)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0].get_type(), Immediate.ADD)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[0], NumericValue))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[1], NumericValue))

    def testImmSizeofNumber(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #sizeof(1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.SIZEOF)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0].get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[0], NumericValue))

    def testImmSizeofVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #sizeof(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.SIZEOF)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0].get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[0], Name))

    def testImmSizeofMath(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #sizeof(1+1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.SIZEOF)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0].get_type(), Immediate.ADD)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[0], NumericValue))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[1], NumericValue))

    def testImmLoNumber(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #lo(1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.LO)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0].get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[0], NumericValue))

    def testImmLoVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #lo(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.LO)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0].get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[0], Name))

    def testImmLoMath(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #lo(1+1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.LO)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0].get_type(), Immediate.ADD)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[0], NumericValue))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[1], NumericValue))

    def testImmHiNumber(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #hi(1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.HI)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0].get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[0], NumericValue))

    def testImmHiVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #hi(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.HI)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0].get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[0], Name))

    def testImmHiMath(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #hi(1+1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.HI)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0].get_type(), Immediate.ADD)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[0], NumericValue))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[0].get_args()[1], NumericValue))

    def testBlockOfCode(self):
        code = """
               clc
               adc #sizeof(SPR_OBJ)
               lda #lo(pproc)
               ora #hi(pproc)
               assign_16i(_jsrind_temp, pproc)
               jsrind_f()
               """
        types = [ InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  FunctionCall,
                  FunctionCall ]

        cc = Session().compiler()

        st = SymbolTable()
        st.reset_state()
        # pre-define the function 'jsrind_f'
        st.new_symbol(Function(Name('jsrind_f'), FunctionType('function'), []))
        # pre-define the macro 'assign_16i'
        st.new_symbol(Function(Name('assign_16i'), FunctionType('inline'), 
                               [FunctionParameter('one'), FunctionParameter('two')]))

        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,6):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

    def testSimpleCompleteFunctionDecl(self):
        code = """
               function foo()
               {
                   lda  0x0200,x
                   inx
                   ora  0x0200,x
                   inx
               }
               """
        types = [ Function,
                  ScopeBegin,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  ScopeEnd ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

    def testSimpleCompleteMacroDecl(self):
        code = """
               inline foo(addr)
               {
                   lda  addr,x
                   inx
                   ora  addr,x
                   jsrind_f()
                   inx
               }
               """
        types = [ Function,
                  ScopeBegin,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  FunctionCall,
                  InstructionLine,
                  ScopeEnd ]

        cc = Session().compiler()
        st = SymbolTable()
        # pre-define the function 'jsrind_f'
        st.new_symbol(Function(Name('jsrind_f'), FunctionType('function'), []))
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

    def testIfConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('if(set)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.IF)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.SET)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testIfNegatedConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('if(not 1)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.IF)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.ONE)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NEGATED)

    def testIfFarConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('if(far carry)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.IF)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.CARRY)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.FAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testIfFarNegatedConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('if(far not overflow)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.IF)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.OVERFLOW)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.FAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NEGATED)
        
    def testElseConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('else')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.ELSE)
        self.assertEquals(cc.get_output()[0].get_condition(), None)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testIfElseConditional(self):
        code = """
               if (set)
               {
                   inx
               }
               else
               {
                   dex
               }
               """
        types = [ Conditional,
                  ScopeBegin,
                  InstructionLine,
                  ScopeEnd,
                  Conditional,
                  ScopeBegin,
                  InstructionLine,
                  ScopeEnd ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

    def testWhileConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('while(true)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.WHILE)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.TRUE)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testWhileNegatedConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('while (not 0)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.WHILE)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.ZERO)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NEGATED)

    def testWhileFarConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('while(far unset)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.WHILE)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.UNSET)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.FAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testWhileFarNegatedConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('while(far not clear)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.WHILE)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.CLEAR)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.FAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NEGATED)

    def testWhileBlockConditional(self):
        code = """
               while (plus)
               {
                   inx
                   dex
               }
               """
        types = [ Conditional,
                  ScopeBegin,
                  InstructionLine,
                  InstructionLine,
                  ScopeEnd ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

    def testDoConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('do')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.DO)
        self.assertEquals(cc.get_output()[0].get_condition(), None)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testDoWhileBlockConditional(self):
        code = """
               do
               {
                   inx
                   dex
               }
               while (positive)
               """
        types = [ Conditional,
                  ScopeBegin,
                  InstructionLine,
                  InstructionLine,
                  ScopeEnd,
                  Conditional ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

    def testForeverConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('forever')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.FOREVER)
        self.assertEquals(cc.get_output()[0].get_condition(), None)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testSwitchConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('switch(x)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.SWITCH)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.X)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testSwitchCapitalConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('switch(A)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.SWITCH)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.A)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testSwitchRegDotConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('switch(reg.y)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.SWITCH)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.Y)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testSwitchRegDotCapitalConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('switch(REG.X)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.SWITCH)
        self.assertEquals(cc.get_output()[0].get_condition(), Conditional.X)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testCaseDecimalConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('case #32')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.CASE)
        self.assertTrue(isinstance(cc.get_output()[0].get_condition(), Immediate))
        self.assertEquals(cc.get_output()[0].get_condition().get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_condition().get_args()[0], NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_condition().get_args()[0]), 32)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testCaseFunctionCallConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('case #sizeof(foo)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.CASE)
        self.assertTrue(isinstance(cc.get_output()[0].get_condition(), Immediate))
        self.assertEquals(cc.get_output()[0].get_condition().get_type(), Immediate.SIZEOF)
        self.assertTrue(isinstance(cc.get_output()[0].get_condition().get_args()[0], Immediate))
        self.assertEquals(cc.get_output()[0].get_condition().get_args()[0].get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_condition().get_args()[0].get_args()[0], Name))
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testCaseVariableConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('case #(1+1)')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.CASE)
        self.assertTrue(isinstance(cc.get_output()[0].get_condition(), Immediate))
        self.assertEquals(cc.get_output()[0].get_condition().get_type(), Immediate.ADD)
        self.assertTrue(isinstance(cc.get_output()[0].get_condition().get_args()[0], NumericValue))
        self.assertTrue(isinstance(cc.get_output()[0].get_condition().get_args()[1], NumericValue))
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testDefaultConditional(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('default')])])
        self.assertEquals(len(cc.get_output()), 1)
        self.assertTrue(isinstance(cc.get_output()[0], Conditional))
        self.assertEquals(cc.get_output()[0].get_mode(), Conditional.DEFAULT)
        self.assertEquals(cc.get_output()[0].get_condition(), None)
        self.assertEquals(cc.get_output()[0].get_distance(), Conditional.NEAR)
        self.assertEquals(cc.get_output()[0].get_modifier(), Conditional.NORMAL)

    def testSwitchCaseDefaultConditional(self):
        code = """
               switch(X)
               {
                   case #sizeof(bar)
                   {
                       inx
                   }
                   case #0x0200
                       dex
                   default
                   {
                       lda  $0300
                   }
               }
               """
        types = [ Conditional,
                  ScopeBegin,
                  Conditional,
                  ScopeBegin,
                  InstructionLine,
                  ScopeEnd,
                  Conditional,
                  InstructionLine,
                  Conditional,
                  ScopeBegin,
                  InstructionLine,
                  ScopeEnd,
                  ScopeEnd ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

    def testFunctionRunloopDecl(self):
        code = """
               interrupt main()
               {
                   forever
                   {
                       cpx #$44
                       if(not equal)
                       {
                           lda  0x0200,x
                           inx
                           ora  0x0200,x
                           inx
                       }
                       else
                       {
                           switch(REG.Y)
                           {
                               case #1K
                               {
                                   cpy  1024
                                   if(equal)
                                   {
                                       dec $4400,X
                                   }
                               }
                               default
                                   dec 0x4400
                           }
                       }
                   }
               }
               """
        types = [ Function,
                  ScopeBegin,
                  Conditional,
                  ScopeBegin,
                  InstructionLine,
                  Conditional,
                  ScopeBegin,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  ScopeEnd,
                  Conditional,
                  ScopeBegin,
                  Conditional,
                  ScopeBegin,
                  Conditional,
                  ScopeBegin,
                  InstructionLine,
                  Conditional,
                  ScopeBegin,
                  InstructionLine,
                  ScopeEnd,
                  ScopeEnd,
                  Conditional,
                  InstructionLine,
                  ScopeEnd,
                  ScopeEnd,
                  ScopeEnd,
                  ScopeEnd ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

 
