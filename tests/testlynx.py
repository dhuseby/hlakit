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
from hlakit.common.functioncall import FunctionCall
from hlakit.common.functiondecl import FunctionDecl
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd
from hlakit.common.label import Label
from hlakit.common.conditional import Conditional
from hlakit.common.symboltable import SymbolTable
from hlakit.common.type_ import Type, TypeRegistry
from hlakit.common.buffer import Buffer
from hlakit.common.variableinitializer import VariableInitializer
from hlakit.cpu.mos6502.instructionline import InstructionLine
from hlakit.cpu.mos6502.conditionaldecl import ConditionalDecl
from hlakit.cpu.mos6502.interrupt import *
from hlakit.platform.lynx.preprocessor import Preprocessor as LynxPreprocessor
from hlakit.platform.lynx.compiler import Compiler as LynxCompiler
from hlakit.platform.lynx.generator import Generator as LynxGenerator
from hlakit.platform.lynx.romfilebank import RomFileBank as LnxRomFileBank
from hlakit.platform.lynx.loader import LynxLoader
from hlakit.platform.lynx.main import LynxMain
from hlakit.platform.lynx.lnx import Lnx
from hlakit.platform.lynx.lnxsetting import LnxSetting
from hlakit.platform.lynx.rompp import LynxRomOrg

class LynxTester(unittest.TestCase):
    def setUp(self):
        Session().parse_args(['--platform=Lynx'])

    def tearDown(self):
        Session().preprocessor().reset_state()
        Session().compiler().reset_state()
        Session().generator().reset_state()
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
            self.assertEquals(str(cc.get_resolver_output()[i]), resolver[i][1], 
                                  '%d: %s != %s' % (i, str(cc.get_resolver_output()[i]), resolver[i][1]))

    def testBasicLnxHeader(self):
        lnx = Lnx()
        lnx.set_segment_size_bank0(1024)
        lnx.set_segment_size_bank1(0)
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
            #lnx.manufacturer_name  "CGD"
            #lnx.rotation           "none"
          
            #ram.org                0x0200  // locate code to run from 0x0200

            // system variables used by the loader
            byte CART_BANK_0                :$FCB2  // uses CART0/ as strobe
            byte MIKEY_SYSTEM_CONTROL       :$FD87
            byte MIKEY_IO_DIRECTION         :$FD8A  // direction control register
            byte MIKEY_GPIO                 :$FD8B  // general purpose I/O register
            byte MIKEY_SERIAL_CONTROL       :$FD8C
            byte MIKEY_MEMORY_MAP_CONTROL   :$FFF9

            // location to load the secondary loader
            #define SECONDARY_LOADER        $FB00

            // loader function
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

                // call the secondary loader
                secondary_loader()
            }

            #ram.end                        // end ram block

            // The following block is necessary to tell the compiler what to do
            // with the loader.
            #rom.bank               0       // working in bank 0
            #setpad                 0       // pad rom block with 0's
            #rom.org                0,0,256 // rom block is first 256 bytes
            #lynx.loader micro_loader       // encrypt micro_loader function
            #rom.end                        // end rom block

            #rom.org    0,0x0100,256
            #ram.org    SECONDARY_LOADER

            #define SET_CART_SEGMENT_ADDRESS    $FE00

            inline set_cart_segment_address(addr)
            {
                // put the address in the accumulator
                lda #addr

                // call the ROM code function
                jsr SET_CART_SEGMENT_ADDRESS
            }

            inline load_startup_values()
            {
                do
                {
                    // load the destination address
                    ldx CART_BANK_0

                    // load the value
                    lda CART_BANK_0

                    // store the value
                    sta $00,x

                    // test to see if we have the end marker
                    and $00,x

                } while(not zero)
            }

            inline calculate_number_of_segments(size, segs, chunks_per_seg)
            {
                // initialize y
                ldy #0

                // load the number of 256 byte chunks in the exe
                lda size+1

                // divide by the number of chunks in the segment
                ldx chunks_per_seg
                while (not zero) {

                    // divide by 2
                    lsr reg.a

                    // set y to true if any bits are set
                    if (carry) {
                        ldy #1
                    }

                    dex
                }

                // decrement y, the zero flag will be set if y was true
                dey
                if(zero) {
                    // we need to increment the number of segments by one
                    tay
                    iny
                    tya
                }

                // store the number of segments
                sta segs
            }


            // load 256 byte from the cart and store it at the address specified by dest
            // NOTE: dest must be a 16-bit address stored in the zero page
            inline load_chunk(dest)
            {
                ldy #0

                // this loop loads 256 bytes of data
                do
                {
                    lda CART_BANK_0
                    sta (dest),y
                    iny
                } while(not zero)
            }

            inline load_segment(seg, dest, chunks_per_seg)
            {
                // reset x to have the number of 256 byte chunks per segment
                ldx chunks_per_seg

                // set the cart segment address 
                set_cart_segment_address(seg)

                do
                {
                    // load a 256 byte chunk from the cart and store it in RAM
                    load_chunk(dest) 

                    // decrement the chunk per segment counter
                    dex

                } while(not zero)
            }

            function noreturn secondary_loader()
            {
                // zero page variables that get initialized with the startup values
                word exe_size       :$80    // the total number of bytes of the exe
                word exe_location   :$82    // the RAM location of the exe
                byte exe_segment    :$84    // the starting ROM segment number of the exe
                byte chunks_per_seg :$85    // the number of 256 byte chunks per segment

                // when we get here, the cart segment is 0, the counter is 512. now is the
                // time to read in the startup variables.  this will initialize the values
                // for the variables defined above.
                load_startup_values()

                // temporary variables used for loading the exe
                byte num_segs       :$86
                byte cur_seg        :$87
                word cur_write      :$88

                // initialize the number of segments to load
                calculate_number_of_segments(exe_size, num_segs, chunks_per_seg)

                // initialize the current segment we're loading
                lda exe_segment
                sta cur_seg

                // initialize write pointer
                lda exe_location
                sta cur_write

                // load all of the segments
                do 
                {
                    // load a segment
                    load_segment(cur_seg, cur_write, chunks_per_seg)
                  
                    // increment the segment address
                    inc cur_seg

                    // decrement the segment counter
                    dec num_segs

                } while(not zero)
                
                // the exe is loaded so do a blind jmp to run it
                jmp (exe_location)
            }

            #ram.end
            #rom.end

            // this block tells the compiler to emit the variable values into
            // the ROM image
            #rom.org            0,0x200,512
            #ram.org            0x0080      // vars go to 0x0080

            // each startup variable is defined using a byte to specify where it
            // should get loaded into the zero page, and the value that should 
            // get loaded there

            // the size of the game executable
            byte    GAME_EXE_SIZE_LO_ADDR   = $80
            byte    GAME_EXE_SIZE_LO        = lo(sizeof(main) + sizeof(irq))
            byte    GAME_EXE_SIZE_HI_ADDR   = $81
            byte    GAME_EXE_SIZE_HI        = hi(sizeof(main) + sizeof(irq))

            // the location where the game executable should be loaded
            byte    GAME_EXE_LOC_LO_ADDR    = $82
            byte    GAME_EXE_LOC_LO         = lo($0200)
            byte    GAME_EXE_LOC_HI_ADDR    = $83
            byte    GAME_EXE_LOC_HI         = hi($0200)

            // the cart segment address of the game executable
            byte    GAME_EXE_SEGMENT_ADDR   = $84
            byte    GAME_EXE_SEGMENT        = $01

            // the number of chunks per cart segment
            byte    CART_CHUNKS_PER_SEG_ADDR= $85
            byte    CART_CHUNKS_PER_SEG     = $08

            // the end marker
            byte    END_ADDR                = $00
            byte    END                     = $00

            #ram.end
            #rom.end


            #ram.org 0x0200

            function noreturn main()
            {
                // initialize the game

                forever
                {
                    // do the game
                }
            }

            interrupt.irq irq()
            {
            }

            #ram.end                    // end ram block


            // NOTE: the game function won't be located exactly at 0x0200
            // because if there are interrupt funcions, the compiler injects
            // a little stub code for initializing the interrupt vector 
            // addresses with the address of the interrupt functions before
            // executing the game main function.  consequently, #interrupt
            // decls have to precede the #lynx.game decl


            // this block tells the compiler to emit the game code into the ROM
            #rom.org           1,0      // game code starts in 1st seg of ROM
            #lynx.main main             // declare the main function
            #rom.end                    // end rom block

            """

        # PREPROCESSOR PASS
        expected_pp_tokens = [
        (FileBegin, 'FileBegin: DummyFile'),
        (LnxSetting, '#lnx.page_size_bank0 2K'),
        (LnxSetting, '#lnx.page_size_bank1'),
        (LnxSetting, '#lnx.version 1'),
        (LnxSetting, '#lnx.cart_name "CGD Demo Game"'),
        (LnxSetting, '#lnx.manufacturer_name "CGD"'),
        (LnxSetting, '#lnx.rotation none'),
        (RamOrg, 'RamOrg <0x200>'),
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
secondary_loader()
}
"""),
        (RamEnd, 'RamEnd'),
        (RomBank, 'RomBank <0>'),
        (SetPad, 'SetPad <0>'),
        (LynxRomOrg, 'LynxRomOrg <0x0>,<0x0>,<0x100>'),
        (LynxLoader, 'LynxLoader(micro_loader)'),
        (RomEnd, 'RomEnd'),
        (LynxRomOrg, 'LynxRomOrg <0x0>,<0x100>,<0x100>'),
        (RamOrg, 'RamOrg <0xfb00>'),
        (CodeBlock, """inline set_cart_segment_address(addr)
{
lda #addr
jsr $FE00
}
inline load_startup_values()
{
do
{
ldx CART_BANK_0
lda CART_BANK_0
sta $00,x
and $00,x
} while(not zero)
}
inline calculate_number_of_segments(size, segs, chunks_per_seg)
{
ldy #0
lda size+1
ldx chunks_per_seg
while (not zero) {
lsr reg.a
if (carry) {
ldy #1
}
dex
}
dey
if(zero) {
tay
iny
tya
}
sta segs
}
inline load_chunk(dest)
{
ldy #0
do
{
lda CART_BANK_0
sta (dest),y
iny
} while(not zero)
}
inline load_segment(seg, dest, chunks_per_seg)
{
ldx chunks_per_seg
set_cart_segment_address(seg)
do
{
load_chunk(dest)
dex
} while(not zero)
}
function noreturn secondary_loader()
{
word exe_size       :$80    // the total number of bytes of the exe
word exe_location   :$82    // the RAM location of the exe
byte exe_segment    :$84    // the starting ROM segment number of the exe
byte chunks_per_seg :$85    // the number of 256 byte chunks per segment
load_startup_values()
byte num_segs       :$86
byte cur_seg        :$87
word cur_write      :$88
calculate_number_of_segments(exe_size, num_segs, chunks_per_seg)
lda exe_segment
sta cur_seg
lda exe_location
sta cur_write
do
{
load_segment(cur_seg, cur_write, chunks_per_seg)
inc cur_seg
dec num_segs
} while(not zero)
jmp (exe_location)
}
"""),
        (RamEnd, 'RamEnd'),
        (RomEnd, 'RomEnd'),
        (LynxRomOrg, 'LynxRomOrg <0x0>,<0x200>,<0x200>'),
        (RamOrg, 'RamOrg <0x80>'),
        (CodeBlock, """byte    GAME_EXE_SIZE_LO_ADDR   = $80
byte    GAME_EXE_SIZE_LO        = lo(sizeof(main) + sizeof(irq))
byte    GAME_EXE_SIZE_HI_ADDR   = $81
byte    GAME_EXE_SIZE_HI        = hi(sizeof(main) + sizeof(irq))
byte    GAME_EXE_LOC_LO_ADDR    = $82
byte    GAME_EXE_LOC_LO         = lo($0200)
byte    GAME_EXE_LOC_HI_ADDR    = $83
byte    GAME_EXE_LOC_HI         = hi($0200)
byte    GAME_EXE_SEGMENT_ADDR   = $84
byte    GAME_EXE_SEGMENT        = $01
byte    CART_CHUNKS_PER_SEG_ADDR= $85
byte    CART_CHUNKS_PER_SEG     = $08
byte    END_ADDR                = $00
byte    END                     = $00
"""),
        (RamEnd, 'RamEnd'),
        (RomEnd, 'RomEnd'),
        (RamOrg, 'RamOrg <0x200>'),
        (CodeBlock, """function noreturn main()
{
forever
{
}
}
interrupt.irq irq()
{
}
"""),
        (RamEnd, 'RamEnd'),
        (LynxRomOrg, 'LynxRomOrg <0x1>,<0x0>'),
        (LynxMain, 'LynxMain(main)'),
        (RomEnd, 'RomEnd'),
        (FileEnd, 'FileEnd: DummyFile'),
        ]
        pp = Session().preprocessor()

        # open input and run it through the pre-processor
        inf = StringIO(code)
        pp_tokens = pp.parse(inf)
        inf.close()
        
        #fout = open("tokens.txt", "w+")
        #print >> fout, "expected_pp_tokens = ["
        #for p in pp_tokens:
        #    if isinstance(p, CodeBlock):
        #        print >> fout, "(%s, \"\"\"%s\"\"\")," % (str(type(p)).split('.')[-1][:-2], str(p))
        #    else:
        #        print >> fout, "(%s, '%s')," % (str(type(p)).split('.')[-1][:-2], str(p))
        #print >> fout, "]"
        #fout.close()
        
        #print "======================="
        
        #for p in expected_pp_tokens:
        #    print "(%s, %s)," % (p[0], p[1])

        self.assertEquals(len(pp_tokens), len(expected_pp_tokens))
        for i in range(0, len(expected_pp_tokens)):
            self.assertTrue(isinstance(pp_tokens[i], expected_pp_tokens[i][0]),
                            'token %d: %s != %s' % (i, pp_tokens[i], expected_pp_tokens[i][0]))
            self.assertEqual(str(pp_tokens[i]), expected_pp_tokens[i][1], 
                             'token %d: %s != %s' % (i, str(pp_tokens[i]), 
                             expected_pp_tokens[i][1]))

        print ">>>>>>>>>>>>>>>>>> PREPROCESSOR OK <<<<<<<<<<<<<<<<<<<<<<<<<<"

        # COMPILER PASS
        scanner = [
            (FileBegin, "FileBegin: DummyFile"),
            (LnxSetting, "#lnx.page_size_bank0 2K"),
            (LnxSetting, "#lnx.page_size_bank1"),
            (LnxSetting, "#lnx.version 1"),
            (LnxSetting, '#lnx.cart_name "CGD Demo Game"'),
            (LnxSetting, '#lnx.manufacturer_name "CGD"'),
            (LnxSetting, "#lnx.rotation none"),
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
            (FunctionCall, "secondary_loader()"),
            (ScopeEnd, "}"),
            (RamEnd, "RamEnd"),
            (RomBank, "RomBank <0>"),
            (SetPad, "SetPad <0>"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x0>,<0x100>"),
            (LynxLoader, "LynxLoader(micro_loader)"),
            (RomEnd, "RomEnd"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x100>,<0x100>"),
            (RamOrg, "RamOrg <0xfb00>"),
            (FunctionDecl, "inline set_cart_segment_address( addr )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #addr"),
            (InstructionLine, "jsr $FE00"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline load_startup_values()"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx $FCB2"),
            (InstructionLine, "lda $FCB2"),
            (InstructionLine, "sta $00,x"),
            (InstructionLine, "and $00,x"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline calculate_number_of_segments( size, segs, chunks_per_seg )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldy #0"),
            (InstructionLine, "lda +([size], 1)"),
            (InstructionLine, "ldx chunks_per_seg"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lsr"),
            (ConditionalDecl, "if(['carry'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldy #1"),
            (ScopeEnd, "}"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (InstructionLine, "dey"),
            (ConditionalDecl, "if(['zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "tay"),
            (InstructionLine, "iny"),
            (InstructionLine, "tya"),
            (ScopeEnd, "}"),
            (InstructionLine, "sta segs"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline load_chunk( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldy #0"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda $FCB2"),
            (InstructionLine, "sta (dest), y"),
            (InstructionLine, "iny"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline load_segment( seg, dest, chunks_per_seg )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx chunks_per_seg"),
            (FunctionCall, "set_cart_segment_address( seg )"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (FunctionCall, "load_chunk( dest )"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (ScopeEnd, "}"),
            (FunctionDecl, "function noreturn secondary_loader()"),
            (ScopeBegin, "{"),
            (Variable, "word exe_size :$80"),
            (Variable, "word exe_location :$82"),
            (Variable, "byte exe_segment :$84"),
            (Variable, "byte chunks_per_seg :$85"),
            (FunctionCall, "load_startup_values()"),
            (Variable, "byte num_segs :$86"),
            (Variable, "byte cur_seg :$87"),
            (Variable, "word cur_write :$88"),
            (FunctionCall, "calculate_number_of_segments( exe_size, num_segs, chunks_per_seg )"),
            (InstructionLine, "lda $84"),
            (InstructionLine, "sta $87"),
            (InstructionLine, "lda $82"),
            (InstructionLine, "sta $88"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (FunctionCall, "load_segment( cur_seg, cur_write, chunks_per_seg )"),
            (InstructionLine, "inc $87"),
            (InstructionLine, "dec $86"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (InstructionLine, "jmp $82"),
            (ScopeEnd, "}"),
            (RamEnd, "RamEnd"),
            (RomEnd, "RomEnd"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x200>,<0x200>"),
            (RamOrg, "RamOrg <0x80>"),
            (Variable, "byte GAME_EXE_SIZE_LO_ADDR"),
            (VariableInitializer, " = $80"),
            (Variable, "byte GAME_EXE_SIZE_LO"),
            (VariableInitializer, " = lo(+(sizeof(main), sizeof(irq)))"),
            (Variable, "byte GAME_EXE_SIZE_HI_ADDR"),
            (VariableInitializer, " = $81"),
            (Variable, "byte GAME_EXE_SIZE_HI"),
            (VariableInitializer, " = hi(+(sizeof(main), sizeof(irq)))"),
            (Variable, "byte GAME_EXE_LOC_LO_ADDR"),
            (VariableInitializer, " = $82"),
            (Variable, "byte GAME_EXE_LOC_LO"),
            (VariableInitializer, " = lo($0200)"),
            (Variable, "byte GAME_EXE_LOC_HI_ADDR"),
            (VariableInitializer, " = $83"),
            (Variable, "byte GAME_EXE_LOC_HI"),
            (VariableInitializer, " = hi($0200)"),
            (Variable, "byte GAME_EXE_SEGMENT_ADDR"),
            (VariableInitializer, " = $84"),
            (Variable, "byte GAME_EXE_SEGMENT"),
            (VariableInitializer, " = $01"),
            (Variable, "byte CART_CHUNKS_PER_SEG_ADDR"),
            (VariableInitializer, " = $85"),
            (Variable, "byte CART_CHUNKS_PER_SEG"),
            (VariableInitializer, " = $08"),
            (Variable, "byte END_ADDR"),
            (VariableInitializer, " = $00"),
            (Variable, "byte END"),
            (VariableInitializer, " = $00"),
            (RamEnd, "RamEnd"),
            (RomEnd, "RomEnd"),
            (RamOrg, "RamOrg <0x200>"),
            (FunctionDecl, "function noreturn main()"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "forever"),
            (ScopeBegin, "{"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "interrupt.irq irq()"),
            (ScopeBegin, "{"),
            (ScopeEnd, "}"),
            (RamEnd, "RamEnd"),
            (LynxRomOrg, "LynxRomOrg <0x1>,<0x0>"),
            (LynxMain, "LynxMain(main)"),
            (RomEnd, "RomEnd"),
            (FileEnd, "FileEnd: DummyFile"),
        ]
        parser = [
            (LnxSetting, "#lnx.page_size_bank0 2K"),
            (LnxSetting, "#lnx.page_size_bank1"),
            (LnxSetting, "#lnx.version 1"),
            (LnxSetting, '#lnx.cart_name "CGD Demo Game"'),
            (LnxSetting, '#lnx.manufacturer_name "CGD"'),
            (LnxSetting, "#lnx.rotation none"),
            (RamOrg, "RamOrg <0x200>"),
            (Variable, "byte CART_BANK_0 :$FCB2"),
            (Variable, "byte MIKEY_SYSTEM_CONTROL :$FD87"),
            (Variable, "byte MIKEY_IO_DIRECTION :$FD8A"),
            (Variable, "byte MIKEY_GPIO :$FD8B"),
            (Variable, "byte MIKEY_SERIAL_CONTROL :$FD8C"),
            (Variable, "byte MIKEY_MEMORY_MAP_CONTROL :$FFF9"),
            (Function, "function noreturn micro_loader()"),
            (RamEnd, "RamEnd"),
            (RomBank, "RomBank <0>"),
            (SetPad, "SetPad <0>"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x0>,<0x100>"),
            (LynxLoader, "LynxLoader(micro_loader)"),
            (RomEnd, "RomEnd"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x100>,<0x100>"),
            (RamOrg, "RamOrg <0xfb00>"),
            (Function, "inline set_cart_segment_address( addr )"),
            (Function, "inline load_startup_values()"),
            (Function, "inline calculate_number_of_segments( size, segs, chunks_per_seg )"),
            (Function, "inline load_chunk( dest )"),
            (Function, "inline load_segment( seg, dest, chunks_per_seg )"),
            (Function, "function noreturn secondary_loader()"),
            (RamEnd, "RamEnd"),
            (RomEnd, "RomEnd"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x200>,<0x200>"),
            (RamOrg, "RamOrg <0x80>"),
            (Variable, "byte GAME_EXE_SIZE_LO_ADDR"),
            (Variable, "byte GAME_EXE_SIZE_LO"),
            (Variable, "byte GAME_EXE_SIZE_HI_ADDR"),
            (Variable, "byte GAME_EXE_SIZE_HI"),
            (Variable, "byte GAME_EXE_LOC_LO_ADDR"),
            (Variable, "byte GAME_EXE_LOC_LO"),
            (Variable, "byte GAME_EXE_LOC_HI_ADDR"),
            (Variable, "byte GAME_EXE_LOC_HI"),
            (Variable, "byte GAME_EXE_SEGMENT_ADDR"),
            (Variable, "byte GAME_EXE_SEGMENT"),
            (Variable, "byte CART_CHUNKS_PER_SEG_ADDR"),
            (Variable, "byte CART_CHUNKS_PER_SEG"),
            (Variable, "byte END_ADDR"),
            (Variable, "byte END"),
            (RamEnd, "RamEnd"),
            (RomEnd, "RomEnd"),
            (RamOrg, "RamOrg <0x200>"),
            (Function, "function noreturn main()"),
            (Function, "interrupt.irq irq()"),
            (RamEnd, "RamEnd"),
            (LynxRomOrg, "LynxRomOrg <0x1>,<0x0>"),
            (LynxMain, "LynxMain(main)"),
            (RomEnd, "RomEnd"),
        ]
        resolver = [
            (LnxSetting, "#lnx.page_size_bank0 2K"),
            (LnxSetting, "#lnx.page_size_bank1"),
            (LnxSetting, "#lnx.version 1"),
            (LnxSetting, '#lnx.cart_name "CGD Demo Game"'),
            (LnxSetting, '#lnx.manufacturer_name "CGD"'),
            (LnxSetting, "#lnx.rotation none"),
            (RamOrg, "RamOrg <0x200>"),
            (Variable, "byte CART_BANK_0 :$FCB2"),
            (Variable, "byte MIKEY_SYSTEM_CONTROL :$FD87"),
            (Variable, "byte MIKEY_IO_DIRECTION :$FD8A"),
            (Variable, "byte MIKEY_GPIO :$FD8B"),
            (Variable, "byte MIKEY_SERIAL_CONTROL :$FD8C"),
            (Variable, "byte MIKEY_MEMORY_MAP_CONTROL :$FFF9"),
            (Label, "MICRO_LOADER"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta $FFF9"),
            (InstructionLine, "lda #%00010011"),
            (InstructionLine, "sta $FD8A"),
            (InstructionLine, "lda #%00000100"),
            (InstructionLine, "sta $FD8C"),
            (InstructionLine, "lda #%00001000"),
            (InstructionLine, "sta $FD8B"),
            (InstructionLine, "ldx #0"),
            (Label, "HLA0"),
            (InstructionLine, "lda $FCB2"),
            (InstructionLine, "sta $FB00,x"),
            (InstructionLine, "inx"),
            (InstructionLine, "bne HLA0"),
            (InstructionLine, "jsr SECONDARY_LOADER"),
            (RamEnd, "RamEnd"),
            (RomBank, "RomBank <0>"),
            (SetPad, "SetPad <0>"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x0>,<0x100>"),
            (LynxLoader, "LynxLoader(micro_loader)"),
            (RomEnd, "RomEnd"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x100>,<0x100>"),
            (RamOrg, "RamOrg <0xfb00>"),
            (Label, "SET_CART_SEGMENT"),
            (InstructionLine, "lda #addr"),
            (InstructionLine, "jsr $FE00"),
            (Label, "LOAD_STARTUP_VAL"),
            (Label, "HLA1"),
            (InstructionLine, "ldx $FCB2"),
            (InstructionLine, "lda $FCB2"),
            (InstructionLine, "sta $00,x"),
            (InstructionLine, "and $00,x"),
            (InstructionLine, "bne HLA1"),
            (Label, "CALCULATE_NUMBER"),
            (InstructionLine, "ldy #0"),
            (InstructionLine, "lda +([size], 1)"),
            (InstructionLine, "ldx chunks_per_seg"),
            (Label, "HLA2"),
            (InstructionLine, "bne HLA3"),
            (InstructionLine, "lsr"),
            (InstructionLine, "bcs HLA9"),
            (InstructionLine, "ldy #1"),
            (Label, "HLA9"),
            (InstructionLine, "dex"),
            (Label, "HLA3"),
            (InstructionLine, "dey"),
            (InstructionLine, "beq HLA4"),
            (InstructionLine, "tay"),
            (InstructionLine, "iny"),
            (InstructionLine, "tya"),
            (Label, "HLA4"),
            (InstructionLine, "sta segs"),
            (Label, "LOAD_CHUNK"),
            (InstructionLine, "ldy #0"),
            (Label, "HLA5"),
            (InstructionLine, "lda $FCB2"),
            (InstructionLine, "sta (dest), y"),
            (InstructionLine, "iny"),
            (InstructionLine, "bne HLA5"),
            (Label, "LOAD_SEGMENT"),
            (InstructionLine, "ldx chunks_per_seg"),
            (Label, "HLA6"),
            (InstructionLine, "dex"),
            (InstructionLine, "bne HLA6"),
            (Label, "SECONDARY_LOADER"),
            (Variable, "word exe_size :$80"),
            (Variable, "word exe_location :$82"),
            (Variable, "byte exe_segment :$84"),
            (Variable, "byte chunks_per_seg :$85"),
            (Variable, "byte num_segs :$86"),
            (Variable, "byte cur_seg :$87"),
            (Variable, "word cur_write :$88"),
            (InstructionLine, "lda $84"),
            (InstructionLine, "sta $87"),
            (InstructionLine, "lda $82"),
            (InstructionLine, "sta $88"),
            (Label, "HLA7"),
            (InstructionLine, "inc $87"),
            (InstructionLine, "dec $86"),
            (InstructionLine, "bne HLA7"),
            (InstructionLine, "jmp $82"),
            (RamEnd, "RamEnd"),
            (RomEnd, "RomEnd"),
            (LynxRomOrg, "LynxRomOrg <0x0>,<0x200>,<0x200>"),
            (RamOrg, "RamOrg <0x80>"),
            (Variable, "byte GAME_EXE_SIZE_LO_ADDR"),
            (Variable, "byte GAME_EXE_SIZE_LO"),
            (Variable, "byte GAME_EXE_SIZE_HI_ADDR"),
            (Variable, "byte GAME_EXE_SIZE_HI"),
            (Variable, "byte GAME_EXE_LOC_LO_ADDR"),
            (Variable, "byte GAME_EXE_LOC_LO"),
            (Variable, "byte GAME_EXE_LOC_HI_ADDR"),
            (Variable, "byte GAME_EXE_LOC_HI"),
            (Variable, "byte GAME_EXE_SEGMENT_ADDR"),
            (Variable, "byte GAME_EXE_SEGMENT"),
            (Variable, "byte CART_CHUNKS_PER_SEG_ADDR"),
            (Variable, "byte CART_CHUNKS_PER_SEG"),
            (Variable, "byte END_ADDR"),
            (Variable, "byte END"),
            (RamEnd, "RamEnd"),
            (RomEnd, "RomEnd"),
            (RamOrg, "RamOrg <0x200>"),
            (Label, "MAIN"),
            (Label, "HLA8"),
            (InstructionLine, "jmp HLA8"),
            (Label, "IRQ"),
            (InstructionLine, "rti"),
            (RamEnd, "RamEnd"),
            (LynxRomOrg, "LynxRomOrg <0x1>,<0x0>"),
            (LynxMain, "LynxMain(main)"),
            (RomEnd, "RomEnd"),
        ]

        cc = Session().compiler()
        cc.compile(pp_tokens, True)

        #fout = open("gen.txt", "w+")
        #print >> fout, cc.output_debug_def()
        #fout.close()

        self._checkScannerParserResolver(cc, scanner, parser, resolver)

        # GENERATOR PASS
        expected_listing = \
"""
BA SG CNT ADDR               LABELS    00 00 00    CODE            FN
00 00 000 0000                                     .org $0200      
00 00 000 0200        MICRO_LOADER:    A9 00       lda #0          micro_loader
00 00 002 0202                         8D F9 FF    sta $FFF9       micro_loader
00 00 005 0205                         A9 13       lda #%00010011  micro_loader
00 00 007 0207                         8D 8A FD    sta $FD8A       micro_loader
00 00 00A 020A                         A9 04       lda #%00000100  micro_loader
00 00 00C 020C                         8D 8C FD    sta $FD8C       micro_loader
00 00 00F 020F                         A9 08       lda #%00001000  micro_loader
00 00 011 0211                         8D 8B FD    sta $FD8B       micro_loader
00 00 014 0214                         A2 00       ldx #0          micro_loader
00 00 016 0216                HLA0:    AD B2 FC    lda $FCB2       micro_loader
00 00 019 0219                         9D 00 FB    sta $FB00,x     micro_loader
00 00 01C 021C                         E8          inx             micro_loader
00 00 01D 021D                         D0 F7       bne *-9         micro_loader
00 00 01F 021F                         4C 00 FB    jmp $FB00       micro_loader
00 00 022 0222                                     .end            
"""

        """
        gen = Session().generator()

        # build the rom
        lnx = gen.build_rom(cc.get_output()[0:97])

        # check the romfile settings
        romfile = gen.romfile()
        self.assertTrue(isinstance(romfile, Lnx))
        self.assertEquals(romfile.get_segment_size_bank0(), 2048)
        self.assertEquals(romfile.get_segment_size_bank1(), 0)
        self.assertEquals(romfile.get_version(), 1)
        self.assertEquals(romfile.get_cart_name(), "CGD Demo Game")
        self.assertEquals(romfile.get_manufacturer_name(), "CGD")
        self.assertEquals(romfile.get_rotation(), Lnx.ROTATE_NONE)
        self.assertEquals(romfile.get_loader(), "micro_loader")

        # bank checks
        self.assertEquals(romfile.get_current_bank_number(), 0)
        self.assertTrue(isinstance(romfile.get_current_bank(), LnxRomFileBank))

        # padding checks
        self.assertEquals(romfile.get_padding(), 0)

        # variable checks
        st = SymbolTable()
        vars = [ ('CART_BANK_0', 0xFCB2),
                 ('MIKEY_SYSTEM_CONTROL', 0xFD87),
                 ('MIKEY_IO_DIRECTION', 0xFD8A),
                 ('MIKEY_GPIO', 0xFD8B),
                 ('MIKEY_SERIAL_CONTROL', 0xFD8C),
                 ('MIKEY_MEMORY_MAP_CONTROL', 0xFFF9) ]
        for n,a in vars:
            v = st.lookup_symbol(n, '__global__.DummyFile')
            self.assertTrue(isinstance(v, Variable))
            self.assertEquals(v.get_address(), a)

        print lnx.get_debug_listing()
        self.assertEquals(expected_listing, lnx.get_debug_listing())

        print lnx.get_debug_str()

        # save the rom
        #outf = StringIO()
        outf = open("out.lnx", "w+")
        lnx.save(outf)
        outf.close()

        # check the rom
        #self.assertEquals(expected_rom, outf.getvalue())
        """
