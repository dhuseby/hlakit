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
from hlakit.cpu.mos6502 import MOS6502Preprocessor, MOS6502Compiler
from hlakit.cpu.mos6502.interrupt import InterruptStart, InterruptNMI, InterruptIRQ
from hlakit.cpu.mos6502.register import Register
from hlakit.cpu.mos6502.opcode import Opcode
from hlakit.cpu.mos6502.operand import Operand
from hlakit.cpu.mos6502.instructionline import InstructionLine
from hlakit.common.functiontype import FunctionType
from hlakit.common.functionparameter import FunctionParameter
from hlakit.common.function import Function
from hlakit.common.functioncall import FunctionCall

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
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), 0x22)

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

    def testLineFunctionCallImm(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #sizeof(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_name(), Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_params(), list))
        self.assertTrue(len(cc.get_output()[0].get_operand().get_value().get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_params()[0], FunctionParameter))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_name().get_name(), 'sizeof')
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type().get_type(), 'operator')
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_params()[0].get_symbol(), 'foo')

    def testLineFunctionCallImm2(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('lda #hi(bar)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'lda')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_name(), Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_params(), list))
        self.assertTrue(len(cc.get_output()[0].get_operand().get_value().get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_params()[0], FunctionParameter))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_name().get_name(), 'hi')
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type().get_type(), 'operator')
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_params()[0].get_symbol(), 'bar')

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
        # pre-define the function 'jsrind_f'
        st.new_symbol(Function(Name('jsrind_f'), FunctionType('function'), []))
        # pre-define the macro 'assign_16i'
        st.new_symbol(Function(Name('assign_16i'), FunctionType('inline'), 
                               [FunctionParameter('one'), FunctionParameter('two')]))

        cb = build_code_block(code)
        cc.compile([cb])
        self.assertTrue(len(cc.get_output()) == 6)
        for i in range(0,6):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))
