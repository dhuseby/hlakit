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
import unittest
from pyparsing import ParseException, ParseFatalException
from cStringIO import StringIO
from tests.utils import build_code_block 
from hlakit.common.session import Session
from hlakit.common.filemarkers import FileBegin, FileEnd
from hlakit.common.rampp import RamOrg, RamEnd
from hlakit.common.rompp import RomEnd, RomBank, RomBanksize
from hlakit.common.setpad import SetPad
from hlakit.common.codeblock import CodeBlock
from hlakit.common.variable import Variable
from hlakit.common.function import Function
from hlakit.common.functiondecl import FunctionDecl
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd
from hlakit.common.label import Label
from hlakit.common.conditional import Conditional
from hlakit.common.symboltable import SymbolTable
from hlakit.common.typeregistry import TypeRegistry
from hlakit.cpu.mos6502.instructionline import InstructionLine
from hlakit.cpu.mos6502.conditionaldecl import ConditionalDecl
from hlakit.platform.lynx.preprocessor import Preprocessor as LynxPreprocessor
from hlakit.platform.lynx.compiler import Compiler as LynxCompiler
from hlakit.platform.lynx.generator import Generator as LynxGenerator
from hlakit.platform.lynx.loader import LynxLoader
from hlakit.platform.lynx.lnx import Lnx
from hlakit.platform.lynx.lnxsetting import LnxSetting
from hlakit.platform.lynx.rompp import LynxRomOrg

class LynxTester(unittest.TestCase):
    def setUp(self):
        Session().parse_args(['--platform=Lynx'])

    def tearDown(self):
        Session().preprocessor().reset_state()
        Session().compiler().reset_state()
        TypeRegistry().reset_state()
        SymbolTable().reset_state()
        Label.reset_state()

    def testLynxPreprocessor(self):
        self.assertTrue(isinstance(Session().preprocessor(), LynxPreprocessor))

    def testLynxCompiler(self):
        self.assertTrue(isinstance(Session().compiler(), LynxCompiler))

    def testLynxGenerator(self):
        self.assertTrue(isinstance(Session().generator(), LynxGenerator))


class LynxPreprocessorTester(LynxTester):
    """
    This class aggregates all of the tests for the Lynx Preprocessor
    """

    pp_lynxloader = '#lynx.loader %s'

    def testLynxLoader(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_lynxloader % 'loader'))
        self.assertTrue(isinstance(tokens[1], LynxLoader))
        self.assertEquals(tokens[1].get_fn(), 'loader')

    def testBadLynxLoader(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_lynxloader % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    pp_lnxoff = '#lnx.off'
    pp_psb0 = '#lnx.page_size_bank0 %s'
    pp_psb1 = '#lnx.page_size_bank1 %s'
    pp_version = '#lnx.version %s'
    pp_cart_name = '#lnx.cart_name %s'
    pp_manu_name = '#lnx.manufacturer_name %s'
    pp_rotation = '#lnx.rotation %s'

    def testLnxOff(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_lnxoff))
        self.assertTrue(isinstance(tokens[1], LnxSetting))

    def testLnxPSB0(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_psb0 % '2K'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.PSB0)
        self.assertEquals(int(tokens[1].get_size()), 2048)

    def testLnxPSB0Label(self):
        pp = Session().preprocessor() 

        pp.set_symbol('FOO', 1024)
        tokens = pp.parse(StringIO(self.pp_psb0 % 'FOO'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.PSB0)
        self.assertEquals(int(tokens[1].get_size()), 1024)

    def testBadLnxPSB0(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_psb0 % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testLnxPSB1(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_psb1 % '2K'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.PSB1)
        self.assertEquals(int(tokens[1].get_size()), 2048)

    def testLnxPSB1Label(self):
        pp = Session().preprocessor() 

        pp.set_symbol('FOO', 1024)
        tokens = pp.parse(StringIO(self.pp_psb1 % 'FOO'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.PSB1)
        self.assertEquals(int(tokens[1].get_size()), 1024)

    def testBadLnxPSB1(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_psb1 % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testLnxVersion(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_version % '1'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.VERSION)
        self.assertEquals(int(tokens[1].get_version()), 1)

    def testLnxVersionLabel(self):
        pp = Session().preprocessor() 

        pp.set_symbol('FOO', 1)
        tokens = pp.parse(StringIO(self.pp_version % 'FOO'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.VERSION)
        self.assertEquals(int(tokens[1].get_version()), 1)

    def testBadLnxVersion(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_version % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testLnxCartName(self):
        pp = Session().preprocessor() 

        tokens = tokens = pp.parse(StringIO(self.pp_cart_name % '"CGD Demo Game"'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.CART_NAME)
        self.assertEquals(str(tokens[1].get_name()), 'CGD Demo Game')

    def testLnxCartNameLabel(self):
        pp = Session().preprocessor() 

        pp.set_symbol('FOO', "CGD Demo Game")
        tokens = tokens = pp.parse(StringIO(self.pp_cart_name % 'FOO'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.CART_NAME)
        self.assertEquals(tokens[1].get_name(), 'CGD Demo Game')

    def testBadLnxCartName(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_cart_name % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testLnxManuName(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_manu_name % '"ClassicGameDev.com"'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.MANU_NAME)
        self.assertEquals(str(tokens[1].get_name()), 'ClassicGameDev.com')

    def testLnxManuNameLabel(self):
        pp = Session().preprocessor() 

        pp.set_symbol('FOO', "ClassicGameDev.com")
        tokens = pp.parse(StringIO(self.pp_manu_name % 'FOO'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.MANU_NAME)
        self.assertEquals(tokens[1].get_name(), 'ClassicGameDev.com')

    def testBadLnxManuName(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_manu_name % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testLnxRotation(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_rotation % '"none"'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.ROTATION)
        self.assertEquals(str(tokens[1].get_rotation()), 'none')

    def testLnxRotationLabel(self):
        pp = Session().preprocessor() 

        pp.set_symbol('FOO', "left")
        tokens = pp.parse(StringIO(self.pp_rotation % 'FOO'))
        self.assertTrue(isinstance(tokens[1], LnxSetting))
        self.assertEquals(tokens[1].get_type(), LnxSetting.ROTATION)
        self.assertEquals(tokens[1].get_rotation(), 'left')

    def testBadLnxRotation(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_rotation % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    pp_romorg = '#rom.org %s'

    def testRomOrg(self):
        pp = Session().preprocessor()

        tokens = pp.parse(StringIO(self.pp_romorg % '0x10'))
        self.assertTrue(isinstance(tokens[1], LynxRomOrg))
        self.assertEquals(int(tokens[1].get_segment()), 0x10)
        self.assertEquals(int(tokens[1].get_counter()), 0)
        self.assertEquals(tokens[1].get_maxsize(), None)

    def testRomOrgCounter(self):
        pp = Session().preprocessor()

        tokens = pp.parse(StringIO(self.pp_romorg % '0x20, 0x0100'))
        self.assertTrue(isinstance(tokens[1], LynxRomOrg))
        self.assertEquals(int(tokens[1].get_segment()), 0x20)
        self.assertEquals(int(tokens[1].get_counter()), 0x0100)
        self.assertEquals(tokens[1].get_maxsize(), None)

    def testRomOrgCounterMaxsize(self):
        pp = Session().preprocessor()

        tokens = pp.parse(StringIO(self.pp_romorg % '0x20, 0x0100, 0x1000'))
        self.assertTrue(isinstance(tokens[1], LynxRomOrg))
        self.assertEquals(int(tokens[1].get_segment()), 0x20)
        self.assertEquals(int(tokens[1].get_counter()), 0x0100)
        self.assertEquals(int(tokens[1].get_maxsize()), 0x1000)

    def testRomOrgLabel(self):
        pp = Session().preprocessor()

        pp.set_symbol('FOO', 0x01)
        tokens = pp.parse(StringIO(self.pp_romorg % 'FOO'))
        self.assertTrue(isinstance(tokens[1], LynxRomOrg))
        self.assertEquals(int(tokens[1].get_segment()), 0x01)
        self.assertEquals(int(tokens[1].get_counter()), 0)
        self.assertEquals(tokens[1].get_maxsize(), None)

    def testRomOrgMaxsizeLabel(self):
        pp = Session().preprocessor()

        pp.set_symbol('FOO', 0x40)
        pp.set_symbol('BAR', 0x0400)
        tokens = pp.parse(StringIO(self.pp_romorg % 'FOO, BAR'))
        self.assertTrue(isinstance(tokens[1], LynxRomOrg))
        self.assertEquals(int(tokens[1].get_segment()), 0x40)
        self.assertEquals(int(tokens[1].get_counter()), 0x0400)
        self.assertEquals(tokens[1].get_maxsize(), None)

    def testRomOrgCounterMaxsizeLabel(self):
        pp = Session().preprocessor()

        pp.set_symbol('FOO', 0x20)
        pp.set_symbol('BAR', 0x0200)
        pp.set_symbol('BAZ', 0x2000)
        tokens = pp.parse(StringIO(self.pp_romorg % 'FOO, BAR, BAZ'))
        self.assertTrue(isinstance(tokens[1], LynxRomOrg))
        self.assertEquals(int(tokens[1].get_segment()), 0x20)
        self.assertEquals(int(tokens[1].get_counter()), 0x0200)
        self.assertEquals(int(tokens[1].get_maxsize()), 0x2000)

    def testRomOrgCounterWithComment(self):
        pp = Session().preprocessor()

        tokens = pp.parse(StringIO(self.pp_romorg % '0x01, 0x0100 // hello'))
        self.assertTrue(isinstance(tokens[1], LynxRomOrg))
        self.assertEquals(int(tokens[1].get_segment()), 0x01)
        self.assertEquals(int(tokens[1].get_counter()), 0x0100)
        self.assertEquals(tokens[1].get_maxsize(), None)

    def testBadRomOrg(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_romorg % ''))
            self.assertTrue(False)
        except ParseException:
            pass

class LynxCompilerTester(LynxTester):
    """
    This class aggregates all of the tests for the Lynx Compiler
    """
    pass


class LynxLnxTester(LynxTester):
    """
    This class aggregates all of the tests for the Lynx .LNX header class
    """

    VALID_HEADER = 'LYNX\x00\x04\x00\x00\x01\x00CALGAMES.040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Atari\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

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

    def testBasicLnxHeader(self):
        lnx = Lnx()
        lnx.set_page_size_bank0(1024)
        lnx.set_page_size_bank1(0)
        lnx.set_version(1)
        lnx.set_cart_name('CALGAMES.040')
        lnx.set_manufacturer_name('Atari')
        lnx.set_rotation(lnx.ROTATE_NONE)

        outf = StringIO()
        lnx.save_header(outf)

        self.assertEquals(self.VALID_HEADER, outf.getvalue())


    def testRoundTrip(self):
        inf = StringIO(self.VALID_HEADER)
        lnx = Lnx()
        lnx.load_header(inf)
        outf = StringIO()
        lnx.save_header(outf)
        self.assertEquals(self.VALID_HEADER, outf.getvalue())

    def testUnencryptedLoaderRom(self):
        code = """
            #lnx.page_size_bank0    2K  // 512K bank size
            #lnx.page_size_bank1    0   // there is only one bank
            #lnx.version            1
            #lnx.cart_name          "CGD Demo Game"
            #lnx.manufacturer_name  "ClassGameDev.com"
            #lnx.rotation           "none"
            #rom.bank               0
            #setpad                 0
            #rom.org                0,0,256
            #ram.org                0x0200
            
            byte CART_BANK_0                :$FCB2  // uses CART0/ as strobe
            byte MIKEY_SYSTEM_CONTROL       :$FD87
            byte MIKEY_IO_DIRECTION         :$FD8A  // direction control register
            byte MIKEY_GPIO                 :$FD8B  // general purpose I/O register
            byte MIKEY_SERIAL_CONTROL       :$FD8C
            byte MIKEY_MEMORY_MAP_CONTROL   :$FFF9
            
            #define SECONDARY_LOADER $FB00
            function noreturn micro_loader()
            {
                // 1. force Mikey to be in memory
                lda #0
                sta MIKEY_MEMORY_MAP_CONTROL

                // 2. set IODIR the way Mikey ROM does, also force AUDIN to 
                //    output
                lda #%00010011    
                sta MIKEY_IO_DIRECTION

                // 3. set ComLynx to open collector
                lda #%00000100
                sta MIKEY_SERIAL_CONTROL

                // 4. make sure the ROM is powered on
                lda #%00001000
                sta MIKEY_GPIO

                // 5. read in 256 bytes from the cart and store it in RAM
                ldx #0
                do
                {
                    // read a byte from the cart, bank 0
                    lda CART_BANK_0

                    // store it in the desired location
                    sta SECONDARY_LOADER,x

                    // move destination index
                    inx

                } while(not zero)

                // do a blind jmp to the second stage loader
                jmp SECONDARY_LOADER 
            }

            #ram.end
            #rom.end
            """

        # PREPROCESSOR PASS
        expected_pp_tokens = [ 
            (FileBegin, 'FileBegin: DummyFile'),
            (LnxSetting, '#lnx.page_size_bank0 2K'),
            (LnxSetting, '#lnx.page_size_bank1'),
            (LnxSetting, '#lnx.version 1'),
            (LnxSetting, '#lnx.cart_name "CGD Demo Game"'),
            (LnxSetting, '#lnx.manufacturer_name "ClassGameDev.com"'),
            (LnxSetting, '#lnx.rotation none'),
            (RomBank,    'RomBank <0>'),
            (SetPad, 'SetPad <0>'),
            (LynxRomOrg, 'LynxRomOrg <0x0>,<0x100>'),
            (RamOrg,      'RamOrg <0x200>'),
            (CodeBlock, """byte CART_BANK_0                :$FCB2  // uses CART0/ as strobe
byte MIKEY_SYSTEM_CONTROL       :$FD87
byte MIKEY_IO_DIRECTION         :$FD8A  // direction control register
byte MIKEY_GPIO                 :$FD8B  // general purpose I/O register
byte MIKEY_SERIAL_CONTROL       :$FD8C
byte MIKEY_MEMORY_MAP_CONTROL   :$FFF9
function noreturn micro_loader()
{
lda #0
sta MIKEY_MEMORY_MAP_CONTROL
lda #%00010011
sta MIKEY_IO_DIRECTION
lda #%00000100
sta MIKEY_SERIAL_CONTROL
lda #%00001000
sta MIKEY_GPIO
ldx #0
do
{
lda CART_BANK_0
sta $FB00,x
inx
} while(not zero)
jmp $FB00
}
"""),
            (RamEnd, 'RamEnd'),
            (RomEnd, 'RomEnd'),
            (FileEnd, 'FileEnd: DummyFile')
        ]
        pp = Session().preprocessor()

        # open input and run it through the pre-processor
        inf = StringIO(code)
        pp_tokens = pp.parse(inf)
        inf.close()

        self.assertEquals(len(pp_tokens), len(expected_pp_tokens))
        for i in range(0, len(expected_pp_tokens)):
            self.assertTrue(isinstance(pp_tokens[i], expected_pp_tokens[i][0]))
            self.assertEqual(str(pp_tokens[i]), expected_pp_tokens[i][1], 'token %d' % i)

        # COMPILER PASS
        scanner = [
            (FileBegin, "FileBegin: DummyFile"),
            (LnxSetting, "#lnx.page_size_bank0 2K"),
            (LnxSetting, "#lnx.page_size_bank1"),
            (LnxSetting, "#lnx.version 1"),
            (LnxSetting, '#lnx.cart_name "CGD Demo Game"'),
            (LnxSetting, '#lnx.manufacturer_name "ClassGameDev.com"'),
            (LnxSetting, "#lnx.rotation none"),
            (RomBank, "RomBank <0>"),
            (SetPad, "SetPad <0>"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x100>"),
            (RamOrg, "RamOrg <0x200>"),
            (Variable, "byte CART_BANK_0 :$FCB2"),
            (Variable, "byte MIKEY_SYSTEM_CONTROL :$FD87"),
            (Variable, "byte MIKEY_IO_DIRECTION :$FD8A"),
            (Variable, "byte MIKEY_GPIO :$FD8B"),
            (Variable, "byte MIKEY_SERIAL_CONTROL :$FD8C"),
            (Variable, "byte MIKEY_MEMORY_MAP_CONTROL :$FFF9"),
            (FunctionDecl, "function noreturn micro_loader()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta $FFF9"),
            (InstructionLine, "lda #%00010011"),
            (InstructionLine, "sta $FD8A"),
            (InstructionLine, "lda #%00000100"),
            (InstructionLine, "sta $FD8C"),
            (InstructionLine, "lda #%00001000"),
            (InstructionLine, "sta $FD8B"),
            (InstructionLine, "ldx #0"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda $FCB2"),
            (InstructionLine, "sta $FB00,x"),
            (InstructionLine, "inx"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (InstructionLine, "jmp $FB00"),
            (ScopeEnd, "}"),
            (RamEnd, "RamEnd"),
            (RomEnd, "RomEnd"),
            (FileEnd, "FileEnd: DummyFile"),
        ]
        parser = [
            (LnxSetting, "#lnx.page_size_bank0 2K"),
            (LnxSetting, "#lnx.page_size_bank1"),
            (LnxSetting, "#lnx.version 1"),
            (LnxSetting, '#lnx.cart_name "CGD Demo Game"'),
            (LnxSetting, '#lnx.manufacturer_name "ClassGameDev.com"'),
            (LnxSetting, "#lnx.rotation none"),
            (RomBank, "RomBank <0>"),
            (SetPad, "SetPad <0>"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x100>"),
            (RamOrg, "RamOrg <0x200>"),
            (Variable, "byte CART_BANK_0 :$FCB2"),
            (Variable, "byte MIKEY_SYSTEM_CONTROL :$FD87"),
            (Variable, "byte MIKEY_IO_DIRECTION :$FD8A"),
            (Variable, "byte MIKEY_GPIO :$FD8B"),
            (Variable, "byte MIKEY_SERIAL_CONTROL :$FD8C"),
            (Variable, "byte MIKEY_MEMORY_MAP_CONTROL :$FFF9"),
            (Function, "function noreturn micro_loader()"),
            (RamEnd, "RamEnd"),
            (RomEnd, "RomEnd"),
        ]
        resolver = [
            (LnxSetting, "#lnx.page_size_bank0 2K"),
            (LnxSetting, "#lnx.page_size_bank1"),
            (LnxSetting, "#lnx.version 1"),
            (LnxSetting, '#lnx.cart_name "CGD Demo Game"'),
            (LnxSetting, '#lnx.manufacturer_name "ClassGameDev.com"'),
            (LnxSetting, "#lnx.rotation none"),
            (RomBank, "RomBank <0>"),
            (SetPad, "SetPad <0>"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x100>"),
            (RamOrg, "RamOrg <0x200>"),
            (Variable, "byte CART_BANK_0 :$FCB2"),
            (Variable, "byte MIKEY_SYSTEM_CONTROL :$FD87"),
            (Variable, "byte MIKEY_IO_DIRECTION :$FD8A"),
            (Variable, "byte MIKEY_GPIO :$FD8B"),
            (Variable, "byte MIKEY_SERIAL_CONTROL :$FD8C"),
            (Variable, "byte MIKEY_MEMORY_MAP_CONTROL :$FFF9"),
            (Label, "HLA_micro_loader:"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta $FFF9"),
            (InstructionLine, "lda #%00010011"),
            (InstructionLine, "sta $FD8A"),
            (InstructionLine, "lda #%00000100"),
            (InstructionLine, "sta $FD8C"),
            (InstructionLine, "lda #%00001000"),
            (InstructionLine, "sta $FD8B"),
            (InstructionLine, "ldx #0"),
            (Label, "HLA0:"),
            (InstructionLine, "lda $FCB2"),
            (InstructionLine, "sta $FB00,x"),
            (InstructionLine, "inx"),
            (InstructionLine, "bne HLA0"),
            (InstructionLine, "jmp $FB00"),
            (RamEnd, "RamEnd"),
            (RomEnd, "RomEnd"),
        ]

        cc = Session().compiler()
        #import pdb; pdb.set_trace()
        cc.compile(pp_tokens, True)
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

        # GENERATOR PASS
        expected_listing = \
"""B SG CNT ADDR    LBL                  00 00 00    CODE
0 00 000 0000                                     .org $0200
0 00 000 0200    HLA_micro_loader:    a9 00       lda #0
0 00 002 0202                         8d f9 ff    sta $FFF9
0 00 005 0205                         a9 13       lda #%00010011
0 00 007 0207                         8d 8a fd    sta $FD8A
0 00 00a 020a                         a9 04       lda #%00000100
0 00 00c 020c                         8d 8c fd    sta $FD8C
0 00 00f 020f                         a9 08       lda #%00001000
0 00 011 0211                         8d 8b fd    sta $FD8B
0 00 014 0214                         a2 00       ldx #0
0 00 016 0216                HLA0:    ad b2 fc    lda $FCB2
0 00 019 0219                         9d 00 fb    sta $FB00,x
0 00 01c 021c                         e8          inx
0 00 01d 021d                         d0 f7       bne -9
0 00 01f 021f                         4c 00 fb    jmp $FB00
"""
        gen = Session().generator()

        # build the rom
        lnx = gen.build_rom(cc.get_output())
        self.assertEquals(expected_listing, lnx.get_debug_listing())

        # save the rom
        #outf = StringIO()
        #lnx.save(outf)

        # check the rom
        #self.assertEquals(expected_rom, outf.getvalue())


