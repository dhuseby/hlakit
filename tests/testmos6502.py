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
from hlakit.common.enum import Enum
from hlakit.common.name import Name
from hlakit.common.session import Session
from hlakit.common.symboltable import SymbolTable
from hlakit.common.typeregistry import TypeRegistry
from hlakit.common.codeblock import CodeBlock
from hlakit.common.codeline import CodeLine
from hlakit.common.numericvalue import NumericValue
from hlakit.common.function import Function
from hlakit.common.functionreturn import FunctionReturn
from hlakit.common.conditional import Conditional
from hlakit.common.label import Label
from hlakit.cpu.mos6502 import MOS6502Preprocessor, MOS6502Compiler
from hlakit.cpu.mos6502.interrupt import InterruptStart, InterruptNMI, InterruptIRQ
from hlakit.cpu.mos6502.register import Register
from hlakit.cpu.mos6502.opcode import Opcode
from hlakit.cpu.mos6502.operand import Operand
from hlakit.cpu.mos6502.instructionline import InstructionLine
from hlakit.cpu.mos6502.conditionaldecl import ConditionalDecl
from hlakit.common.functiontype import FunctionType
from hlakit.common.functionparameter import FunctionParameter
from hlakit.common.functiondecl import FunctionDecl
from hlakit.common.functioncall import FunctionCall
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd
from hlakit.common.immediate import Immediate
from hlakit.common.variable import Variable
from hlakit.common.variableinitializer import VariableInitializer

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

    def testInitialTypes(self):
        tr = TypeRegistry()
        types = Session().basic_types()
        for t in types:
            self.assertTrue(tr[t.get_name()] != None)

    pp_intstart = '#interrupt.start %s\n'
    pp_intnmi = '#interrupt.nmi %s\n'
    pp_intirq = '#interrupt.irq %s\n'

    def testInterruptStart(self):
        pp = Session().preprocessor()

        tokens = pp.parse(StringIO(self.pp_intstart % 'start'))
        self.assertTrue(isinstance(tokens[1], InterruptStart))
        self.assertEquals(tokens[1].get_fn(), 'start')

    def testBadInterruptStart(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_intstart % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testInterruptNMI(self):
        pp = Session().preprocessor()

        tokens = pp.parse(StringIO(self.pp_intnmi % 'vblank'))
        self.assertTrue(isinstance(tokens[1], InterruptNMI))
        self.assertEquals(tokens[1].get_fn(), 'vblank')

    def testBadInterruptNMI(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_intnmi % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testInterruptIRQ(self):
        pp = Session().preprocessor()

        tokens = pp.parse(StringIO(self.pp_intirq % 'timer'))
        self.assertTrue(isinstance(tokens[1], InterruptIRQ))
        self.assertEquals(tokens[1].get_fn(), 'timer')

    def testBadInterruptStart(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_intirq % ''))
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
        Label.reset_state()

    def _checkScannerParserResolver(self, cc, scanner, parser, resolver):
        # check the scanner output
        self.assertEquals(len(cc.get_scanner_output()), len(scanner))
        for i in range(0,len(scanner)):
            self.assertTrue(isinstance(cc.get_scanner_output()[i], scanner[i][0]), '%d' % i)
            self.assertEquals(str(cc.get_scanner_output()[i]), scanner[i][1], '%d' % i)

        # check the parser output
        self.assertEquals(len(cc.get_parser_output()), len(parser))
        for i in range(0,len(parser)):
            self.assertTrue(isinstance(cc.get_parser_output()[i], parser[i][0]), '%d' % i)
            self.assertEquals(str(cc.get_parser_output()[i]), parser[i][1], '%d' % i)

        # check the resolver output
        self.assertEquals(len(cc.get_resolver_output()), len(resolver))
        for i in range(0,len(resolver)):
            self.assertTrue(isinstance(cc.get_resolver_output()[i], resolver[i][0]), '%d' % i)
            self.assertEquals(str(cc.get_resolver_output()[i]), resolver[i][1], '%d' % i)

    def testCompiler(self):
        session = Session()
        self.assertTrue(isinstance(session.compiler(), MOS6502Compiler))

    def testLineNoOperand(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('clc')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'clc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMP)

    def testTwoLinesNoOperand(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('clc'), CodeLine('cli')])])
        self.assertEquals(len(cc.get_output()), 2)
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'clc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMP)
        self.assertTrue(isinstance(cc.get_output()[1], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[1].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[1].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[1].get_opcode().get_op()), 'cli')
        self.assertEquals(cc.get_output()[1].get_operand().get_mode(), Operand.IMP)


    def testLineAddr(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('ldx $D010')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'ldx')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.ABS)
        self.assertEquals(int(cc.get_output()[0].get_operand().get_addr()), 0xD010)

    def testLineImm(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('ldx #$22')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'ldx')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), 0x22)

    def testLineIndexed(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc $2200,x')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.ABS_X)
        self.assertEquals(int(cc.get_output()[0].get_operand().get_addr()), 0x2200)
        self.assertEquals(str(cc.get_output()[0].get_operand().get_reg()), 'x')

    def testLineIndexedIndirect(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('jmp ($2200,x)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'jmp')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.ABS_IDX_IND)
        self.assertEquals(int(cc.get_output()[0].get_operand().get_addr()), 0x2200)
        self.assertEquals(str(cc.get_output()[0].get_operand().get_reg()), 'x')

    def testLineZPIndexedIndirect(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('lsr ($22),y')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'lsr')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.ZP_IND_IDX)
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
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), 1)

    def testImmVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #foo')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.UNK)
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
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), 2)

    def testImmSignNumber(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #-1')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), -1)

    def testImmSignVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #-foo')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.UNK)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.SIGN)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[1], Name))

    def testImmSignMath(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #-(1+1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), -2)

    def testImmSizeofNumber(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #sizeof(1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), 1)

    def testImmSizeofVariable(self):
        cc = Session().compiler()

        # pre-define the function 'foo'
        st = SymbolTable()
        st.reset_state()
        st.new_symbol(Variable(Name('foo'), FunctionType('function')))

        cc.compile([CodeBlock([CodeLine('adc #sizeof(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.UNK)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.SIZEOF)
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0], 'sizeof')
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[1], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[1].get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[1].get_args()[0], Name))

    def testImmSizeofMath(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #sizeof(1+1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), 1)

    def testImmLoNumber(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #lo(1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), 1)

    def testImmLoVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #lo(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.UNK)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.LO)
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0], 'lo')
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[1], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[1].get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[1].get_args()[0], Name))

    def testImmLoMath(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #lo(1+1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), 2)

    def testImmHiNumber(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #hi(1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), 0)

    def testImmHiVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #hi(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.UNK)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_type(), Immediate.HI)
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[0], 'hi')
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[1], Immediate))
        self.assertEquals(cc.get_output()[0].get_operand().get_value().get_args()[1].get_type(), Immediate.TERMINAL)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value().get_args()[1].get_args()[0], Name))

    def testImmHiMath(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('adc #hi(1+1)')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'adc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMM)
        self.assertTrue(isinstance(cc.get_output()[0].get_operand().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_operand().get_value()), 0)

    def testImpliedAddress(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('clc')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'clc')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.IMP)

    def testAccumulatorRegAddress(self):
        cc = Session().compiler()
        cc.compile([CodeBlock([CodeLine('ror REG.A')])])
        self.assertTrue(isinstance(cc.get_output()[0], InstructionLine))
        self.assertTrue(isinstance(cc.get_output()[0].get_opcode(), Opcode))
        self.assertTrue(isinstance(cc.get_output()[0].get_operand(), Operand))
        self.assertEquals(str(cc.get_output()[0].get_opcode().get_op()), 'ror')
        self.assertEquals(cc.get_output()[0].get_operand().get_mode(), Operand.ACC)

    def testComplexVariableDecl(self):
        code = """
            byte _b_temp, _b_temp2
            word _w_temp
            """
        types = [ Variable,
                  Variable,
                  Variable ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

    def testComplexVariableDecls(self):
        code = """
            byte _b_temp
            word _w_temp
            pointer _p_temp, _jsrind_temp
            byte _b_remainder,
            _random_value,
            _random_ticks
            pointer _mem_src, _mem_dest
            """
        types = [ Variable,
                  Variable,
                  Variable,
                  Variable,
                  Variable,
                  Variable,
                  Variable,
                  Variable,
                  Variable ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

    def testComplexEnum(self):
        code = """
            enum PPU {
                CNT0        = $2000,
                CNT1        = $2001,
                STATUS      = $2002,
                ADDRESS     = $2006,
                IO          = $2007,
                SPR_ADDRESS = $2003,
                SPR_IO      = $2004,
                SPR_DMA     = $4014,
                BG_SCROLL   = $2005
            }
            """
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertTrue(isinstance(cc.get_output()[0], Enum))
        self.assertTrue(cc.get_output()[0].has_member('CNT0'))
        self.assertTrue(cc.get_output()[0].has_member('CNT1'))
        self.assertTrue(cc.get_output()[0].has_member('STATUS'))
        self.assertTrue(cc.get_output()[0].has_member('ADDRESS'))
        self.assertTrue(cc.get_output()[0].has_member('IO'))
        self.assertTrue(cc.get_output()[0].has_member('SPR_ADDRESS'))
        self.assertTrue(cc.get_output()[0].has_member('SPR_IO'))
        self.assertTrue(cc.get_output()[0].has_member('SPR_DMA'))
        self.assertTrue(cc.get_output()[0].has_member('BG_SCROLL'))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('CNT0'), Enum.Member))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('CNT1'), Enum.Member))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('STATUS'), Enum.Member))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('ADDRESS'), Enum.Member))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('IO'), Enum.Member))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('SPR_ADDRESS'), Enum.Member))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('SPR_IO'), Enum.Member))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('SPR_DMA'), Enum.Member))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('BG_SCROLL'), Enum.Member))
        self.assertEquals(int(cc.get_output()[0].get_member('CNT0').get_value()), 8192)
        self.assertEquals(int(cc.get_output()[0].get_member('CNT1').get_value()), 8193)
        self.assertEquals(int(cc.get_output()[0].get_member('STATUS').get_value()), 8194)
        self.assertEquals(int(cc.get_output()[0].get_member('ADDRESS').get_value()), 8198)
        self.assertEquals(int(cc.get_output()[0].get_member('IO').get_value()), 8199)
        self.assertEquals(int(cc.get_output()[0].get_member('SPR_ADDRESS').get_value()), 8195)
        self.assertEquals(int(cc.get_output()[0].get_member('SPR_IO').get_value()), 8196)
        self.assertEquals(int(cc.get_output()[0].get_member('SPR_DMA').get_value()), 16404)
        self.assertEquals(int(cc.get_output()[0].get_member('BG_SCROLL').get_value()), 8197)

    def testBlockOfCode(self):
        code = """
               clc
               adc #sizeof(SPR_OBJ)
               lda #lo(pproc)
               ora #hi(pproc)
               jsrind_f()
               """
        scanner = [ 
            (InstructionLine, 'clc <implied>'),
            (InstructionLine, 'adc <unresolved>'),
            (InstructionLine, 'lda <unresolved>'),
            (InstructionLine, 'ora <unresolved>'),
            (FunctionCall, 'jsrind_f()')
        ]
        parser = [
            (InstructionLine, 'clc <implied>'),
            (InstructionLine, 'adc <unresolved>'),
            (InstructionLine, 'lda <unresolved>'),
            (InstructionLine, 'ora <unresolved>'),
            (FunctionCall, 'jsrind_f()')
        ]
        resolver = [
            (InstructionLine, 'clc <implied>'),
            (InstructionLine, 'adc <unresolved>'),
            (InstructionLine, 'lda <unresolved>'),
            (InstructionLine, 'ora <unresolved>'),
            (InstructionLine, 'jsr jsrind_f')
        ]

        cc = Session().compiler()

        st = SymbolTable()
        st.reset_state()
        # pre-define the function 'jsrind_f'
        st.new_symbol(Function(FunctionDecl(Name('jsrind_f'), FunctionType('function'), [])))

        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

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
        scanner = [
            (FunctionDecl, 'function foo()'),
            (ScopeBegin, '{'),
            (InstructionLine, 'lda 0x0200,x'),
            (InstructionLine, 'inx <implied>'),
            (InstructionLine, 'ora 0x0200,x'),
            (InstructionLine, 'inx <implied>'),
            (ScopeEnd, '}')
        ]
        parser = [
            (Function, 'function foo()')
        ]
        resolver = [
            (Label, 'foo:'),
            (InstructionLine, 'lda 0x0200,x'),
            (InstructionLine, 'inx <implied>'),
            (InstructionLine, 'ora 0x0200,x'),
            (InstructionLine, 'inx <implied>'),
            (InstructionLine, 'rts')
        ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

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
        scanner = [
            (FunctionDecl, 'inline foo( addr )'),
            (ScopeBegin, '{'),
            (InstructionLine, 'lda <unresolved>'),
            (InstructionLine, 'inx <implied>'),
            (InstructionLine, 'ora <unresolved>'),
            (FunctionCall, 'jsrind_f()'),
            (InstructionLine, 'inx <implied>'),
            (ScopeEnd, '}'),
        ]
        parser = [
            (Function, 'inline foo( addr )'),
        ]
        resolver = [
            (Label, 'foo:'),
            (InstructionLine, 'lda <unresolved>'),
            (InstructionLine, 'inx <implied>'),
            (InstructionLine, 'ora <unresolved>'),
            (InstructionLine, 'jsr jsrind_f'),
            (InstructionLine, 'inx <implied>'),
        ]

        # pre-define the function 'jsrind_f'
        st = SymbolTable()
        st.new_symbol(FunctionDecl(Name('jsrind_f'), FunctionType('function'), []))

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testFunctionWithLabel(self):
        code = """
            inline div( dest, amount )
            {
                sec
                ldx #0
                lda amount

                while (nonzero) 
                {
                    bmi div_done_remainder
                    inx
                    sec
                    sbc dest
                }

                jmp div_done
            div_done_remainder:
                dex
            div_done:
                stx dest
            }
            """
        scanner = [
            (FunctionDecl, "inline div( dest, amount )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec <implied>"),
            (InstructionLine, "ldx #0"),
            (InstructionLine, "lda <unresolved>"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "bmi <unresolved>"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "sec <implied>"),
            (InstructionLine, "sbc <unresolved>"),
            (ScopeEnd, "}"),
            (InstructionLine, "jmp <unresolved>"),
            (Label, "div_done_remainder:"),
            (InstructionLine, "dex <implied>"),
            (Label, "div_done:"),
            (InstructionLine, "stx <unresolved>"),
            (ScopeEnd, "}"),
        ]
        parser = [
            (Function, "inline div( dest, amount )"),
        ]
        resolver = [
            (Label, "div:"),
            (InstructionLine, "sec <implied>"),
            (InstructionLine, "ldx #0"),
            (InstructionLine, "lda <unresolved>"),
            (Label, "HLA0:"),
            (InstructionLine, "bne HLA1"),
            (InstructionLine, "bmi <unresolved>"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "sec <implied>"),
            (InstructionLine, "sbc <unresolved>"),
            (Label, "HLA1:"),
            (InstructionLine, "jmp <unresolved>"),
            (Label, "div_done_remainder:"),
            (InstructionLine, "dex <implied>"),
            (Label, "div_done:"),
            (InstructionLine, "stx <unresolved>"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testFunctionWithReturn(self):
        code = """
            function vram_write_string()
            {
                ldy #0
                forever 
                {
                    lda (pstr), y
                    if (zero) 
                    {
                        return
                    }
                    iny
                }
            }
            """
        scanner = [
            (FunctionDecl, "function vram_write_string()"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldy #0"),
            (ConditionalDecl, "forever"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda <unresolved>"),
            (ConditionalDecl, "if(['zero'])"),
            (ScopeBegin, "{"),
            (FunctionReturn, "return"),
            (ScopeEnd, "}"),
            (InstructionLine, "iny <implied>"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
        ]
        parser = [
            (Function, "function vram_write_string()"),
        ]
        resolver = [
            (Label, "vram_write_string:"),
            (InstructionLine, "ldy #0"),
            (Label, "HLA0:"),
            (InstructionLine, "lda <unresolved>"),
            (InstructionLine, "beq HLA1"),
            (InstructionLine, "rts"),
            (Label, "HLA1:"),
            (InstructionLine, "iny <implied>"),
            (InstructionLine, "jmp HLA0"),
            (InstructionLine, "rts"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testInitializedArrayBeforeFunction(self):
        code = """
            byte setamt[] = {0,0,0,0,0,0,0,7}
            function dummy_fn()
            {
                ldy #0
            }
            """
        scanner = [
            (Variable, "byte setamt[]"),
            (VariableInitializer, " = { 0, 0, 0, 0, 0, 0, 0, 7 }"),
            (FunctionDecl, "function dummy_fn()"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldy #0"),
            (ScopeEnd, "}"),
        ]
        parser = [
            (Variable, "byte setamt[]"),
            (Function, "function dummy_fn()"),
        ]
        resolver = [
            (Variable, "byte setamt[]"),
            (Label, "dummy_fn:"),
            (InstructionLine, "ldy #0"),
            (InstructionLine, "rts"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testIfConditional(self):
        code = """
            if(set)
                inx
        """
        scanner = [
            (ConditionalDecl, "if(['set'])"),
            (InstructionLine, "inx <implied>"),
        ]
        parser = [
            (Conditional, "IF"),
        ]
        resolver = [
            (InstructionLine, "bne HLA0"),
            (InstructionLine, "inx <implied>"),
            (Label, "HLA0:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testIfNegatedConditional(self):
        code = """
            if(not 1)
                inx
        """
        scanner = [
            (ConditionalDecl, "if(['not', '1'])"),
            (InstructionLine, "inx <implied>"),
        ]
        parser = [
            (Conditional, "IF"),
        ]
        resolver = [
            (InstructionLine, "beq HLA0"),
            (InstructionLine, "inx <implied>"),
            (Label, "HLA0:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testIfFarConditional(self):
        code = """
            if(far carry)
                inx
        """
        scanner = [
            (ConditionalDecl, "if(['far', 'carry'])"),
            (InstructionLine, "inx <implied>"),
        ]
        parser = [
            (Conditional, "IF"),
        ]
        resolver = [
            (InstructionLine, "bcc HLA1"),
            (InstructionLine, "jmp HLA0"),
            (Label, "HLA1:"),
            (InstructionLine, "inx <implied>"),
            (Label, "HLA0:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testIfFarNegatedConditional(self):
        code = """
            if(far not overflow)
                inx
        """
        scanner = [
            (ConditionalDecl, "if(['far', 'not', 'overflow'])"),
            (InstructionLine, "inx <implied>"),
        ]
        parser = [
            (Conditional, "IF"),
        ]
        resolver = [
            (InstructionLine, "bvc HLA1"),
            (InstructionLine, "jmp HLA0"),
            (Label, "HLA1:"),
            (InstructionLine, "inx <implied>"),
            (Label, "HLA0:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)
       
    def testIfOneLinersConditional(self):
        code = """
               if (set)
                   if (zero)
                       inx
               """

        scanner = [
            (ConditionalDecl, 'if([\'set\'])'),
            (ConditionalDecl, 'if([\'zero\'])'),
            (InstructionLine, 'inx <implied>'),
        ]
        parser = [
            (Conditional, 'IF'),
        ]
        resolver = [
            (InstructionLine, 'bne HLA0'),
            (InstructionLine, 'beq HLA1'),
            (InstructionLine, 'inx <implied>'),
            (Label, 'HLA1:'),
            (Label, 'HLA0:'),
        ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

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

        scanner = [
            (ConditionalDecl, 'if([\'set\'])'),
            (ScopeBegin, '{'),
            (InstructionLine, 'inx <implied>'),
            (ScopeEnd, '}'),
            (ConditionalDecl, 'else'),
            (ScopeBegin, '{'),
            (InstructionLine, 'dex <implied>'),
            (ScopeEnd, '}'),
        ]
        parser = [
            (Conditional, 'IF_ELSE'),
        ]
        resolver = [
            (InstructionLine, 'bne HLA0'),
            (InstructionLine, 'dex <implied>'),
            (InstructionLine, 'jmp HLA1'),
            (Label, 'HLA0:'),
            (InstructionLine, 'inx <implied>'),
            (Label, 'HLA1:'),
        ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testWhileConditional(self):
        code = """
            while(true)
                inx
        """
        scanner = [
            (ConditionalDecl, "while(['true'])"),
            (InstructionLine, "inx <implied>"),
        ]
        parser = [
            (Conditional, "WHILE"),
        ]
        resolver = [
            (Label, "HLA0:"),
            (InstructionLine, "bne HLA1"),
            (InstructionLine, "inx <implied>"),
            (Label, "HLA1:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)
        
    def testWhileNegatedConditional(self):
        code = """
            while (not 0)
                inx
        """
        scanner = [
            (ConditionalDecl, "while(['not', '0'])"),
            (InstructionLine, "inx <implied>"),
        ]
        parser = [
            (Conditional, "WHILE"),
        ]
        resolver = [
            (Label, "HLA0:"),
            (InstructionLine, "bne HLA1"),
            (InstructionLine, "inx <implied>"),
            (Label, "HLA1:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)
        
    def testWhileFarConditional(self):
        code = """
            while(far unset)
                inx
        """
        scanner = [
            (ConditionalDecl, "while(['far', 'unset'])"),
            (InstructionLine, "inx <implied>"),
        ]
        parser = [
            (Conditional, "WHILE"),
        ]
        resolver = [
            (Label, "HLA0:"),
            (InstructionLine, "beq HLA2"),
            (InstructionLine, "jmp HLA1"),
            (Label, "HLA2:"),
            (InstructionLine, "inx <implied>"),
            (Label, "HLA1:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)
        
    def testWhileFarNegatedConditional(self):
        code = """
            while(far not clear)
                inx
        """
        scanner = [
            (ConditionalDecl, "while(['far', 'not', 'clear'])"),
            (InstructionLine, "inx <implied>"),
        ]
        parser = [
            (Conditional, "WHILE"),
        ]
        resolver = [
            (Label, "HLA0:"),
            (InstructionLine, "bne HLA2"),
            (InstructionLine, "jmp HLA1"),
            (Label, "HLA2:"),
            (InstructionLine, "inx <implied>"),
            (Label, "HLA1:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)
        
    def testWhileBlockConditional(self):
        code = """
               while (plus)
               {
                   inx
                   dex
               }
               """
        scanner = [
            (ConditionalDecl, "while(['plus'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "dex <implied>"),
            (ScopeEnd, "}"),
        ]
        parser = [
            (Conditional, "WHILE"),
        ]
        resolver = [
            (Label, "HLA0:"),
            (InstructionLine, "bpl HLA1"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "dex <implied>"),
            (Label, "HLA1:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testDoWhileBlockConditional(self):
        code = """
               do
               {
                   inx
                   dex
               }
               while (positive)
               """
        scanner = [
            ( ConditionalDecl, 'do'),
            ( ScopeBegin, '{'),
            ( InstructionLine, 'inx <implied>'),
            ( InstructionLine, 'dex <implied>'),
            ( ScopeEnd, '}'),
            ( ConditionalDecl, 'while([\'positive\'])' )
        ]
        parser = [
            ( Conditional, 'DO_WHILE')
        ]
        resolver = [
            ( Label, 'HLA0:'),
            ( InstructionLine, 'inx <implied>'),
            ( InstructionLine, 'dex <implied>'),
            ( InstructionLine, 'bpl HLA0')
        ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testForeverConditional(self):
        code = """
            forever
            {
                inx
            }
        """
        scanner = [
            (ConditionalDecl, "forever"),
            (ScopeBegin, "{"),
            (InstructionLine, "inx <implied>"),
            (ScopeEnd, "}"),
        ]
        parser = [
            (Conditional, "FOREVER"),
        ]
        resolver = [
            (Label, "HLA0:"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "jmp HLA0"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)
        
    def testSwitchConditional(self):
        code = """
            switch(x)
            {
                case #1
                    inx
            }
        """
        scanner = [
            (ConditionalDecl, "switch(['x'])"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "case([1])"),
            (InstructionLine, "inx <implied>"),
            (ScopeEnd, "}"),
        ]
        parser = [
            (Conditional, "SWITCH"),
        ]
        resolver = [
            (InstructionLine, "cpx #1"),
            (InstructionLine, "bne HLA1"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "jmp HLA0"),
            (Label, "HLA1:"),
            (Label, "HLA0:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)
        
    def testSwitchCapitalConditional(self):
        code = """
            switch(A)
            {
                case #1
                    inx
            }
        """
        scanner = [
            (ConditionalDecl, "switch(['a'])"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "case([1])"),
            (InstructionLine, "inx <implied>"),
            (ScopeEnd, "}"),
        ]
        parser = [
            (Conditional, "SWITCH"),
        ]
        resolver = [
            (InstructionLine, "cmp #1"),
            (InstructionLine, "bne HLA1"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "jmp HLA0"),
            (Label, "HLA1:"),
            (Label, "HLA0:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testSwitchRegDotConditional(self):
        code = """
            switch(reg.y)
            {
                case #1
                    inx
            }
        """
        scanner = [
            (ConditionalDecl, "switch(['y'])"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "case([1])"),
            (InstructionLine, "inx <implied>"),
            (ScopeEnd, "}"),
        ]
        parser = [
            (Conditional, "SWITCH"),
        ]
        resolver = [
            (InstructionLine, "cpy #1"),
            (InstructionLine, "bne HLA1"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "jmp HLA0"),
            (Label, "HLA1:"),
            (Label, "HLA0:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)
        
    def testSwitchRegDotCapitalConditional(self):
        code = """
            switch(REG.X)
            {
                case #1
                    inx
            }
        """
        scanner = [
            (ConditionalDecl, "switch(['x'])"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "case([1])"),
            (InstructionLine, "inx <implied>"),
            (ScopeEnd, "}"),
        ]
        parser = [
            (Conditional, "SWITCH"),
        ]
        resolver = [
            (InstructionLine, "cpx #1"),
            (InstructionLine, "bne HLA1"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "jmp HLA0"),
            (Label, "HLA1:"),
            (Label, "HLA0:"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)
        
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
        scanner = [
            (ConditionalDecl, 'switch([\'x\'])'),
            (ScopeBegin, '{'),
            (ConditionalDecl, 'case([sizeof(bar)])'),
            (ScopeBegin, '{'),
            (InstructionLine, 'inx <implied>'),
            (ScopeEnd, '}'),
            (ConditionalDecl, 'case([0x0200])'),
            (InstructionLine, 'dex <implied>'),
            (ConditionalDecl, 'default'),
            (ScopeBegin, '{'),
            (InstructionLine, 'lda $0300'),
            (ScopeEnd, '}'),
            (ScopeEnd, '}'),
        ]
        parser = [
            (Conditional, 'SWITCH_DEFAULT'),
        ]
        resolver = [
            (InstructionLine, 'cpx #sizeof(bar)'),
            (InstructionLine, 'bne HLA1'),
            (InstructionLine, 'inx <implied>'),
            (InstructionLine, 'jmp HLA0'),
            (Label, 'HLA1:'),
            (InstructionLine, 'cpx #0x0200'),
            (InstructionLine, 'bne HLA2'),
            (InstructionLine, 'dex <implied>'),
            (InstructionLine, 'jmp HLA0'),
            (Label, 'HLA2:'),
            (InstructionLine, 'lda $0300'),
            (Label, 'HLA0:'),
        ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

    def testFunctionRunloopDecl(self):
        code = """
               interrupt noreturn main()
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
                                   cpy  #1024
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
        scanner = [
            (FunctionDecl, "interrupt noreturn main()"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "forever"),
            (ScopeBegin, "{"),
            (InstructionLine, "cpx #$44"),
            (ConditionalDecl, "if(['not', 'equal'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda 0x0200,x"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "ora 0x0200,x"),
            (InstructionLine, "inx <implied>"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "else"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "switch(['y'])"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "case([1K])"),
            (ScopeBegin, "{"),
            (InstructionLine, "cpy #1024"),
            (ConditionalDecl, "if(['equal'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "dec $4400,x"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "default"),
            (InstructionLine, "dec 0x4400"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
        ]
        parser = [
            (Function, "interrupt noreturn main()"),
        ]
        resolver = [
            (Label, "main:"),
            (Label, "HLA0:"),
            (InstructionLine, "cpx #$44"),
            (InstructionLine, "bne HLA1"),
            (InstructionLine, "cpy #1K"),
            (InstructionLine, "bne HLA4"),
            (InstructionLine, "cpy #1024"),
            (InstructionLine, "beq HLA5"),
            (InstructionLine, "dec $4400,x"),
            (Label, "HLA5:"),
            (InstructionLine, "jmp HLA3"),
            (Label, "HLA4:"),
            (InstructionLine, "dec 0x4400"),
            (Label, "HLA3:"),
            (InstructionLine, "jmp HLA2"),
            (Label, "HLA1:"),
            (InstructionLine, "lda 0x0200,x"),
            (InstructionLine, "inx <implied>"),
            (InstructionLine, "ora 0x0200,x"),
            (InstructionLine, "inx <implied>"),
            (Label, "HLA2:"),
            (InstructionLine, "jmp HLA0"),
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

