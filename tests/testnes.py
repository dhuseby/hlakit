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
from hlakit.common.enum import Enum
from hlakit.common.name import Name
from hlakit.common.session import Session
from hlakit.common.symboltable import SymbolTable
from hlakit.common.type_ import Type, TypeRegistry
from hlakit.common.codeblock import CodeBlock
from hlakit.common.codeline import CodeLine
from hlakit.common.numericvalue import NumericValue
from hlakit.common.function import Function
from hlakit.common.functiontype import FunctionType
from hlakit.common.functionparameter import FunctionParameter
from hlakit.common.functiondecl import FunctionDecl
from hlakit.common.functioncall import FunctionCall
from hlakit.common.functionreturn import FunctionReturn
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd
from hlakit.common.immediate import Immediate
from hlakit.common.typedef import Typedef
from hlakit.common.type_ import Type
from hlakit.common.variable import Variable
from hlakit.common.variableinitializer import VariableInitializer
from hlakit.common.label import Label
from hlakit.common.conditional import Conditional
from hlakit.cpu.mos6502.interrupt import InterruptStart, InterruptNMI, InterruptIRQ
from hlakit.cpu.mos6502.register import Register
from hlakit.cpu.mos6502.opcode import Opcode
from hlakit.cpu.mos6502.operand import Operand
from hlakit.cpu.mos6502.instructionline import InstructionLine
from hlakit.cpu.mos6502.conditionaldecl import ConditionalDecl
from hlakit.platform.nes.preprocessor import Preprocessor as NESPreprocessor
from hlakit.platform.nes.compiler import Compiler as NESCompiler
from hlakit.platform.nes.generator import Generator as NESGenerator
from hlakit.platform.nes.chr import ChrBanksize, ChrBank, ChrLink, ChrEnd
from hlakit.platform.nes.ines import iNESMapper, iNESMirroring, iNESFourscreen, iNESBattery, iNESTrainer, iNESPrgRepeat, iNESChrRepeat, iNESOff

class NESTester(unittest.TestCase):
    def setUp(self):
        Session().parse_args(['--platform=NES'])

    def tearDown(self):
        Session().preprocessor().reset_state()
        Session().compiler().reset_state()
        Session().generator().reset_state()
        TypeRegistry().reset_state()
        SymbolTable().reset_state()
        Label.reset_state()

    def testNESPreprocessor(self):
        self.assertTrue(isinstance(Session().preprocessor(), NESPreprocessor))

    def testNESCompiler(self):
        self.assertTrue(isinstance(Session().compiler(), NESCompiler))

    def testNESGenerator(self):
        self.assertTrue(isinstance(Session().generator(), NESGenerator))


class NESPreprocessorTester(NESTester):
    """
    This class aggregates all of the tests for the NES Preprocessor
    """

    pp_chrbanksize = '#chr.banksize %s\n'
    pp_chrend = '#chr.end'

    def testChrBanksize(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_chrbanksize % '1K'))
        self.assertTrue(isinstance(tokens[1], ChrBanksize))
        self.assertEquals(int(tokens[1].get_size()), 1024)

    def testChrBanksizeLabel(self):
        pp = Session().preprocessor() 

        pp.set_symbol('FOO', 1024)
        tokens = pp.parse(StringIO(self.pp_chrbanksize % 'FOO'))
        self.assertTrue(isinstance(tokens[1], ChrBanksize))
        self.assertEquals(int(tokens[1].get_size()), 1024)

    def testBadChrBanksize(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_chrbanksize % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    #TODO: tests for #chr.bank and #chr.link

    def testChrEnd(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_chrend))
        self.assertTrue(isinstance(tokens[1], ChrEnd))

    pp_inesmapper = '#ines.mapper %s\n'
    pp_inesmirroring = '#ines.mirroring %s\n'
    pp_inesfourscreen = '#ines.fourscreen %s\n'
    pp_inesbattery = '#ines.battery %s\n'
    pp_inestrainer = '#ines.trainer %s\n'
    pp_inesprgrepeat = '#ines.prgrepeat %s\n'
    pp_ineschrrepeat = '#ines.chrrepeat %s\n'
    pp_inesoff = '#ines.off\n'

    def testiNESMapperName(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inesmapper % '"NROM"'))
        self.assertTrue(isinstance(tokens[1], iNESMapper))
        self.assertEquals(tokens[1].get_mapper(), 'NROM')

    def testiNESMapperNumber(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inesmapper % '0'))
        self.assertTrue(isinstance(tokens[1], iNESMapper))
        self.assertEquals(int(tokens[1].get_mapper()), 0)

    def testBadiNESMapper(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_inesmapper % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testiNESMirroringVertical(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inesmirroring % '"vertical"'))
        self.assertTrue(isinstance(tokens[1], iNESMirroring))
        self.assertEquals(tokens[1].get_mirroring(), 'vertical')

    def testiNESMirroringHorizontal(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inesmirroring % '"horizontal"'))
        self.assertTrue(isinstance(tokens[1], iNESMirroring))
        self.assertEquals(tokens[1].get_mirroring(), 'horizontal')

    def testBadiNESMirroring(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_inesmirroring % '"blah"'))
            self.assertTrue(False)
        except ParseFatalException:
            pass

    def testiNESFourscreenYes(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inesfourscreen % '"yes"'))
        self.assertTrue(isinstance(tokens[1], iNESFourscreen))
        self.assertEquals(tokens[1].get_fourscreen(), 'yes')

    def testiNESFourscreenNo(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inesfourscreen % '"no"'))
        self.assertTrue(isinstance(tokens[1], iNESFourscreen))
        self.assertEquals(tokens[1].get_fourscreen(), 'no')

    def testBadiNESFourscreen(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_inesfourscreen % '"blah"'))
            self.assertTrue(False)
        except ParseFatalException:
            pass

    def testiNESBatterYes(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inesbattery % '"yes"'))
        self.assertTrue(isinstance(tokens[1], iNESBattery))
        self.assertEquals(tokens[1].get_battery(), 'yes')

    def testiNESBatteryNo(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inesbattery % '"no"'))
        self.assertTrue(isinstance(tokens[1], iNESBattery))
        self.assertEquals(tokens[1].get_battery(), 'no')

    def testBadiNESBattery(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_inesbattery % '"blah"'))
            self.assertTrue(False)
        except ParseFatalException:
            pass

    def testiNESTrainerYes(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inestrainer % '"yes"'))
        self.assertTrue(isinstance(tokens[1], iNESTrainer))
        self.assertEquals(tokens[1].get_trainer(), 'yes')

    def testiNESTrainerNo(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inestrainer % '"no"'))
        self.assertTrue(isinstance(tokens[1], iNESTrainer))
        self.assertEquals(tokens[1].get_trainer(), 'no')

    def testBadiNESTrainer(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_inestrainer % '"blah"'))
            self.assertTrue(False)
        except ParseFatalException:
            pass

    def testiNESPrgRepeat(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inesprgrepeat % '4'))
        self.assertTrue(isinstance(tokens[1], iNESPrgRepeat))
        self.assertEquals(int(tokens[1].get_repeat()), 4)

    def testBadiNESPrgRepeat(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_inesprgrepeat % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testiNESChrRepeat(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_ineschrrepeat % '4'))
        self.assertTrue(isinstance(tokens[1], iNESChrRepeat))
        self.assertEquals(int(tokens[1].get_repeat()), 4)

    def testBadiNESChrRepeat(self):
        pp = Session().preprocessor()

        try:
            tokens = pp.parse(StringIO(self.pp_ineschrrepeat % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testiNESOff(self):
        pp = Session().preprocessor() 

        tokens = pp.parse(StringIO(self.pp_inesoff))
        self.assertTrue(isinstance(tokens[1], iNESOff))


class NESCompilerTester(NESTester):
    """
    This class aggregates all of the tests for the NES Compiler
    """

    def _checkScannerParserResolver(self, cc, scanner, parser, resolver):
        # check the scanner output
        self.assertEquals(len(cc.get_scanner_output()), len(scanner))
        for i in range(0,len(scanner)):
            self.assertTrue(isinstance(cc.get_scanner_output()[i], scanner[i][0]), '%d' % i)
            self.assertEquals(str(cc.get_scanner_output()[i]), scanner[i][1], '%d: (%s) %s != (%s) %s' % (i, type(cc.get_scanner_output()[i]), str(cc.get_scanner_output()[i]), type(scanner[i][1]), scanner[i][1]))

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

    def testExampleGame(self):
        code = """
            inline enable_interrupts()
            {
                cli // clear interrupt disable
            }

            inline disable_interrupts()
            {
                sei // set interrupt disable
            }

            inline enable_decimal_mode()
            {
                sei // set decimal mode
            }

            inline disable_decimal_mode()
            {
                cld // clear decimal mode
            }

            inline set_carry_flag()
            {
                sec // set the carry flag
            }

            inline clear_carry_flag()
            {
                clc // clear the carry flag
            }

            inline reset_stack()
            {
                ldx #0xFF // reset the stack pointer
                    txs
            }

            inline nes_reset()
            {
                jmp ($FFFC)
            }

            inline system_initialize()
            {
                disable_decimal_mode()
                    disable_interrupts()
                    reset_stack()  // this is why this MUST be inline!
                    vblank_wait()
                    lda  #0
                    sta  PPU.CNT0
                    sta  PPU.CNT1
                    sta  PPU.BG_SCROLL
                    sta  PPU.BG_SCROLL
                    sta  PCM_CNT
                    sta  PCM_VOLUMECNT
                    sta  SND_CNT
                    lda  #0xC0
                    sta  joystick.cnt1
                    enable_interrupts()
            }

            enum PPU {
                CNT0        = $2000,
                CNT1        = $2001,
                STATUS      = $2002,
                ADDRESS     = $2006,
                IO          = $2007,
                SPR_ADDRESS = $2003,
                SPR_IO      = $2004,
                SPR_DMA     = $4014,
                BG_SCROLL   = $2005,
            }

            typedef struct OAM_ENTRY_ {
                byte y, tile, attributes, x
            } OAM_ENTRY

            typedef struct PALENT_ {
                byte colBackground, col1, col2, col3
            } PALENT

            typedef struct PALETTE_ {
                PALENT pal0, pal1, pal2, pal3
            } PALETTE

            inline ppu_ctl0_assign(newctl)
            {
                lda newctl
                    sta _ppu_ctl0
                    sta PPU.CNT0
            }

            inline ppu_ctl0_set(mask)
            {
                lda _ppu_ctl0
                    ora #(mask)
                    sta _ppu_ctl0
                    sta PPU.CNT0
            }

            inline ppu_ctl0_clear(mask)
            {
                lda _ppu_ctl0
                    and #~(mask)
                    sta _ppu_ctl0
                    sta PPU.CNT0
            }

            inline ppu_ctl0_adjust( clearmask, setmask )
            {
                lda _ppu_ctl0
                    and #~(clearmask)
                    ora #(setmask)
                    sta _ppu_ctl0
                    sta PPU.CNT0
            }

            inline ppu_ctl0_xor(mask)
            {
                lda _ppu_ctl0
                    eor #(mask)
                    sta _ppu_ctl0
                    sta PPU.CNT0
            }

            inline ppu_ctl0_test( mask )
            {
                lda mask
                    bit _ppu_ctl0
            }

            inline ppu_enable_nmi(mask)
            {
                ppu_ctl0_set(%10000000)
            }

            inline ppu_disable_nmi()
            {
                ppu_ctl0_clear(%10000000)
            }

            inline ppu_turn_off()
            {
                ppu_ctl0_assign(#0) // disable nmi
                    vblank_wait()
                    ppu_ctl1_assign(#0) // turn off the screen completely
                    sta  PPU.BG_SCROLL
                    sta  PPU.BG_SCROLL
            }

            inline ppu_turn_on_draw()
            {
                ppu_enable_nmi()
                    ppu_ctl1_set(%00010000|%00001000)
            }

            inline ppu_turn_off_draw()
            {
                ppu_disable_nmi()
                    ppu_ctl1_clear(%00010000|%00001000)
            }

            inline ppu_set_nametable(nametable)
            {
                ppu_ctl0_adjust(%00000011, nametable)
            }

            inline ppu_xor_nametable()
            {
                ppu_ctl0_xor(%00000011)
            }

            inline ppu_ctl1_assign(newctl)
            {
                lda newctl
                    sta _ppu_ctl1
                    sta PPU.CNT1
            }

            inline ppu_ctl1_set(mask)
            {
                lda _ppu_ctl1
                    ora #(mask)
                    sta _ppu_ctl1
                    sta PPU.CNT1
            }

            inline ppu_ctl1_clear(mask)
            {
                lda _ppu_ctl1
                    and #~(mask)
                    sta _ppu_ctl1
                    sta PPU.CNT1
            }

            inline ppu_ctl1_adjust( clearmask, setmask )
            {
                lda _ppu_ctl1
                    and #~(clearmask)
                    ora #(setmask)
                    sta _ppu_ctl1
                    sta PPU.CNT1
            }

            inline ppu_ctl1_test( mask )
            {
                lda mask
                    bit _ppu_ctl1
            }

            inline ppu_set_palette_intensity(newbits)
            {
                ppu_ctl1_adjust(%11100000, newbits)
            }

            inline vblank_wait()
            {
                do
                    lda PPU.STATUS
                    while (is plus)
            }

            inline vblank_wait_full()
            {
                vblank_wait()
                    unvblank_wait()
            }

            inline vblank_wait_for(amount)
            {
                ldx amount
                    do 
                    {
                        vblank_wait_full()
                            dex
                    } 
                while (nonzero)
            }

            inline unvblank_wait()
            {
                do
                    lda PPU.STATUS
                    while (is minus)
            }

            inline test_scanline()
            {
                lda PPU.STATUS
                    and #%00100000
            }

            inline ppu_clean_latch()
            {
                lda PPU.STATUS
            }

            inline vram_clear_address()
            {
                lda #0
                    sta PPU.ADDRESS
                    sta PPU.ADDRESS
            }

            inline vram_set_address(newaddress)
            {
                ppu_clean_latch()
                    lda newaddress+1
                    sta PPU.ADDRESS
                    lda newaddress+0
                    sta PPU.ADDRESS
            }

            inline vram_set_address_i(newaddress)
            {
                ppu_clean_latch()
                    lda #hi(newaddress)
                    sta PPU.ADDRESS
                    lda #lo(newaddress)
                    sta PPU.ADDRESS
            }

            inline vram_set_scroll( x, y )
            {
                assign(PPU.BG_SCROLL, x)
                    assign(PPU.BG_SCROLL, y)
            }

            inline vram_write(value)
            {
                assign(PPU.IO, value)
            }

            inline vram_write_ind(value)
            {
                assign_ind(PPU.IO, value)
            }

            inline vram_write_x(value)
            {
                x_assign(PPU.IO, value)
            }

            inline vram_write_ind_y(value)
            {
                ind_y_assign(PPU.IO, value)
            }

            inline vram_write_a()
            {
                sta PPU.IO
            }

            inline vram_write_regx()
            {
                stx PPU.IO
            }

            inline vram_write_16(value)
            {
                assign(PPU.IO, value+0)
                    assign(PPU.IO, value+1)
            }

            inline vram_write_16_i(value)
            {
                assign(PPU.IO, #hi(value))
                    assign(PPU.IO, #lo(value))
            }

            inline vram_read(dest)
            {
                assign(dest,PPU.IO)
            }

            inline vram_ind_read(dest)
            {
                assign_ind(dest,PPU.IO)
            }

            inline vram_ind_y_read(dest)
            {
                assign_ind_y(dest,PPU.IO)
            }

            inline vram_read_a()
            {
                lda PPU.IO
            }

            inline vram_read_16(dest)
            {
                assign(dest+0,PPU.IO)
                    assign(dest+1,PPU.IO)
            }

            inline vram_set_sprite_address(newaddress)
            {
                assign(PPU.SPR_ADDRESS,newaddress+1)
                    assign(PPU.SPR_ADDRESS,newaddress+0)
            }

            inline vram_set_sprite_address_i(newaddress)
            {
                assign(PPU.SPR_ADDRESS, #hi(newaddress))
                    assign(PPU.SPR_ADDRESS, #lo(newaddress))
            }

            inline vram_set_sprite_data( x, y, tile, attributes )
            {
                assign(PPU.SPR_IO, y)
                    assign(PPU.SPR_IO, tile)
                    assign(PPU.SPR_IO, attributes)
                    assign(PPU.SPR_IO, x)
            }

            inline vram_sprite_dma_copy(oamptr)
            {
                assign(PPU.SPR_DMA, #hi(oamptr))
            }

            byte JOYSTICK_CNT0    :$4016
            byte JOYSTICK_CNT1    :$4017
            enum JOYSTICK {
                CNT0 = $4016,
                CNT1 = $4017,
            }

            inline reset_joystick()
            {
                assign(JOYSTICK.CNT0, #1)
                    assign(JOYSTICK.CNT0, #0)
            }

            inline read_joystick0()
            {
                lda JOYSTICK.CNT0
                    and #1
            }

            inline read_joystick1()
            {
                lda JOYSTICK.CNT1
                    and #1
            }

            inline test_joystick1(buttonmask)
            {
                lda _joypad
                    and buttonmask
            }

            inline test_joystick1_prev(buttonmask)
            {
                lda _joypad_prev
                    and buttonmask
            }

            inline test_button_release(buttonmask)
            {
                test_joystick1(buttonmask)
                    if (zero) 
                    {
                        test_joystick1_prev(buttonmask)
                    }
                eor #0xFF
            }

            inline test_button_press(buttonmask)
            {
                test_joystick1(buttonmask)    // return(
                    if (nonzero)       //   if(joypad&buttonmask)
                    {
                        test_joystick1_prev(buttonmask)  //   !(joypad&buttonmask)
                            eor #0xFF       //
                    }          // )
            }

            byte SQUAREWAVEA_CNT0       :$4000
            byte SQUAREWAVEA_CNT1       :$4001
            byte SQUAREWAVEA_FREQ0      :$4002
            byte SQUAREWAVEA_FREQ1      :$4003
            enum SQUAREWAVEA {
                CNT0                    = $4000,
                CNT1                    = $4001,
                FREQ0                   = $4002,
                FREQ1                   = $4003
            }
            byte SQUAREWAVEB_CNT0       :$4004
            byte SQUAREWAVEB_CNT1       :$4005
            byte SQUAREWAVEB_FREQ0      :$4006
            byte SQUAREWAVEB_FREQ1      :$4007
            enum SQUAREWAVEB {
                CNT0                    = $4004,
                CNT1                    = $4005,
                FREQ0                   = $4006,
                FREQ1                   = $4007
            }
            byte TRIANGLEWAVE_CNT0      :$4008
            byte TRIANGLEWAVE_CNT1      :$4009
            byte TRIANGLEWAVE_FREQ0     :$400A
            byte TRIANGLEWAVE_FREQ1     :$400B
            enum TRIANGLEWAVE {
                CNT0                    = $4008,
                CNT1                    = $4009,
                FREQ0                   = $400A,
                FREQ1                   = $400B
            }
            byte NOISE_CNT0             :$400C
            byte NOISE_CNT1             :$400D
            byte NOISE_FREQ0            :$400E
            byte NOISE_FREQ1            :$400F
            byte PCM_CNT                :$4010
            byte PCM_VOLUMECNT          :$4011
            byte PCM_ADDRESS            :$4012
            byte PCM_LENGTH             :$4013
            byte SND_CNT                :$4015
            enum SNDENABLE {
                SQUARE_0                = %00000001,
                SQUARE_1                = %00000010,
                TRIANGLE                = %00000100,
                NOISE                   = %00001000,
                DMC                     = %00010000
            }

            enum MMC5 {
                GRAPHICS_MODE    = 0x5104,
                GRAPHMODE_SPLIT    = 0x02,
                GRAPHMODE_EXGRAPHIC   = 0x01,
                GRAPHMODE_EXRAMWRITE  = 0x00,//0x02,
                GRAPHMODE_NORMAL   = 0x03,
                SPLIT_CNT     = 0x5200,
                SPLITMODE_ENABLED   = 0x80,
                SPLITMODE_RIGHT    = 0x40,
                SPLIT_SCROLL    = 0x5201,
                SPLIT_PAGE     = 0x5202,
                IRQ_LINE     = 0x5203,
                IRQ_CNT      = 0x5204,
                IRQ_ENABLE     = 0x80,
                SRAM_ADDRESS    = 0x6000, // 0x6000-0x7FFF
                SRAM_ENABLE_A    = 0x5102,
                SRAM_ENABLE_A_CODE   = 0x02,
                SRAM_ENABLE_B    = 0x5103,
                SRAM_ENABLE_B_CODE   = 0x01,
                SRAM_BANK_SELECT_6000  = 0x5113,
                MULT_VALUE_A    = 0x5205,
                MULT_VALUE_B    = 0x5206,
                MULT_RESULT     = 0x5205,  // could be read using 16 bit macros
                MULT_RESULT_LO    = 0x5205, // lo( A * B )
                MULT_RESULT_HI    = 0x5206, // hi( A * B )
                EXRAM_ADDRESS    = 0x5C00, // 0x5C00-0x5FFF
                NAMETABLE_SELECT   = 0x5105,
                PRG_BANKSIZE    = 0x5100,
                PRG_BANKSIZE_32K   = 0,
                PRG_BANKSIZE_16K   = 1,
                PRG_BANKSIZE_8K    = 3,
                PRG_BANK_SELECT_8000  = 0x5114,
                PRG_BANK_SELECT_A000  = 0x5115,
                PRG_BANK_SELECT_C000  = 0x5116,
                PRG_BANK_SELECT_E000  = 0x5117,
                PRG_BANK_SELECT_16K_8000 = 0x5115,
                PRG_BANK_SELECT_16K_C000 = 0x5117,
                PRG_BANK_SELECT_32K   = 0x5117,
                SELECT_PRG_MASK    = 0x7F,
                SELECT_PRG_ACTIVATE   = 0x80,
                CHR_BANKSIZE    = 0x5101,
                CHR_BANK_ONE_8K    = 0,
                CHR_BANK_TWO_4K    = 1,
                CHR_BANK_THREE_2K   = 2,
                CHR_BANK_FOUR_1K   = 3,
                SPRCHR_BANK_SELECT_1K_0000 = 0x5120,
                SPRCHR_BANK_SELECT_1K_0400 = 0x5121,
                SPRCHR_BANK_SELECT_1K_0800 = 0x5122,
                SPRCHR_BANK_SELECT_1K_0C00 = 0x5123,
                SPRCHR_BANK_SELECT_1K_1000 = 0x5124,
                SPRCHR_BANK_SELECT_1K_1400 = 0x5125,
                SPRCHR_BANK_SELECT_1K_1800 = 0x5126,
                SPRCHR_BANK_SELECT_1K_1C00 = 0x5127,
                SPRCHR_BANK_SELECT_2K_0000 = 0x5121,
                SPRCHR_BANK_SELECT_2K_0800 = 0x5123,
                SPRCHR_BANK_SELECT_2K_1000 = 0x5125,
                SPRCHR_BANK_SELECT_2K_1800 = 0x5127,
                SPRCHR_BANK_SELECT_4K_0000 = 0x5123,
                SPRCHR_BANK_SELECT_4K_1000 = 0x5127,
                SPRCHR_BANK_SELECT_8K_0000 = 0x5127,
                BGCHR_BANK_SELECT_2K_0000 = 0x5128,
                BGCHR_BANK_SELECT_2K_0800 = 0x5129,
                BGCHR_BANK_SELECT_2K_1000 = 0x512A,
                BGCHR_BANK_SELECT_2K_1800 = 0x512B,
                SOUND_CH1_PULSECNT = 0x5000,
                SOUND_CH1_FREQ_LO = 0x5002,
                SOUND_CH1_FREQ_HI = 0x5003,
                SOUND_CH2_PULSECNT = 0x5004,
                SOUND_CH2_FREQ_LO = 0x5006,
                SOUND_CH2_FREQ_HI = 0x5007,
                SOUND_CH3_VOICE_CH = 0x5010,
                SOUND_CH4_VOICE_CH = 0x5011,
                SOUND_CH_OUTPUT  = 0x5015,
            }

            inline mmc5_init()
            {
                lda #MMC5.GRAPHMODE_EXGRAPHIC
                    sta MMC5.GRAPHICS_MODE
                    lda #0
                    sta MMC5.SPLIT_CNT
                    sta MMC5.SOUND_CH_OUTPUT
                    sta MMC5.SOUND_CH3_VOICE_CH
                    ldx #0
                    stx MMC5.BGCHR_BANK_SELECT_2K_0000
                    inx
                    stx MMC5.BGCHR_BANK_SELECT_2K_0800
                    inx
                    stx MMC5.BGCHR_BANK_SELECT_2K_1000
                    inx
                    stx MMC5.BGCHR_BANK_SELECT_2K_1800
            }

            inline mmc5_select_prg_8000_a()
            {
                ora #MMC5.SELECT_PRG_ACTIVATE
                    sta MMC5.PRG_BANK_SELECT_8000
            }

            inline mmc5_select_prg_8000(number)
            {
                lda number
                    mmc5_select_prg_8000_a()
            }

            inline mmc5_select_prg_8000i(number)
            {
                assign(MMC5.PRG_BANK_SELECT_8000, #number|MMC5.SELECT_PRG_ACTIVATE)
            }

            inline mmc5_save_prg_A000_bank_number()
            {
                pha
                    assign(pBankA000_prev, pBankA000_cur)
                    pla
            }

            inline mmc5_select_prg_A000_a()
            {
                mmc5_save_prg_A000_bank_number()
                    ora #MMC5.SELECT_PRG_ACTIVATE
                    sta pBankA000_cur
                    sta MMC5.PRG_BANK_SELECT_A000
            }

            inline mmc5_select_prg_A000(number)
            {
                lda number
                    mmc5_select_prg_A000_a()
            }

            inline mmc5_select_prg_A000i_raw(number)
            {
                lda #number|MMC5.SELECT_PRG_ACTIVATE
                    sta pBankA000_cur
                    sta MMC5.PRG_BANK_SELECT_A000
            }

            inline mmc5_select_prg_A000i(number)
            {
                assign(pBankA000_prev, pBankA000_cur)
                    mmc5_select_prg_A000i_raw(number)
            }

            inline mmc5_select_prg_A000i_push(number)
            {
                lda pBankA000_cur
                    pha
                    lda #number|MMC5.SELECT_PRG_ACTIVATE
                    sta pBankA000_cur
                    sta MMC5.PRG_BANK_SELECT_A000
            }

            inline mmc5_select_prg_A000_x_push(var)
            {
                lda pBankA000_cur
                    pha
                    lda var, x
                    ora #MMC5.SELECT_PRG_ACTIVATE
                    sta pBankA000_cur
                    sta MMC5.PRG_BANK_SELECT_A000
            }

            inline mmc5_select_prg_A000_push(var)
            {
                lda pBankA000_cur
                    pha
                    lda var
                    ora #MMC5.SELECT_PRG_ACTIVATE
                    sta pBankA000_cur
                    sta MMC5.PRG_BANK_SELECT_A000
            }

            inline mmc5_restore_prg_A000_pop()
            {
                pla
                    sta pBankA000_cur
                    sta MMC5.PRG_BANK_SELECT_A000
            }

            inline mmc5_restore_prg_A000(number)
            {
                lda pBankA000_prev
                    sta pBankA000_cur
                    sta MMC5.PRG_BANK_SELECT_A000
            }

            inline mmc5_select_prg_C000_a()
            {
                ora #MMC5.SELECT_PRG_ACTIVATE
                    sta MMC5.PRG_BANK_SELECT_C000
            }

            inline mmc5_select_prg_C000(number)
            {
                lda number
                    mmc5_select_prg_C000_a()
            }

            inline mmc5_select_prg_C000i(number)
            {
                assign(MMC5.PRG_BANK_SELECT_C000, #number|MMC5.SELECT_PRG_ACTIVATE)
            }

            inline mmc5_select_prg_E000_a()
            {
                ora #MMC5.SELECT_PRG_ACTIVATE
                    sta MMC5.PRG_BANK_SELECT_E000
            }

            inline mmc5_select_prg_E000(number)
            {
                lda number
                    mmc5_select_prg_E000_a()
            }

            inline mmc5_select_prg_E000i(number)
            {
                assign(MMC5.PRG_BANK_SELECT_E000, #number|MMC5.SELECT_PRG_ACTIVATE)
            }

            inline mmc5_multiply(valueA, valueB)
            {
                assign(MMC5.MULT_VALUE_A, valueA)
                    assign(MMC5.MULT_VALUE_B, valueB)
            }

            inline assign(dest,value)
            {
                lda value
                    sta dest
            }

            inline assign_x(dest,value)
            {
                lda value
                    sta dest,x
            }

            inline x_assign_x(dest,src)
            {
                lda src,x
                    sta dest,x
            }

            inline x_assign_y(dest,src)
            {
                lda src,x
                    sta dest,y
            }

            inline assign_y(dest,value)
            {
                lda value
                    sta dest,y
            }

            inline x_assign(dest,src)
            {
                lda src,x
                    sta dest
            }

            inline y_assign(dest,src)
            {
                lda src,y
                    sta dest
            }

            inline assign_ind(dest,value)
            {
                lda value
                    sta (dest)
            }

            inline assign_ind_y(dest,value)
            {
                lda value
                    sta (dest),y
            }

            inline ind_x_assign(dest,src)
            {
                lda (src,x)
                    sta dest
            }

            inline ind_y_assign(dest,src)
            {
                lda (src),y
                    sta dest
            }

            inline assign_16_8(dest,value)
            {
                lda value
                    sta dest+0
                    lda #0
                    sta dest+1
            }

            inline assign_16_8_x(dest,value)
            {
                lda value
                    sta dest+0,x
                    lda #0
                    sta dest+1,x
            }

            inline assign_16_8_y(dest,value)
            {
                lda value
                    sta dest+0,y
                    lda #0
                    sta dest+1,y
            }

            inline assign_16_16(dest,value)
            {
                lda value+0
                    sta dest+0
                    lda value+1
                    sta dest+1
            }

            inline assign_16_16_x(dest,value)
            {
                lda value+0
                    sta dest+0,x
                    lda value+1
                    sta dest+1,x
            }

            inline y_assign_16_16_x(dest,value)
            {
                lda value+0,y
                    sta dest+0,x
                    lda value+1,y
                    sta dest+1,x
            }

            inline assign_16_16_y(dest,value)
            {
                lda value+0
                    sta dest+0,y
                    lda value+1
                    sta dest+1,y
            }

            inline ind_assign_16_16_x(dest,value)
            {
                ldy #0
                    lda (value),y
                    sta dest+0,x
                    iny
                    lda (value),y
                    sta dest+1,x
            }

            inline x_assign_16_16(dest,value)
            {
                lda value+0,x
                    sta dest +0
                    lda value+1,x
                    sta dest +1
            }

            inline x_assign_16_16_x(dest,value)
            {
                lda value+0,x
                    sta dest +0,x
                    lda value+1,x
                    sta dest +1,x
            }

            inline y_ind_assign_16_16(dest,value)
            {
                lda (value),y
                    sta dest +0
                    iny
                    lda (value),y
                    sta dest +1
            }

            inline y_assign_16_16(dest,value)
            {
                lda value+0,y
                    sta dest +0
                    lda value+1,y
                    sta dest +1
            }

            inline assign_16i(dest,value)
            {
                lda #lo(value)
                    sta dest+0
                    lda #hi(value)
                    sta dest+1
            }

            inline assign_16i_x(dest,value)
            {
                lda #lo(value)
                    sta dest+0,x
                    lda #hi(value)
                    sta dest+1,x
            }

            inline assign_16i_y(dest,value)
            {
                lda #lo(value)
                    sta dest+0,y
                    lda #hi(value)
                    sta dest+1,y
            }

            inline zero_16(dest)
            {
                lda #0
                    sta dest+0
                    sta dest+1
            }

            inline zero_32(dest)
            {
                lda #0
                    sta dest+0
                    sta dest+1
                    sta dest+2
                    sta dest+3
            }

            inline zero_16_x(dest)
            {
                lda #0
                    sta dest+0,x
                    sta dest+1,x
            }

            inline zero_16_y(dest)
            {
                lda #0
                    sta dest+0,y
                    sta dest+1,y
            }

            inline tyx()
            {
                tya
                    tax
            }

            inline txy()
            {
                txa
                    tay
            }

            inline test(dest,mask)
            {
                lda mask
                    bit dest
            }

            inline test_x(dest,mask)
            {
                lda dest,x
                    and mask
            }

            inline test_16_8(dest,mask)
            {
                lda mask+0
                    bit dest+0
            }

            inline test_16_16(dest,mask)
            {
                lda mask+0
                    bit dest+0
                    if (zero) 
                    {
                        lda mask+1
                            bit dest+1
                    }
            }

            inline test_16i(dest,mask)
            {
                lda #lo(mask)
                    bit dest+0
                    if (zero) 
                    {
                        lda #hi(mask)
                            bit dest+1
                    }
            }

            inline or(dest,mask)
            {
                lda dest
                    ora mask
                    sta dest
            }

            inline or_x_a(dest)
            {
                ora dest,x
                    sta dest,x
            }

            inline or_x(dest,mask)
            {
                lda mask
                    or_x_a(dest)
            }

            inline or_y_a(dest)
            {
                ora dest,y
                    sta dest,y
            }

            inline or_y(dest,mask)
            {
                lda mask
                    or_y_a(dest)
            }

            inline or_16_8(dest,mask)
            {
                lda dest+0
                    ora mask
                    sta dest+0
            }

            inline or_16_8_x(dest,mask)
            {
                lda dest+0,x
                    ora mask
                    sta dest+0,x
            }

            inline or_16_16(dest,mask)
            {
                lda dest+0
                    ora mask+0
                    sta dest+0
                    lda dest+1
                    ora mask+1
                    sta dest+1
            }

            inline or_16_16_x(dest,mask)
            {
                lda dest+0
                    ora mask+0
                    sta dest+0,x
                    lda dest+1
                    ora mask+1
                    sta dest+1,x
            }

            inline or_16i(dest,mask)
            {
                lda dest+0
                    ora #lo(mask)
                    sta dest+0
                    lda dest+1
                    ora #hi(mask)
                    sta dest+1
            }

            inline or_16i_x(dest,mask)
            {
                lda dest+0,x
                    ora #lo(mask)
                    sta dest+0,x
                    lda dest+1,x
                    ora #hi(mask)
                    sta dest+1,x
            }

            inline xor(dest,mask)
            {
                lda dest
                    eor mask
                    sta dest
            }

            inline xor_x(dest,mask)
            {
                lda dest,x
                    eor mask
                    sta dest,x
            }

            inline xor_16_8(dest,mask)
            {
                lda dest+0
                    eor mask
                    sta dest+0
            }

            inline xor_16_8_x(dest,mask)
            {
                lda dest+0,x
                    eor mask
                    sta dest+0,x
            }

            inline xor_16_16(dest,mask)
            {
                lda dest+0
                    eor mask+0
                    sta dest+0
                    lda dest+1
                    eor mask+1
                    sta dest+1
            }

            inline xor_16_16_x(dest,mask)
            {
                lda dest+0
                    eor mask+0
                    sta dest+0,x
                    lda dest+1
                    eor mask+1
                    sta dest+1,x
            }

            inline xor_16i(dest,mask)
            {
                lda dest+0
                    eor #lo(mask)
                    sta dest+0
                    lda dest+1
                    eor #hi(mask)
                    sta dest+1
            }

            inline xor_16i_x(dest,mask)
            {
                lda dest+0,x
                    eor #lo(mask)
                    sta dest+0,x
                    lda dest+1,x
                    eor #hi(mask)
                    sta dest+1,x
            }

            inline and_8(dest,mask)
            {
                lda dest
                    and mask
                    sta dest
            }

            inline and_x(dest,mask)
            {
                lda dest,x
                    and mask
                    sta dest,x
            }

            inline and_y(dest,mask)
            {
                lda dest,y
                    and mask
                    sta dest,y
            }

            inline and_16_8(dest,mask)
            {
                lda dest+0
                    and mask
                    sta dest+0
            }

            inline and_16_8_x(dest,mask)
            {
                lda dest+0,x
                    and mask
                    sta dest+0,x
            }

            inline and_16_16(dest,mask)
            {
                lda dest+0
                    and mask+0
                    sta dest+0
                    lda dest+1
                    and mask+1
                    sta dest+1
            }

            inline and_16_16_x(dest,mask)
            {
                lda dest+0
                    and mask+0
                    sta dest+0,x
                    lda dest+1
                    and mask+1
                    sta dest+1,x
            }

            inline and_16i(dest,mask)
            {
                lda dest+0
                    and #lo(mask)
                    sta dest+0
                    lda dest+1
                    and #hi(mask)
                    sta dest+1
            }

            inline and_16i_x(dest,mask)
            {
                lda dest+0,x
                    and #lo(mask)
                    sta dest+0,x
                    lda dest+1,x
                    and #hi(mask)
                    sta dest+1,x
            }

            inline and_or(dest,and_mask,or_mask)
            {
                lda dest
                    and and_mask
                    ora or_mask
                    sta dest
            }

            inline add(dest,value)
            {
                clc
                    lda dest
                    adc value
                    sta dest
            }

            inline add_x(dest,value)
            {
                clc
                    lda dest,x
                    adc value
                    sta dest,x
            }

            inline y_add(dest,value)
            {
                clc
                    lda dest
                    adc value, y
                    sta dest
            }

            inline add_x_a(dest)
            {
                clc
                    adc dest,x
                    sta dest,x
            }

            inline add_16_8_a(dest)
            {
                clc
                    adc dest
                    sta dest
                    lda dest+1
                    adc #0
                    sta dest+1
            }

            inline adds_16_8_a(dest)
            {
                if (negative) 
                {
                    clc
                        adc dest
                        sta dest
                        lda dest+1
                        adc #0xFF
                        sta dest+1
                } 
                else 
                {
                    clc
                        adc dest
                        sta dest
                        lda dest+1
                        adc #0
                        sta dest+1
                }
            }

            inline add_16_8_a_x(dest)
            {
                clc
                    adc dest,x
                    sta dest,x
                    lda dest+1,x
                    adc #0
                    sta dest+1,x
            }

            inline adds_16_8_a_x(dest)
            {
                if (negative) 
                {
                    clc
                        adc dest+0,x
                        sta dest+0,x
                        lda dest+1,x
                        adc #0xFF
                } 
                else 
                {
                    clc
                        adc dest+0,x
                        sta dest+0,x
                        lda dest+1,x
                        adc #0
                }
                sta dest+1,x
            }

            inline adds_16_8_a_x_to(src, dest)
            {
                if (negative) 
                {
                    clc
                        adc src+0,x
                        sta dest+0
                        lda src+1,x
                        adc #0xFF
                        sta dest+1
                } 
                else 
                {
                    clc
                        adc src+0,x
                        sta dest+0
                        lda src+1,x
                        adc #0
                        sta dest+1
                }
            }

            inline add_16_8(dest,value)
            {
                lda value
                    add_16_8_a(dest)
            }

            inline adds_16_8(dest,value)
            {
                lda value
                    adds_16_8_a(dest)
            }

            inline add_16_8_to(src,value,dest)
            {
                clc
                    lda src+0
                    adc value
                    sta dest+0
                    lda src+1
                    adc #0
                    sta dest+1
            }

            inline add_16_8yind_to(src,value,dest)
            {
                clc
                    lda src+0
                    adc (value),y
                    sta dest+0
                    lda src+1
                    adc #0
                    sta dest+1
            }

            inline adds_16_8yind_to(src,value,dest)
            {
                lda (value),y
                    if (negative) 
                    {
                        ldx #0xFF
                    } 
                    else 
                    {
                        ldx #0
                    }
                stx btemp
                    clc
                    adc src+0
                    sta dest+0
                    lda src+1
                    adc btemp
                    sta dest+1
            }

            inline add_16_8_a_to_x(src,dest)
            {
                clc
                    adc src+0
                    sta dest+0, x
                    lda src+1
                    adc #0
                    sta dest+1, x
            }

            inline add_16_8_x(dest,value)
            {
                lda value
                    add_16_8_a_x(dest)
            }

            inline adds_16_8_x(dest,value)
            {
                lda value
                    adds_16_8_a_x(dest)
            }

            inline add_16_16(dest,value)
            {
                clc
                    lda dest
                    adc value
                    sta dest
                    lda dest+1
                    adc value+1
                    sta dest+1
            }

            inline add_16_16_x(dest,value)
            {
                clc
                    lda dest,x
                    adc value
                    sta dest,x
                    lda dest+1,x
                    adc value+1
                    sta dest+1,x
            }

            inline x_add_16_8_to(dest,value,src)
            {
                clc
                    lda src+0,x
                    adc value
                    sta dest+0
                    lda src+1,x
                    adc #0
                    sta dest+1
            }

            inline add_8y_16x_to_16(var8, var16, dest16)
            {
                lda var8, y
                    if (positive) 
                    {
                        clc
                            adc var16 +0,x
                            sta dest16+0
                            lda var16 +1,x
                            adc #0
                    } 
                    else 
                    {
                        clc
                            adc var16 +0,x
                            sta dest16+0
                            lda var16 +1,x
                            adc #0xFF
                    }
                sta dest16+1
            }

            inline x_sub_16_8_to(dest,value,src)
            {
                sec
                    lda src+0,x
                    sbc value
                    sta dest+0
                    lda src+1,x
                    sbc #0
                    sta dest+1
            }

            inline add_16i(dest,value)
            {
                clc
                    lda dest
                    adc #lo(value)
                    sta dest
                    lda dest+1
                    adc #hi(value)
                    sta dest+1
            }

            inline add_16i_x(dest,value)
            {
                clc
                    lda dest,x
                    adc #lo(value)
                    sta dest,x
                    lda dest+1,x
                    adc #hi(value)
                    sta dest+1,x
            }

            inline sub(dest,value)
            {
                sec
                    lda dest
                    sbc value
                    sta dest
            }

            inline sub_x(dest,value)
            {
                sec
                    lda dest,x
                    sbc value
                    sta dest,x
            }

            inline sub_16_8_a(dest)
            {
                sec
                    sta _b_temp
                    lda dest+0
                    sbc _b_temp
                    sta dest+0
                    lda dest+1
                    sbc #0
                    sta dest+1
            }

            inline sub_16_8_a_to(value,dest)
            {
                sec
                    sta _b_temp
                    lda value+0
                    sbc _b_temp
                    sta dest+0
                    lda value+1
                    sbc #0
                    sta dest+1
            }

            inline sub_16_8_a_x(dest)
            {
                sec
                    sta _b_temp
                    lda dest+0,x
                    sbc _b_temp
                    sta dest+0,x
                    lda dest+1,x
                    sbc #0
                    sta dest+1,x
            }

            inline x_sub_16_8_a_to(value, dest)
            {
                sec
                    sta _b_temp
                    lda value+0,x
                    sbc _b_temp
                    sta dest+0
                    lda value+1,x
                    sbc #0
                    sta dest+1
            }

            inline y_sub_16_8_a_to(value, dest)
            {
                sec
                    sta _b_temp
                    lda value+0,y
                    sbc _b_temp
                    sta dest+0
                    lda value+1,y
                    sbc #0
                    sta dest+1
            }

            inline sub_16_8(dest,value)
            {
                sec
                    lda dest+0
                    sbc value
                    sta dest+0
                    lda dest+1
                    sbc #0
                    sta dest+1
            }

            inline sub_16_8_to(src,value,dest)
            {
                sec
                    lda src+0
                    sbc value
                    sta dest+0
                    lda src+1
                    sbc #0
                    sta dest+1
            }

            inline sub_16_8_x(dest,value)
            {
                sec
                    lda dest+0,x
                    sbc value
                    sta dest+0,x
                    lda dest+1,x
                    sbc #0
                    sta dest+1,x
            }

            inline sub_16_16(dest,value)
            {
                sec
                    lda dest+0
                    sbc value+0
                    sta dest+0
                    lda dest+1
                    sbc value+1
                    sta dest+1
            }

            inline sub_16_16_to(valuea,valueb,dest)
            {
                sec
                    lda valuea+0
                    sbc valueb+0
                    sta dest+0
                    lda valuea+1
                    sbc valueb+1
                    sta dest+1
            }

            inline add_16_16_to(valuea,valueb,dest)
            {
                clc
                    lda valuea+0
                    adc valueb+0
                    sta dest+0
                    lda valuea+1
                    adc valueb+1
                    sta dest+1
            }

            inline sub16_16_x(dest,value)
            {
                sec
                    lda dest+0,x
                    sbc value+0
                    sta dest+0,x
                    sbc dest+1,x
                    adc value+1
                    sta dest+1,x
            }

            inline sub_16i(dest,value)
            {
                sec
                    lda dest
                    sbc #lo(value)
                    sta dest
                    lda dest+1
                    sbc #hi(value)
                    sta dest+1
            }

            inline sub_16i_x(dest,value)
            {
                sec
                    lda dest,x
                    sbc #lo(value)
                    sta dest,x
                    lda dest+1,x
                    sbc #hi(value)
                    sta dest+1,x
            }

            inline mul_a( dest, multipiler )
            {
                clc
                    lda #0
                    ldx dest
                    while (nonzero) 
                    {
                        adc multipiler
                            dex
                    }
            }

            inline mul_x_a( dest, multipiler )
            {
                clc
                    lda #0
                    ldy dest,x
                    while (nonzero) 
                    {
                        adc multipiler
                            dey
                    }
            }

            inline mul( dest, multipiler )
            {
                mul_a( dest, multipiler )
                    sta dest
            }

            inline mul_x( dest, multipiler )
            {
                mul_x_a( dest, multipiler )
                    sta dest,x
            }

            inline mul_16_8( dest, multipiler )
            {
                zero_16(_w_temp)
                    ldx multipiler
                    while (nonzero) 
                    {
                        add_16_16( _w_temp, dest )
                            dex
                    }
                assign_16_16( dest, _w_temp )
            }

            inline mul_16_8_x( dest, multipiler )
            {
                zero_16(_w_temp)
                    ldx multipiler
                    while (nonzero) 
                    {
                        add_16_16_x( _w_temp, dest )
                            dex
                    }
                assign_16_16_x( dest, _w_temp )
            }

            inline asl2_a()
            {
                asl a
                    asl a
            }

            inline asl3_a()
            {
                asl a
                    asl a
                    asl a
            }

            inline asl4_a()
            {
                asl a
                    asl a
                    asl a
                    asl a
            }

            inline asl5_a()
            {
                asl a
                    asl a
                    asl a
                    asl a
                    asl a
            }

            inline asl6_a()
            {
                asl a
                    asl a
                    asl a
                    asl a
                    asl a
                    asl a
            }

            inline asl7_a()
            {
                asl a
                    asl a
                    asl a
                    asl a
                    asl a
                    asl a
                    asl a
            }

            inline asl_16_1( dest )
            {
                asl dest+0
                    rol dest+1
            }

            inline asl_16( dest, amount )
            {
                ldx amount
                    while (not zero) 
                    {
                        asl dest+0
                            rol dest+1
                            dex
                    }
            }

            inline asl_16_to( dest, src, amount )
            {
                assign_16_16(src,dest)
                    ldx amount
                    while (not zero) 
                    {
                        asl src+0/*
                                    php
                                    lda src+1
                                    asl a
                                    plp
                                    adc #0
                                    sta src+1*/
                            rol dest+1
                            dex
                    }
            }

            inline asl_8_to_16( dest, src, amount )
            {
                lda src
                    sta dest+0
                    lda #0
                    sta dest+1
                    ldx amount
                    while (not zero) 
                    {
                        asl dest+0
                            rol dest+1
                            dex
                    }
            }

            inline asl2_8_a_to_16( dest )
            {
                sta dest+0
                    lda #0
                    sta dest+1
                    asl dest+0
                    rol dest+1
                    asl dest+0
                    rol dest+1
            }

            inline lsr2_a()
            {
                lsr a
                    lsr a
            }

            inline lsr3_a()
            {
                lsr a
                    lsr a
                    lsr a
            }

            inline lsr4_a()
            {
                lsr a
                    lsr a
                    lsr a
                    lsr a
            }

            inline lsr5_a()
            {
                lsr a
                    lsr a
                    lsr a
                    lsr a
                    lsr a
            }

            inline lsr6_a()
            {
                lsr a
                    lsr a
                    lsr a
                    lsr a
                    lsr a
                    lsr a
            }

            inline lsr7_a()
            {
                lsr a
                    lsr a
                    lsr a
                    lsr a
                    lsr a
                    lsr a
                    lsr a
            }

            inline lsr_16( dest, amount )
            {
                ldx amount
                    while (not zero) 
                    {
                        lsr dest+1
                            ror dest+0
                            dex
                    }
            }

            inline lsr_16_to( dest, src, amount )
            {
                assign_16_16(src,dest)
                    ldx amount
                    while (not zero) 
                    {
                        lsr dest+1
                            ror dest+0
                            dex
                    }
            }

            inline lsr_16_by_6_to_8( dest, src )
            {
                lda src+0
                    rol a
                    rol a
                    rol a
                    and #3
                    sta dest
                    lda src+1
                    asl a
                    asl a
                    ora dest
                    sta dest
            }

            inline lsr_16_by_5_to_8( dest, src )
            {
                lda src+0    // A  = LOW(B)  >> 5
                lsr5_a()    //
                sta dest    //
                lda src+1    // A |= HIGH(B) << 3
                asl3_a()    //
                ora dest    //
                sta dest    //
            }

            inline lsr_16_by_4_to_8( dest, src )
            {
                lda src+0    // A  = LOW(B)  >> 4
                lsr4_a()    //
                sta dest    //
                lda src+1    // A |= HIGH(B) << 4
                asl4_a()    //
                ora dest    //
                sta dest    //
            }

            inline lsr_16_by_3_to_8( dest, src )
            {
                lda src+0    // A  = LOW(B)  >> 3
                lsr3_a()     //
                sta dest     //
                lda src+1    // A |= HIGH(B) << 5
                asl5_a()     //
                ora dest     //
                sta dest     //
            }

            inline lsr_16_by_2_to_8( dest, src )
            {
                lda src+0
                lsr2_a()
                sta dest
                lda src+1
                asl6_a()
                ora dest
                and #7
                sta dest
            }

            inline div( dest, amount )
            {
                sec
                ldx #0
                lda amount
                while (nonzero) 
                {
                    bmi div_remainder
                    inx
                    sec
                    sbc dest
                }
                jmp div_done
            div_remainder:
                dex
            div_done:
                stx dest
            }

            inline div_with_rem( dest, amount )
            {
                sec
                ldx #0
                lda dest
                while (nonzero) 
                {
                    bmi div_remainder
                    inx
                    sec
                    sbc amount
                }
                assign(_b_remainder, #0)
                jmp div_done
            div_remainder:
                clc
                adc amount
                sta _b_remainder
                dex
            div_done:
                stx dest
            }

            inline div_16_8_to_x( dest, amount )
            {
                assign_16_16( _w_temp, dest )
                    ldx    #0
                    _d168tx_loop:
                    inx
                    sub_16i( _w_temp, amount )
                    bmi    _d168tx_loop_end
                    bne    _d168tx_loop
                    lda    _w_temp+0
                    bne    _d168tx_loop
                    _d168tx_loop_end:
                    if (nonzero)
                        dex
            }

            inline mod_16_by_240_to_8( dest, src )
            {
                lda src
                    sta _w_temp+0
                    ora src+1
                    if (not zero) 
                    {
                        lda src+1
                            sta _w_temp+1
                            _loop:
                            sub_16i( _w_temp, 240 )
                            lda _w_temp+1
                            bmi _loop_end
                            bne _loop
                            lda _w_temp+0
                            bne _loop
                            _loop_end:
                            beq _is_solid
                            lda _w_temp
                            eor #0xFF
                            clc
                            adc #1
                    }
            _is_solid:
                sta    dest
            }

            inline mod_16_to_8( dest, src, val )
            {
                lda src
                    sta _w_temp+0
                    ora src+1
                    if (not zero) 
                    {
                        lda src+1
                            sta _w_temp+1
                            _loop:
                            sub_16i( _w_temp, val )
                            lda _w_temp+1
                            bmi _loop_end
                            bne _loop
                            lda _w_temp+0
                            bne _loop
                            _loop_end:
                            beq _is_solid
                            lda _w_temp
                            eor #0xFF
                            clc
                            adc #1
                    }
            _is_solid:
                sta    dest
            }

            inline abs_a()
            {
                if (is minus) 
                {
                    eor #0xFF
                        clc
                        adc #1
                }
            }

            inline abs(number)
            {
                lda number
                    if (is minus) 
                    {
                        eor #0xFF
                            sta number
                            inc number
                    }
            }

            inline abs_16(number)
            {
                lda number+1
                    if (is minus) 
                    {
                        neg_16(number)
                    }
            }

            inline neg_a()
            {
                eor #0xFF
                    clc
                    adc #1
            }

            inline neg(number)
            {
                lda number
                    eor #0xFF
                    sta number
                    inc number
            }

            inline neg_16(number)
            {
                sec
                    lda #0
                    sbc number+0
                    sta number+0
                    lda #0
                    sbc number+1
                    sta number+1
            }

            inline inc_16(number)
            {
                inc number+0
                    if (zero)
                        inc number+1
            }

            inline inc_16_limit(number)
            {
                /*
                   ldx number+0
                   inx
                   if(not zero) 
                   {
                   ldx number+1
                   inx
                   if(not zero) 
                   {
                   inc number+0
                   if(zero)
                   inc number+1
                   }
                   }
                 */

                lda #0xFF
                    cmp number+0
                    bne _inc_nolimit_reached
                    cmp number+1
                    beq _inc_limit_reached
                    _inc_nolimit_reached:
                    inc number+0
                    if (zero)
                        inc number+1
                            _inc_limit_reached:
            }

            inline inc_16_x(number)
            {
                inc number+0,x
                    if (zero)
                        inc number+1,x
            }

            inline dec_16(number)
            {
                lda number+0
                    if (zero)
                        dec number+1
                            dec number+0
            }

            inline dec_16_x(number)
            {
                lda number+0,x
                    if (zero)
                        dec number+1,x
                            dec number+0,x
            }

            inline clip_16(number)
            {
                lda number+1
                    if (negative) 
                    {
                        zero_16( number )
                    }
            }

            inline compare(src, value)
            {
                lda src
                    cmp value
            }

            inline compare_x(src, value)
            {
                lda src, x
                    cmp value
            }

            inline x_compare_x(src, value)
            {
                lda src, x
                    cmp value, x
            }

            inline compare_16_16(src, value)
            {
                lda src+1
                    cmp value+1
                    if (equal) 
                    {
                        lda src+0
                            cmp value+0
                    }
            }

            inline compare_16_16_x(src, value)
            {
                lda src+1
                    cmp value+1, x
                    if (equal) 
                    {
                        lda src+0
                            cmp value+0, x
                    }
            }

            inline compare_16_x_16_x(src, value)
            {
                lda src+1, x
                    cmp value+1, x
                    if (equal) 
                    {
                        lda src+0, x
                            cmp value+0, x
                    }
            }

            inline compare_16_y_16_x(src, value)
            {
                lda src+1, y
                    cmp value+1, x
                    if (equal) 
                    {
                        lda src+0, y
                            cmp value+0, x
                    }
            }

            inline compare_8_y_8_x(src, value)
            {
                lda src, y
                    cmp value, x
            }

            inline compare_16_x_16_y(src, value)
            {
                lda src+1, x
                    cmp value+1, y
                    if (equal) 
                    {
                        lda src+0, x
                            cmp value+0, y
                    }
            }

            inline compare_8_x_8_y(src, value)
            {
                lda src, x
                    cmp value, y
            }

            inline compare_8_x_8_x(src, value)
            {
                lda src, x
                    cmp value, x
            }

            inline compare_8_x_8(src, value)
            {
                lda src, x
                    cmp value
            }

            inline compare_8_y_8_y(src, value)
            {
                lda src, y
                    cmp value, y
            }

            inline compare_16_16_y(src, value)
            {
                lda src+1
                    cmp value+1, y
                    if (equal) 
                    {
                        lda src+0
                            cmp value+0, y
                    }
            }

            inline compare_16i(src, value)
            {
                lda src+1
                    cmp #hi(value)
                    if (equal) 
                    {
                        lda src+0
                            cmp #lo(value)
                    }
            }

            inline pusha()
            {
                pha
            }

            inline popa()
            {
                pla
            }

            inline toss16()
            {
                pla
                    pla
            }

            inline push(value)
            {
                lda value
                    pusha()
            }

            inline push_x(src)
            {
                lda src,x
                    pusha()
            }

            inline push_16(src)
            {
                lda src+0
                    pusha()
                    lda src+1
                    pusha()
            }

            inline push_16_x(src)
            {
                lda src+0,x
                    pusha()
                    lda src+1,x
                    pusha()
            }

            inline pop(dest)
            {
                popa()
                    sta dest
            }

            inline pop_x(dest)
            {
                popa()
                    sta dest,x
            }

            inline pop_16(dest)
            {
                popa()
                    sta dest+1
                    popa()
                    sta dest+0
            }

            inline pop_16_x(dest)
            {
                popa()
                    sta dest+1,x
                    popa()
                    sta dest+0,x
            }

            inline peek()
            {
                popa()
                    pusha()
            }

            inline pushx()
            {
                txa
                    pusha()
            }

            inline popx()
            {
                popa()
                    tax
            }

            inline peekx()
            {
                popa()
                    pusha()
                    tax
            }

            inline pushy()
            {
                tya
                    pusha()
            }

            inline popy()
            {
                popa()
                    tay
            }

            inline peeky()
            {
                popa()
                    pusha()
                    tay
            }

            inline pushp()
            {
                php
            }

            inline popp()
            {
                plp
            }

            inline pushsp()
            {
                tsx
                    pushx()
            }

            inline popsp()
            {
                popx()
                    txs
            }

            inline push_all()
            {
                pushp()
                    pusha()
                    pushx()
                    pushy()
            }

            inline pop_all()
            {
                popy()
                    popx()
                    popa()
                    popp()
            }

            inline memcpy_inline( dest, src, size )
            {
                ldx #0
                    do 
                    {
                        lda src,x
                            sta dest,x
                            inx
                            cpx size
                    } 
                while (nonzero)
            }
            inline memset_inline( memdest, value, memsize)
            {
                lda value
                    ldx #0
                    do 
                    {
                        sta memdest,x
                            inx
                            cpx memsize
                    } 
                while (nonzero)
            }

            enum COLOUR {
                BLUE  = 0x01,
                RED  = 0x05,
                YELLOW = 0x07,
                GREEN  = 0x09,
            }

            byte _b_temp
            word _w_temp
            pointer _p_temp
            pointer _jsrind_temp
            byte _b_remainder
            byte _random_value
            byte _random_ticks
            pointer _mem_src
            pointer _mem_dest
            byte counter
            byte palcol
            pointer paddr
            pointer pstr
            char msgbuf[64]

            function Turn_Video_On()
            {
                assign(PPU.CNT1, #%00001000|%00000010)
            }

            function Turn_Video_Off()
            {
                assign(PPU.CNT1, #0)
            }

            function vram_write_hex_a()
            {
                pha
                    tax
                    lsr a
                    lsr a
                    lsr a
                    lsr a
                    and #$0F
                    cmp #$A
                    bcs _hexxy0
                    clc
                    adc #$30
                    jmp _hexxy0d
                    _hexxy0:
                    clc
                    adc #$41-10
                    _hexxy0d:
                    sta $2007
                    txa
                    and #$0F
                    cmp #$A
                    bcs _hexxy1
                    clc
                    adc #$30
                    jmp _hexxy1d
                    _hexxy1:
                    clc
                    adc #$41-10
                    _hexxy1d:
                    sta $2007
                    pla
            }

            inline vram_write_string_inl(addr, str)
            {
                vram_set_address_i(addr)
                    assign_16i(pstr, str)
                    vram_write_string()
            }

            function vram_write_string()
            {
                ldy #0
                    forever 
                    {
                        lda (pstr), y
                            if (zero) 
                            {
                                vram_clear_address()
                                    return
                            }
                        vram_write_a()
                            iny
                    }
            }

            byte setamt[] = {0,0,0,0,0,0,0,7}

            function vram_init()
            {
                vram_set_address_i(0x3F00)
                    vram_write(#0x30)
                    vram_write(#0x21)
                    vram_write(#0x22)
                    vram_write(#0x0F)
                    vram_set_address_i(0x2000)
                    lda #0
                    ldy #8 // 1024 bytes
                    do 
                    {
                        lda setamt-1,y
                            ldx #128
                            do 
                            {
                                vram_write_a()
                                    dex
                            } 
                        while (not zero)
                            dey
                    } 
                while (not zero)
                    vram_write_string_inl(0x2000+0x40, strTitle)
                        vram_clear_address()
            }

            function palette_memset()
            {
                unvblank_wait()
                    vblank_wait()
                    vram_set_address_i(0x3F00)
                    ldy #16
                    do 
                    {
                        vram_write_regx()
                            dey
                    } 
                while (not equal)
                    vram_clear_address()
            }

            inline palette_memset_inl(col)
            {
                ldx col
                    palette_memset()
            }

            function pal_animate()
            {
                vram_set_address_i(0x3F00)
                    lda palcol
                    clc
                    adc #0x10
                    sta palcol
                    and #0x40
                    php
                    lda palcol
                    plp
                    if (set) 
                    {
                        eor #0x30
                    }
                and #0x3F
                    vram_write_a()
                    vram_clear_address()
            }

            function pal_animate2()
            {
                vram_set_address_i(0x3F00)
                    ldx palcol
                    inx
                    txa
                    sta palcol
                    and #0x10
                    php
                    lda palcol
                    plp
                    if (set) 
                    {
                        eor #0x0F
                    }
                and #0x0F
                    vram_write_a()
                    vram_clear_address()
            }

            inline wait_for(amount)
            {
                ldx amount
                    wait_for_func()
            }

            function wait_for_func()
            {
                do 
                {
                    vblank_wait_full()
                        dex
                } 
                while (nonzero)
            }

            function message_error()
            {
                assign(palcol, #COLOUR.RED)
                    forever 
                    {
                        wait_for(#5)
                            pal_animate()
                    }
            }

            char strTitle[] = "\a\a\a\a\a\a\aNESHLA Demo Program"
            char strHello[] = "Hello, World!"

            inline custom_system_initialize()
            {
                disable_decimal_mode()
                    disable_interrupts()
                    reset_stack()  // this is why this MUST be inline!
                    lda  #0
                    sta  PPU.CNT0
                    sta  PPU.CNT1
                    sta  PPU.BG_SCROLL
                    sta  PPU.BG_SCROLL
                    sta  PCM_CNT
                    sta  PCM_VOLUMECNT
                    sta  SND_CNT
                    lda  #0xC0
                    sta  joystick.cnt1
            }

            interrupt.irq int_irq()
            {
            }

            interrupt.nmi int_nmi()
            {
            }

            interrupt.start main()
            {
                custom_system_initialize()
                    vram_init()
                    Turn_Video_Off()
                    vram_write_string_inl(0x2000+(15*32+10), strHello)
                    vram_clear_address()
                    assign(palcol, #COLOUR.YELLOW)
                    Turn_Video_On()
                    forever 
                    {
                        wait_for(#6)
                            pal_animate()
                    }
            }

            function jsr_ind()
            {
                jmp (paddr)
            }
        """
        scanner = [
            (FunctionDecl, "inline enable_interrupts()"),
            (ScopeBegin, "{"),
            (InstructionLine, "cli"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline disable_interrupts()"),
            (ScopeBegin, "{"),
            (InstructionLine, "sei"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline enable_decimal_mode()"),
            (ScopeBegin, "{"),
            (InstructionLine, "sei"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline disable_decimal_mode()"),
            (ScopeBegin, "{"),
            (InstructionLine, "cld"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline set_carry_flag()"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline clear_carry_flag()"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline reset_stack()"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx #0xFF"),
            (InstructionLine, "txs"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline nes_reset()"),
            (ScopeBegin, "{"),
            (InstructionLine, "jmp $FFFC"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline system_initialize()"),
            (ScopeBegin, "{"),
            (FunctionCall, "disable_decimal_mode()"),
            (FunctionCall, "disable_interrupts()"),
            (FunctionCall, "reset_stack()"),
            (FunctionCall, "vblank_wait()"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta PPU.CNT0"),
            (InstructionLine, "sta PPU.CNT1"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (InstructionLine, "sta $4010"),
            (InstructionLine, "sta $4011"),
            (InstructionLine, "sta $4015"),
            (InstructionLine, "lda #0xC0"),
            (InstructionLine, "sta joystick.cnt1"),
            (FunctionCall, "enable_interrupts()"),
            (ScopeEnd, "}"),
            (Enum, "enum PPU"),
            (Typedef, "typedef struct OAM_ENTRY_"),
            (Typedef, "typedef struct PALENT_"),
            (Typedef, "typedef struct PALETTE_"),
            (FunctionDecl, "inline ppu_ctl0_assign( newctl )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda newctl"),
            (InstructionLine, "sta _ppu_ctl0"),
            (InstructionLine, "sta PPU.CNT0"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_ctl0_set( mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda _ppu_ctl0"),
            (InstructionLine, "ora #mask"),
            (InstructionLine, "sta _ppu_ctl0"),
            (InstructionLine, "sta PPU.CNT0"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_ctl0_clear( mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda _ppu_ctl0"),
            (InstructionLine, "and #~(mask)"),
            (InstructionLine, "sta _ppu_ctl0"),
            (InstructionLine, "sta PPU.CNT0"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_ctl0_adjust( clearmask, setmask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda _ppu_ctl0"),
            (InstructionLine, "and #~(clearmask)"),
            (InstructionLine, "ora #setmask"),
            (InstructionLine, "sta _ppu_ctl0"),
            (InstructionLine, "sta PPU.CNT0"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_ctl0_xor( mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda _ppu_ctl0"),
            (InstructionLine, "eor #mask"),
            (InstructionLine, "sta _ppu_ctl0"),
            (InstructionLine, "sta PPU.CNT0"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_ctl0_test( mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda mask"),
            (InstructionLine, "bit _ppu_ctl0"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_enable_nmi( mask )"),
            (ScopeBegin, "{"),
            (FunctionCall, "ppu_ctl0_set( %10000000 )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_disable_nmi()"),
            (ScopeBegin, "{"),
            (FunctionCall, "ppu_ctl0_clear( %10000000 )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_turn_off()"),
            (ScopeBegin, "{"),
            (FunctionCall, "ppu_ctl0_assign( 0 )"),
            (FunctionCall, "vblank_wait()"),
            (FunctionCall, "ppu_ctl1_assign( 0 )"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_turn_on_draw()"),
            (ScopeBegin, "{"),
            (FunctionCall, "ppu_enable_nmi()"),
            (FunctionCall, "ppu_ctl1_set( |(%00010000, %00001000) )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_turn_off_draw()"),
            (ScopeBegin, "{"),
            (FunctionCall, "ppu_disable_nmi()"),
            (FunctionCall, "ppu_ctl1_clear( |(%00010000, %00001000) )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_set_nametable( nametable )"),
            (ScopeBegin, "{"),
            (FunctionCall, "ppu_ctl0_adjust( %00000011, nametable )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_xor_nametable()"),
            (ScopeBegin, "{"),
            (FunctionCall, "ppu_ctl0_xor( %00000011 )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_ctl1_assign( newctl )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda newctl"),
            (InstructionLine, "sta _ppu_ctl1"),
            (InstructionLine, "sta PPU.CNT1"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_ctl1_set( mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda _ppu_ctl1"),
            (InstructionLine, "ora #mask"),
            (InstructionLine, "sta _ppu_ctl1"),
            (InstructionLine, "sta PPU.CNT1"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_ctl1_clear( mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda _ppu_ctl1"),
            (InstructionLine, "and #~(mask)"),
            (InstructionLine, "sta _ppu_ctl1"),
            (InstructionLine, "sta PPU.CNT1"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_ctl1_adjust( clearmask, setmask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda _ppu_ctl1"),
            (InstructionLine, "and #~(clearmask)"),
            (InstructionLine, "ora #setmask"),
            (InstructionLine, "sta _ppu_ctl1"),
            (InstructionLine, "sta PPU.CNT1"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_ctl1_test( mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda mask"),
            (InstructionLine, "bit _ppu_ctl1"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_set_palette_intensity( newbits )"),
            (ScopeBegin, "{"),
            (FunctionCall, "ppu_ctl1_adjust( %11100000, newbits )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vblank_wait()"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "do"),
            (InstructionLine, "lda PPU.STATUS"),
            (ConditionalDecl, "while(['is', 'plus'])"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vblank_wait_full()"),
            (ScopeBegin, "{"),
            (FunctionCall, "vblank_wait()"),
            (FunctionCall, "unvblank_wait()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vblank_wait_for( amount )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx amount"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (FunctionCall, "vblank_wait_full()"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline unvblank_wait()"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "do"),
            (InstructionLine, "lda PPU.STATUS"),
            (ConditionalDecl, "while(['is', 'minus'])"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline test_scanline()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda PPU.STATUS"),
            (InstructionLine, "and #%00100000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ppu_clean_latch()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda PPU.STATUS"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_clear_address()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_set_address( newaddress )"),
            (ScopeBegin, "{"),
            (FunctionCall, "ppu_clean_latch()"),
            (InstructionLine, "lda +([newaddress], 1)"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (InstructionLine, "lda +([newaddress], 0)"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_set_address_i( newaddress )"),
            (ScopeBegin, "{"),
            (FunctionCall, "ppu_clean_latch()"),
            (InstructionLine, "lda #hi(newaddress)"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (InstructionLine, "lda #lo(newaddress)"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_set_scroll( x, y )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( PPU.BG_SCROLL, x )"),
            (FunctionCall, "assign( PPU.BG_SCROLL, y )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_write( value )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( PPU.IO, value )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_write_ind( value )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign_ind( PPU.IO, value )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_write_x( value )"),
            (ScopeBegin, "{"),
            (FunctionCall, "x_assign( PPU.IO, value )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_write_ind_y( value )"),
            (ScopeBegin, "{"),
            (FunctionCall, "ind_y_assign( PPU.IO, value )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_write_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "sta PPU.IO"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_write_regx()"),
            (ScopeBegin, "{"),
            (InstructionLine, "stx PPU.IO"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_write_16( value )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( PPU.IO, +([value], 0) )"),
            (FunctionCall, "assign( PPU.IO, +([value], 1) )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_write_16_i( value )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( PPU.IO, hi(value) )"),
            (FunctionCall, "assign( PPU.IO, lo(value) )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_read( dest )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( dest, PPU.IO )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_ind_read( dest )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign_ind( dest, PPU.IO )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_ind_y_read( dest )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign_ind_y( dest, PPU.IO )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_read_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda PPU.IO"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_read_16( dest )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( +([dest], 0), PPU.IO )"),
            (FunctionCall, "assign( +([dest], 1), PPU.IO )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_set_sprite_address( newaddress )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( PPU.SPR_ADDRESS, +([newaddress], 1) )"),
            (FunctionCall, "assign( PPU.SPR_ADDRESS, +([newaddress], 0) )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_set_sprite_address_i( newaddress )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( PPU.SPR_ADDRESS, hi(newaddress) )"),
            (FunctionCall, "assign( PPU.SPR_ADDRESS, lo(newaddress) )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_set_sprite_data( x, y, tile, attributes )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( PPU.SPR_IO, y )"),
            (FunctionCall, "assign( PPU.SPR_IO, tile )"),
            (FunctionCall, "assign( PPU.SPR_IO, attributes )"),
            (FunctionCall, "assign( PPU.SPR_IO, x )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_sprite_dma_copy( oamptr )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( PPU.SPR_DMA, hi(oamptr) )"),
            (ScopeEnd, "}"),
            (Variable, "byte JOYSTICK_CNT0 :$4016"),
            (Variable, "byte JOYSTICK_CNT1 :$4017"),
            (Enum, "enum JOYSTICK"),
            (FunctionDecl, "inline reset_joystick()"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( JOYSTICK.CNT0, 1 )"),
            (FunctionCall, "assign( JOYSTICK.CNT0, 0 )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline read_joystick0()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda JOYSTICK.CNT0"),
            (InstructionLine, "and #1"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline read_joystick1()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda JOYSTICK.CNT1"),
            (InstructionLine, "and #1"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline test_joystick1( buttonmask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda _joypad"),
            (InstructionLine, "and buttonmask"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline test_joystick1_prev( buttonmask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda _joypad_prev"),
            (InstructionLine, "and buttonmask"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline test_button_release( buttonmask )"),
            (ScopeBegin, "{"),
            (FunctionCall, "test_joystick1( buttonmask )"),
            (ConditionalDecl, "if(['zero'])"),
            (ScopeBegin, "{"),
            (FunctionCall, "test_joystick1_prev( buttonmask )"),
            (ScopeEnd, "}"),
            (InstructionLine, "eor #0xFF"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline test_button_press( buttonmask )"),
            (ScopeBegin, "{"),
            (FunctionCall, "test_joystick1( buttonmask )"),
            (ConditionalDecl, "if(['nonzero'])"),
            (ScopeBegin, "{"),
            (FunctionCall, "test_joystick1_prev( buttonmask )"),
            (InstructionLine, "eor #0xFF"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (Variable, "byte SQUAREWAVEA_CNT0 :$4000"),
            (Variable, "byte SQUAREWAVEA_CNT1 :$4001"),
            (Variable, "byte SQUAREWAVEA_FREQ0 :$4002"),
            (Variable, "byte SQUAREWAVEA_FREQ1 :$4003"),
            (Enum, "enum SQUAREWAVEA"),
            (Variable, "byte SQUAREWAVEB_CNT0 :$4004"),
            (Variable, "byte SQUAREWAVEB_CNT1 :$4005"),
            (Variable, "byte SQUAREWAVEB_FREQ0 :$4006"),
            (Variable, "byte SQUAREWAVEB_FREQ1 :$4007"),
            (Enum, "enum SQUAREWAVEB"),
            (Variable, "byte TRIANGLEWAVE_CNT0 :$4008"),
            (Variable, "byte TRIANGLEWAVE_CNT1 :$4009"),
            (Variable, "byte TRIANGLEWAVE_FREQ0 :$400A"),
            (Variable, "byte TRIANGLEWAVE_FREQ1 :$400B"),
            (Enum, "enum TRIANGLEWAVE"),
            (Variable, "byte NOISE_CNT0 :$400C"),
            (Variable, "byte NOISE_CNT1 :$400D"),
            (Variable, "byte NOISE_FREQ0 :$400E"),
            (Variable, "byte NOISE_FREQ1 :$400F"),
            (Variable, "byte PCM_CNT :$4010"),
            (Variable, "byte PCM_VOLUMECNT :$4011"),
            (Variable, "byte PCM_ADDRESS :$4012"),
            (Variable, "byte PCM_LENGTH :$4013"),
            (Variable, "byte SND_CNT :$4015"),
            (Enum, "enum SNDENABLE"),
            (Enum, "enum MMC5"),
            (FunctionDecl, "inline mmc5_init()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #MMC5.GRAPHMODE_EXGRAPHIC"),
            (InstructionLine, "sta MMC5.GRAPHICS_MODE"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta MMC5.SPLIT_CNT"),
            (InstructionLine, "sta MMC5.SOUND_CH_OUTPUT"),
            (InstructionLine, "sta MMC5.SOUND_CH3_VOICE_CH"),
            (InstructionLine, "ldx #0"),
            (InstructionLine, "stx MMC5.BGCHR_BANK_SELECT_2K_0000"),
            (InstructionLine, "inx"),
            (InstructionLine, "stx MMC5.BGCHR_BANK_SELECT_2K_0800"),
            (InstructionLine, "inx"),
            (InstructionLine, "stx MMC5.BGCHR_BANK_SELECT_2K_1000"),
            (InstructionLine, "inx"),
            (InstructionLine, "stx MMC5.BGCHR_BANK_SELECT_2K_1800"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_8000_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_8000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_8000( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda number"),
            (FunctionCall, "mmc5_select_prg_8000_a()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_8000i( number )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( MMC5.PRG_BANK_SELECT_8000, |([number], [MMC5, SELECT_PRG_ACTIVATE]) )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_save_prg_A000_bank_number()"),
            (ScopeBegin, "{"),
            (InstructionLine, "pha"),
            (FunctionCall, "assign( pBankA000_prev, pBankA000_cur )"),
            (InstructionLine, "pla"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_A000_a()"),
            (ScopeBegin, "{"),
            (FunctionCall, "mmc5_save_prg_A000_bank_number()"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_A000( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda number"),
            (FunctionCall, "mmc5_select_prg_A000_a()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_A000i_raw( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #|([number], [MMC5, SELECT_PRG_ACTIVATE])"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_A000i( number )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( pBankA000_prev, pBankA000_cur )"),
            (FunctionCall, "mmc5_select_prg_A000i_raw( number )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_A000i_push( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda pBankA000_cur"),
            (InstructionLine, "pha"),
            (InstructionLine, "lda #|([number], [MMC5, SELECT_PRG_ACTIVATE])"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_A000_x_push( var )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda pBankA000_cur"),
            (InstructionLine, "pha"),
            (InstructionLine, "lda"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_A000_push( var )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda pBankA000_cur"),
            (InstructionLine, "pha"),
            (InstructionLine, "lda var"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_restore_prg_A000_pop()"),
            (ScopeBegin, "{"),
            (InstructionLine, "pla"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_restore_prg_A000( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda pBankA000_prev"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_C000_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_C000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_C000( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda number"),
            (FunctionCall, "mmc5_select_prg_C000_a()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_C000i( number )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( MMC5.PRG_BANK_SELECT_C000, |([number], [MMC5, SELECT_PRG_ACTIVATE]) )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_E000_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_E000"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_E000( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda number"),
            (FunctionCall, "mmc5_select_prg_E000_a()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_select_prg_E000i( number )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( MMC5.PRG_BANK_SELECT_E000, |([number], [MMC5, SELECT_PRG_ACTIVATE]) )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mmc5_multiply( valueA, valueB )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( MMC5.MULT_VALUE_A, valueA )"),
            (FunctionCall, "assign( MMC5.MULT_VALUE_B, valueB )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline x_assign_x( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline x_assign_y( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_y( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline x_assign( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline y_assign( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_ind( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_ind_y( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta (dest), y"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ind_x_assign( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda (src, x)"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ind_y_assign( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda (src), y"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_16_8( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_16_8_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_16_8_y( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_16_16( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([value], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([value], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_16_16_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([value], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([value], 1)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline y_assign_16_16_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_16_16_y( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([value], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([value], 1)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline ind_assign_16_16_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldy #0"),
            (InstructionLine, "lda (value), y"),
            (InstructionLine, "sta"),
            (InstructionLine, "iny"),
            (InstructionLine, "lda (value), y"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline x_assign_16_16( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline x_assign_16_16_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline y_ind_assign_16_16( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda (value), y"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "iny"),
            (InstructionLine, "lda (value), y"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline y_assign_16_16( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_16i( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #lo(value)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda #hi(value)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_16i_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #lo(value)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda #hi(value)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline assign_16i_y( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #lo(value)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda #hi(value)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline zero_16( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline zero_32( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "sta +([dest], 1)"),
            (InstructionLine, "sta +([dest], 2)"),
            (InstructionLine, "sta +([dest], 3)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline zero_16_x( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline zero_16_y( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline tyx()"),
            (ScopeBegin, "{"),
            (InstructionLine, "tya"),
            (InstructionLine, "tax"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline txy()"),
            (ScopeBegin, "{"),
            (InstructionLine, "txa"),
            (InstructionLine, "tay"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline test( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda mask"),
            (InstructionLine, "bit dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline test_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "and mask"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline test_16_8( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([mask], 0)"),
            (InstructionLine, "bit +([dest], 0)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline test_16_16( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([mask], 0)"),
            (InstructionLine, "bit +([dest], 0)"),
            (ConditionalDecl, "if(['zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([mask], 1)"),
            (InstructionLine, "bit +([dest], 1)"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline test_16i( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #lo(mask)"),
            (InstructionLine, "bit +([dest], 0)"),
            (ConditionalDecl, "if(['zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #hi(mask)"),
            (InstructionLine, "bit +([dest], 1)"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "ora mask"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or_x_a( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ora"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda mask"),
            (FunctionCall, "or_x_a( dest )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or_y_a( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ora"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or_y( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda mask"),
            (FunctionCall, "or_y_a( dest )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or_16_8( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "ora mask"),
            (InstructionLine, "sta +([dest], 0)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or_16_8_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "ora mask"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or_16_16( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "ora +([mask], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "ora +([mask], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or_16_16_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "ora +([mask], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "ora +([mask], 1)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or_16i( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "ora #lo(mask)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "ora #hi(mask)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline or_16i_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "ora #lo(mask)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "ora #hi(mask)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline xor( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "eor mask"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline xor_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "eor mask"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline xor_16_8( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "eor mask"),
            (InstructionLine, "sta +([dest], 0)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline xor_16_8_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "eor mask"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline xor_16_16( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "eor +([mask], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "eor +([mask], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline xor_16_16_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "eor +([mask], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "eor +([mask], 1)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline xor_16i( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "eor #lo(mask)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "eor #hi(mask)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline xor_16i_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "eor #lo(mask)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "eor #hi(mask)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline and_8( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "and mask"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline and_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "and mask"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline and_y( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "and mask"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline and_16_8( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "and mask"),
            (InstructionLine, "sta +([dest], 0)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline and_16_8_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "and mask"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline and_16_16( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "and +([mask], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "and +([mask], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline and_16_16_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "and +([mask], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "and +([mask], 1)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline and_16i( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "and #lo(mask)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "and #hi(mask)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline and_16i_x( dest, mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "and #lo(mask)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "and #hi(mask)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline and_or( dest, and_mask, or_mask )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "and and_mask"),
            (InstructionLine, "ora or_mask"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline y_add( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_x_a( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16_8_a( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc dest"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline adds_16_8_a( dest )"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "if(['negative'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc dest"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "adc #0xFF"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "else"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc dest"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16_8_a_x( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline adds_16_8_a_x( dest )"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "if(['negative'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0xFF"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "else"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0"),
            (ScopeEnd, "}"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline adds_16_8_a_x_to( src, dest )"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "if(['negative'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0xFF"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "else"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16_8( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (FunctionCall, "add_16_8_a( dest )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline adds_16_8( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (FunctionCall, "adds_16_8_a( dest )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16_8_to( src, value, dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16_8yind_to( src, value, dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "adc (value), y"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline adds_16_8yind_to( src, value, dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda (value), y"),
            (ConditionalDecl, "if(['negative'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx #0xFF"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "else"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx #0"),
            (ScopeEnd, "}"),
            (InstructionLine, "stx btemp"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc +([src], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "adc btemp"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16_8_a_to_x( src, dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc +([src], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16_8_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (FunctionCall, "add_16_8_a_x( dest )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline adds_16_8_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (FunctionCall, "adds_16_8_a_x( dest )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16_16( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "adc +([value], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16_16_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc +([value], 1)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline x_add_16_8_to( dest, value, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_8y_16x_to_16( var8, var16, dest16 )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (ConditionalDecl, "if(['positive'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta +([dest16], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "else"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta +([dest16], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0xFF"),
            (ScopeEnd, "}"),
            (InstructionLine, "sta +([dest16], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline x_sub_16_8_to( dest, value, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16i( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "adc #lo(value)"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "adc #hi(value)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16i_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #lo(value)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #hi(value)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_16_8_a( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "sta _b_temp"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "sbc _b_temp"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_16_8_a_to( value, dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "sta _b_temp"),
            (InstructionLine, "lda +([value], 0)"),
            (InstructionLine, "sbc _b_temp"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([value], 1)"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_16_8_a_x( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "sta _b_temp"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc _b_temp"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline x_sub_16_8_a_to( value, dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "sta _b_temp"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc _b_temp"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline y_sub_16_8_a_to( value, dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "sta _b_temp"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc _b_temp"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_16_8( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_16_8_to( src, value, dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_16_8_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_16_16( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "sbc +([value], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "sbc +([value], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_16_16_to( valuea, valueb, dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda +([valuea], 0)"),
            (InstructionLine, "sbc +([valueb], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([valuea], 1)"),
            (InstructionLine, "sbc +([valueb], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline add_16_16_to( valuea, valueb, dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda +([valuea], 0)"),
            (InstructionLine, "adc +([valueb], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([valuea], 1)"),
            (InstructionLine, "adc +([valueb], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub16_16_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc +([value], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "sbc"),
            (InstructionLine, "adc +([value], 1)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_16i( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "sbc #lo(value)"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "sbc #hi(value)"),
            (InstructionLine, "sta +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline sub_16i_x( dest, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #lo(value)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #hi(value)"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mul_a( dest, multipiler )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "ldx dest"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "adc multipiler"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mul_x_a( dest, multipiler )"),
            (ScopeBegin, "{"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "ldy"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "adc multipiler"),
            (InstructionLine, "dey"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mul( dest, multipiler )"),
            (ScopeBegin, "{"),
            (FunctionCall, "mul_a( dest, multipiler )"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mul_x( dest, multipiler )"),
            (ScopeBegin, "{"),
            (FunctionCall, "mul_x_a( dest, multipiler )"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mul_16_8( dest, multipiler )"),
            (ScopeBegin, "{"),
            (FunctionCall, "zero_16( _w_temp )"),
            (InstructionLine, "ldx multipiler"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeBegin, "{"),
            (FunctionCall, "add_16_16( _w_temp, dest )"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (FunctionCall, "assign_16_16( dest, _w_temp )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mul_16_8_x( dest, multipiler )"),
            (ScopeBegin, "{"),
            (FunctionCall, "zero_16( _w_temp )"),
            (InstructionLine, "ldx multipiler"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeBegin, "{"),
            (FunctionCall, "add_16_16_x( _w_temp, dest )"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (FunctionCall, "assign_16_16_x( dest, _w_temp )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl2_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl3_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl4_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl5_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl6_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl7_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl_16_1( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "asl +([dest], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl_16( dest, amount )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx amount"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "asl +([dest], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl_16_to( dest, src, amount )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign_16_16( src, dest )"),
            (InstructionLine, "ldx amount"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "asl +([src], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl_8_to_16( dest, src, amount )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda src"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (InstructionLine, "ldx amount"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "asl +([dest], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline asl2_8_a_to_16( dest )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (InstructionLine, "asl +([dest], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (InstructionLine, "asl +([dest], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr2_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr3_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr4_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr5_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr6_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr7_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr_16( dest, amount )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx amount"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lsr +([dest], 1)"),
            (InstructionLine, "ror +([dest], 0)"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr_16_to( dest, src, amount )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign_16_16( src, dest )"),
            (InstructionLine, "ldx amount"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lsr +([dest], 1)"),
            (InstructionLine, "ror +([dest], 0)"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr_16_by_6_to_8( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "rol a"),
            (InstructionLine, "rol a"),
            (InstructionLine, "rol a"),
            (InstructionLine, "and #3"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "ora dest"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr_16_by_5_to_8( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 0)"),
            (FunctionCall, "lsr5_a()"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([src], 1)"),
            (FunctionCall, "asl3_a()"),
            (InstructionLine, "ora dest"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr_16_by_4_to_8( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 0)"),
            (FunctionCall, "lsr4_a()"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([src], 1)"),
            (FunctionCall, "asl4_a()"),
            (InstructionLine, "ora dest"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr_16_by_3_to_8( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 0)"),
            (FunctionCall, "lsr3_a()"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([src], 1)"),
            (FunctionCall, "asl5_a()"),
            (InstructionLine, "ora dest"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline lsr_16_by_2_to_8( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 0)"),
            (FunctionCall, "lsr2_a()"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([src], 1)"),
            (FunctionCall, "asl6_a()"),
            (InstructionLine, "ora dest"),
            (InstructionLine, "and #7"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline div( dest, amount )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "ldx #0"),
            (InstructionLine, "lda amount"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "bmi div_remainder"),
            (InstructionLine, "inx"),
            (InstructionLine, "sec"),
            (InstructionLine, "sbc dest"),
            (ScopeEnd, "}"),
            (InstructionLine, "jmp div_done"),
            (Label, "DIV_REMAINDER"),
            (InstructionLine, "dex"),
            (Label, "DIV_DONE"),
            (InstructionLine, "stx dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline div_with_rem( dest, amount )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "ldx #0"),
            (InstructionLine, "lda dest"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "bmi div_remainder"),
            (InstructionLine, "inx"),
            (InstructionLine, "sec"),
            (InstructionLine, "sbc amount"),
            (ScopeEnd, "}"),
            (FunctionCall, "assign( _b_remainder, 0 )"),
            (InstructionLine, "jmp div_done"),
            (Label, "DIV_REMAINDER"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc amount"),
            (InstructionLine, "sta _b_remainder"),
            (InstructionLine, "dex"),
            (Label, "DIV_DONE"),
            (InstructionLine, "stx dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline div_16_8_to_x( dest, amount )"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign_16_16( _w_temp, dest )"),
            (InstructionLine, "ldx #0"),
            (Label, "_D168TX_LOOP"),
            (InstructionLine, "inx"),
            (FunctionCall, "sub_16i( _w_temp, amount )"),
            (InstructionLine, "bmi _d168tx_loop_end"),
            (InstructionLine, "bne _d168tx_loop"),
            (InstructionLine, "lda +([_w_temp], 0)"),
            (InstructionLine, "bne _d168tx_loop"),
            (Label, "_D168TX_LOOP_END"),
            (ConditionalDecl, "if(['nonzero'])"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mod_16_by_240_to_8( dest, src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda src"),
            (InstructionLine, "sta +([_w_temp], 0)"),
            (InstructionLine, "ora +([src], 1)"),
            (ConditionalDecl, "if(['not', 'zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "sta +([_w_temp], 1)"),
            (Label, "_LOOP"),
            (FunctionCall, "sub_16i( _w_temp, 240 )"),
            (InstructionLine, "lda +([_w_temp], 1)"),
            (InstructionLine, "bmi _loop_end"),
            (InstructionLine, "bne _loop"),
            (InstructionLine, "lda +([_w_temp], 0)"),
            (InstructionLine, "bne _loop"),
            (Label, "_LOOP_END"),
            (InstructionLine, "beq _is_solid"),
            (InstructionLine, "lda _w_temp"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #1"),
            (ScopeEnd, "}"),
            (Label, "_IS_SOLID"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline mod_16_to_8( dest, src, val )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda src"),
            (InstructionLine, "sta +([_w_temp], 0)"),
            (InstructionLine, "ora +([src], 1)"),
            (ConditionalDecl, "if(['not', 'zero'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "sta +([_w_temp], 1)"),
            (Label, "_LOOP"),
            (FunctionCall, "sub_16i( _w_temp, val )"),
            (InstructionLine, "lda +([_w_temp], 1)"),
            (InstructionLine, "bmi _loop_end"),
            (InstructionLine, "bne _loop"),
            (InstructionLine, "lda +([_w_temp], 0)"),
            (InstructionLine, "bne _loop"),
            (Label, "_LOOP_END"),
            (InstructionLine, "beq _is_solid"),
            (InstructionLine, "lda _w_temp"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #1"),
            (ScopeEnd, "}"),
            (Label, "_IS_SOLID"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline abs_a()"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "if(['is', 'minus'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #1"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline abs( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda number"),
            (ConditionalDecl, "if(['is', 'minus'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "sta number"),
            (InstructionLine, "inc number"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline abs_16( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([number], 1)"),
            (ConditionalDecl, "if(['is', 'minus'])"),
            (ScopeBegin, "{"),
            (FunctionCall, "neg_16( number )"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline neg_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #1"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline neg( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda number"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "sta number"),
            (InstructionLine, "inc number"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline neg_16( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sbc +([number], 0)"),
            (InstructionLine, "sta +([number], 0)"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sbc +([number], 1)"),
            (InstructionLine, "sta +([number], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline inc_16( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "inc +([number], 0)"),
            (ConditionalDecl, "if(['zero'])"),
            (InstructionLine, "inc +([number], 1)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline inc_16_limit( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda #0xFF"),
            (InstructionLine, "cmp +([number], 0)"),
            (InstructionLine, "bne _inc_nolimit_reached"),
            (InstructionLine, "cmp +([number], 1)"),
            (InstructionLine, "beq _inc_limit_reached"),
            (Label, "_INC_NOLIMIT_REA"),
            (InstructionLine, "inc +([number], 0)"),
            (ConditionalDecl, "if(['zero'])"),
            (InstructionLine, "inc +([number], 1)"),
            (Label, "_INC_LIMIT_REACH"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline inc_16_x( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "inc"),
            (ConditionalDecl, "if(['zero'])"),
            (InstructionLine, "inc"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline dec_16( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([number], 0)"),
            (ConditionalDecl, "if(['zero'])"),
            (InstructionLine, "dec +([number], 1)"),
            (InstructionLine, "dec +([number], 0)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline dec_16_x( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (ConditionalDecl, "if(['zero'])"),
            (InstructionLine, "dec"),
            (InstructionLine, "dec"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline clip_16( number )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([number], 1)"),
            (ConditionalDecl, "if(['negative'])"),
            (ScopeBegin, "{"),
            (FunctionCall, "zero_16( number )"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda src"),
            (InstructionLine, "cmp value"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_x( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp value"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline x_compare_x( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_16_16( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "cmp +([value], 1)"),
            (ConditionalDecl, "if(['equal'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "cmp +([value], 0)"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_16_16_x( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "cmp"),
            (ConditionalDecl, "if(['equal'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "cmp"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_16_x_16_x( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ConditionalDecl, "if(['equal'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_16_y_16_x( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ConditionalDecl, "if(['equal'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_8_y_8_x( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_16_x_16_y( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ConditionalDecl, "if(['equal'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_8_x_8_y( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_8_x_8_x( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_8_x_8( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp value"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_8_y_8_y( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_16_16_y( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "cmp"),
            (ConditionalDecl, "if(['equal'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "cmp"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline compare_16i( src, value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "cmp #hi(value)"),
            (ConditionalDecl, "if(['equal'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "cmp #lo(value)"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline pusha()"),
            (ScopeBegin, "{"),
            (InstructionLine, "pha"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline popa()"),
            (ScopeBegin, "{"),
            (InstructionLine, "pla"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline toss16()"),
            (ScopeBegin, "{"),
            (InstructionLine, "pla"),
            (InstructionLine, "pla"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline push( value )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (FunctionCall, "pusha()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline push_x( src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (FunctionCall, "pusha()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline push_16( src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda +([src], 0)"),
            (FunctionCall, "pusha()"),
            (InstructionLine, "lda +([src], 1)"),
            (FunctionCall, "pusha()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline push_16_x( src )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (FunctionCall, "pusha()"),
            (InstructionLine, "lda"),
            (FunctionCall, "pusha()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline pop( dest )"),
            (ScopeBegin, "{"),
            (FunctionCall, "popa()"),
            (InstructionLine, "sta dest"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline pop_x( dest )"),
            (ScopeBegin, "{"),
            (FunctionCall, "popa()"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline pop_16( dest )"),
            (ScopeBegin, "{"),
            (FunctionCall, "popa()"),
            (InstructionLine, "sta +([dest], 1)"),
            (FunctionCall, "popa()"),
            (InstructionLine, "sta +([dest], 0)"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline pop_16_x( dest )"),
            (ScopeBegin, "{"),
            (FunctionCall, "popa()"),
            (InstructionLine, "sta"),
            (FunctionCall, "popa()"),
            (InstructionLine, "sta"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline peek()"),
            (ScopeBegin, "{"),
            (FunctionCall, "popa()"),
            (FunctionCall, "pusha()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline pushx()"),
            (ScopeBegin, "{"),
            (InstructionLine, "txa"),
            (FunctionCall, "pusha()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline popx()"),
            (ScopeBegin, "{"),
            (FunctionCall, "popa()"),
            (InstructionLine, "tax"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline peekx()"),
            (ScopeBegin, "{"),
            (FunctionCall, "popa()"),
            (FunctionCall, "pusha()"),
            (InstructionLine, "tax"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline pushy()"),
            (ScopeBegin, "{"),
            (InstructionLine, "tya"),
            (FunctionCall, "pusha()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline popy()"),
            (ScopeBegin, "{"),
            (FunctionCall, "popa()"),
            (InstructionLine, "tay"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline peeky()"),
            (ScopeBegin, "{"),
            (FunctionCall, "popa()"),
            (FunctionCall, "pusha()"),
            (InstructionLine, "tay"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline pushp()"),
            (ScopeBegin, "{"),
            (InstructionLine, "php"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline popp()"),
            (ScopeBegin, "{"),
            (InstructionLine, "plp"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline pushsp()"),
            (ScopeBegin, "{"),
            (InstructionLine, "tsx"),
            (FunctionCall, "pushx()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline popsp()"),
            (ScopeBegin, "{"),
            (FunctionCall, "popx()"),
            (InstructionLine, "txs"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline push_all()"),
            (ScopeBegin, "{"),
            (FunctionCall, "pushp()"),
            (FunctionCall, "pusha()"),
            (FunctionCall, "pushx()"),
            (FunctionCall, "pushy()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline pop_all()"),
            (ScopeBegin, "{"),
            (FunctionCall, "popy()"),
            (FunctionCall, "popx()"),
            (FunctionCall, "popa()"),
            (FunctionCall, "popp()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline memcpy_inline( dest, src, size )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx #0"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (InstructionLine, "inx"),
            (InstructionLine, "cpx size"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline memset_inline( memdest, value, memsize )"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda value"),
            (InstructionLine, "ldx #0"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (InstructionLine, "sta"),
            (InstructionLine, "inx"),
            (InstructionLine, "cpx memsize"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeEnd, "}"),
            (Enum, "enum COLOUR"),
            (Variable, "byte _b_temp"),
            (Variable, "word _w_temp"),
            (Variable, "pointer _p_temp"),
            (Variable, "pointer _jsrind_temp"),
            (Variable, "byte _b_remainder"),
            (Variable, "byte _random_value"),
            (Variable, "byte _random_ticks"),
            (Variable, "pointer _mem_src"),
            (Variable, "pointer _mem_dest"),
            (Variable, "byte counter"),
            (Variable, "byte palcol"),
            (Variable, "pointer paddr"),
            (Variable, "pointer pstr"),
            (Variable, "char msgbuf[64]"),
            (FunctionDecl, "function Turn_Video_On()"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( PPU.CNT1, |(%00001000, %00000010) )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "function Turn_Video_Off()"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( PPU.CNT1, 0 )"),
            (ScopeEnd, "}"),
            (FunctionDecl, "function vram_write_hex_a()"),
            (ScopeBegin, "{"),
            (InstructionLine, "pha"),
            (InstructionLine, "tax"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "and #$0F"),
            (InstructionLine, "cmp #$A"),
            (InstructionLine, "bcs _hexxy0"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #$30"),
            (InstructionLine, "jmp _hexxy0d"),
            (Label, "_HEXXY0"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #0x37"),
            (Label, "_HEXXY0D"),
            (InstructionLine, "sta $2007"),
            (InstructionLine, "txa"),
            (InstructionLine, "and #$0F"),
            (InstructionLine, "cmp #$A"),
            (InstructionLine, "bcs _hexxy1"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #$30"),
            (InstructionLine, "jmp _hexxy1d"),
            (Label, "_HEXXY1"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #0x37"),
            (Label, "_HEXXY1D"),
            (InstructionLine, "sta $2007"),
            (InstructionLine, "pla"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline vram_write_string_inl( addr, str )"),
            (ScopeBegin, "{"),
            (FunctionCall, "vram_set_address_i( addr )"),
            (FunctionCall, "assign_16i( pstr, str )"),
            (FunctionCall, "vram_write_string()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "function vram_write_string()"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldy #0"),
            (ConditionalDecl, "forever"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda (pstr), y"),
            (ConditionalDecl, "if(['zero'])"),
            (ScopeBegin, "{"),
            (FunctionCall, "vram_clear_address()"),
            (FunctionReturn, "return"),
            (ScopeEnd, "}"),
            (FunctionCall, "vram_write_a()"),
            (InstructionLine, "iny"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (Variable, "byte setamt[]"),
            (VariableInitializer, " = { 0, 0, 0, 0, 0, 0, 0, 7 }"),
            (FunctionDecl, "function vram_init()"),
            (ScopeBegin, "{"),
            (FunctionCall, "vram_set_address_i( 0x3F00 )"),
            (FunctionCall, "vram_write( 0x30 )"),
            (FunctionCall, "vram_write( 0x21 )"),
            (FunctionCall, "vram_write( 0x22 )"),
            (FunctionCall, "vram_write( 0x0F )"),
            (FunctionCall, "vram_set_address_i( 0x2000 )"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "ldy #8"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (InstructionLine, "lda"),
            (InstructionLine, "ldx #128"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (FunctionCall, "vram_write_a()"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (InstructionLine, "dey"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['not', 'zero'])"),
            (FunctionCall, "vram_write_string_inl( +(0x2000, 0x40), strTitle )"),
            (FunctionCall, "vram_clear_address()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "function palette_memset()"),
            (ScopeBegin, "{"),
            (FunctionCall, "unvblank_wait()"),
            (FunctionCall, "vblank_wait()"),
            (FunctionCall, "vram_set_address_i( 0x3F00 )"),
            (InstructionLine, "ldy #16"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (FunctionCall, "vram_write_regx()"),
            (InstructionLine, "dey"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['not', 'equal'])"),
            (FunctionCall, "vram_clear_address()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline palette_memset_inl( col )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx col"),
            (FunctionCall, "palette_memset()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "function pal_animate()"),
            (ScopeBegin, "{"),
            (FunctionCall, "vram_set_address_i( 0x3F00 )"),
            (InstructionLine, "lda palcol"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #0x10"),
            (InstructionLine, "sta palcol"),
            (InstructionLine, "and #0x40"),
            (InstructionLine, "php"),
            (InstructionLine, "lda palcol"),
            (InstructionLine, "plp"),
            (ConditionalDecl, "if(['set'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "eor #0x30"),
            (ScopeEnd, "}"),
            (InstructionLine, "and #0x3F"),
            (FunctionCall, "vram_write_a()"),
            (FunctionCall, "vram_clear_address()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "function pal_animate2()"),
            (ScopeBegin, "{"),
            (FunctionCall, "vram_set_address_i( 0x3F00 )"),
            (InstructionLine, "ldx palcol"),
            (InstructionLine, "inx"),
            (InstructionLine, "txa"),
            (InstructionLine, "sta palcol"),
            (InstructionLine, "and #0x10"),
            (InstructionLine, "php"),
            (InstructionLine, "lda palcol"),
            (InstructionLine, "plp"),
            (ConditionalDecl, "if(['set'])"),
            (ScopeBegin, "{"),
            (InstructionLine, "eor #0x0F"),
            (ScopeEnd, "}"),
            (InstructionLine, "and #0x0F"),
            (FunctionCall, "vram_write_a()"),
            (FunctionCall, "vram_clear_address()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "inline wait_for( amount )"),
            (ScopeBegin, "{"),
            (InstructionLine, "ldx amount"),
            (FunctionCall, "wait_for_func()"),
            (ScopeEnd, "}"),
            (FunctionDecl, "function wait_for_func()"),
            (ScopeBegin, "{"),
            (ConditionalDecl, "do"),
            (ScopeBegin, "{"),
            (FunctionCall, "vblank_wait_full()"),
            (InstructionLine, "dex"),
            (ScopeEnd, "}"),
            (ConditionalDecl, "while(['nonzero'])"),
            (ScopeEnd, "}"),
            (FunctionDecl, "function message_error()"),
            (ScopeBegin, "{"),
            (FunctionCall, "assign( palcol, COLOUR.RED )"),
            (ConditionalDecl, "forever"),
            (ScopeBegin, "{"),
            (FunctionCall, "wait_for( 5 )"),
            (FunctionCall, "pal_animate()"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (Variable, "char strTitle[]"),
            (VariableInitializer, " = NESHLA Demo Program"),
            (Variable, "char strHello[]"),
            (VariableInitializer, " = Hello, World!"),
            (FunctionDecl, "inline custom_system_initialize()"),
            (ScopeBegin, "{"),
            (FunctionCall, "disable_decimal_mode()"),
            (FunctionCall, "disable_interrupts()"),
            (FunctionCall, "reset_stack()"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta PPU.CNT0"),
            (InstructionLine, "sta PPU.CNT1"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (InstructionLine, "sta $4010"),
            (InstructionLine, "sta $4011"),
            (InstructionLine, "sta $4015"),
            (InstructionLine, "lda #0xC0"),
            (InstructionLine, "sta joystick.cnt1"),
            (ScopeEnd, "}"),
            (FunctionDecl, "interrupt.irq int_irq()"),
            (ScopeBegin, "{"),
            (ScopeEnd, "}"),
            (FunctionDecl, "interrupt.nmi int_nmi()"),
            (ScopeBegin, "{"),
            (ScopeEnd, "}"),
            (FunctionDecl, "interrupt.start main()"),
            (ScopeBegin, "{"),
            (FunctionCall, "custom_system_initialize()"),
            (FunctionCall, "vram_init()"),
            (FunctionCall, "Turn_Video_Off()"),
            (FunctionCall, "vram_write_string_inl( +(0x2000, +(*(15, 32), 10)), strHello )"),
            (FunctionCall, "vram_clear_address()"),
            (FunctionCall, "assign( palcol, COLOUR.YELLOW )"),
            (FunctionCall, "Turn_Video_On()"),
            (ConditionalDecl, "forever"),
            (ScopeBegin, "{"),
            (FunctionCall, "wait_for( 6 )"),
            (FunctionCall, "pal_animate()"),
            (ScopeEnd, "}"),
            (ScopeEnd, "}"),
            (FunctionDecl, "function jsr_ind()"),
            (ScopeBegin, "{"),
            (InstructionLine, "jmp paddr"),
            (ScopeEnd, "}")
        ]
        parser = [
            (Function, "inline enable_interrupts()"),
            (Function, "inline disable_interrupts()"),
            (Function, "inline enable_decimal_mode()"),
            (Function, "inline disable_decimal_mode()"),
            (Function, "inline set_carry_flag()"),
            (Function, "inline clear_carry_flag()"),
            (Function, "inline reset_stack()"),
            (Function, "inline nes_reset()"),
            (Function, "inline system_initialize()"),
            (Enum, "enum PPU"),
            (Typedef, "typedef struct OAM_ENTRY_"),
            (Typedef, "typedef struct PALENT_"),
            (Typedef, "typedef struct PALETTE_"),
            (Function, "inline ppu_ctl0_assign( newctl )"),
            (Function, "inline ppu_ctl0_set( mask )"),
            (Function, "inline ppu_ctl0_clear( mask )"),
            (Function, "inline ppu_ctl0_adjust( clearmask, setmask )"),
            (Function, "inline ppu_ctl0_xor( mask )"),
            (Function, "inline ppu_ctl0_test( mask )"),
            (Function, "inline ppu_enable_nmi( mask )"),
            (Function, "inline ppu_disable_nmi()"),
            (Function, "inline ppu_turn_off()"),
            (Function, "inline ppu_turn_on_draw()"),
            (Function, "inline ppu_turn_off_draw()"),
            (Function, "inline ppu_set_nametable( nametable )"),
            (Function, "inline ppu_xor_nametable()"),
            (Function, "inline ppu_ctl1_assign( newctl )"),
            (Function, "inline ppu_ctl1_set( mask )"),
            (Function, "inline ppu_ctl1_clear( mask )"),
            (Function, "inline ppu_ctl1_adjust( clearmask, setmask )"),
            (Function, "inline ppu_ctl1_test( mask )"),
            (Function, "inline ppu_set_palette_intensity( newbits )"),
            (Function, "inline vblank_wait()"),
            (Function, "inline vblank_wait_full()"),
            (Function, "inline vblank_wait_for( amount )"),
            (Function, "inline unvblank_wait()"),
            (Function, "inline test_scanline()"),
            (Function, "inline ppu_clean_latch()"),
            (Function, "inline vram_clear_address()"),
            (Function, "inline vram_set_address( newaddress )"),
            (Function, "inline vram_set_address_i( newaddress )"),
            (Function, "inline vram_set_scroll( x, y )"),
            (Function, "inline vram_write( value )"),
            (Function, "inline vram_write_ind( value )"),
            (Function, "inline vram_write_x( value )"),
            (Function, "inline vram_write_ind_y( value )"),
            (Function, "inline vram_write_a()"),
            (Function, "inline vram_write_regx()"),
            (Function, "inline vram_write_16( value )"),
            (Function, "inline vram_write_16_i( value )"),
            (Function, "inline vram_read( dest )"),
            (Function, "inline vram_ind_read( dest )"),
            (Function, "inline vram_ind_y_read( dest )"),
            (Function, "inline vram_read_a()"),
            (Function, "inline vram_read_16( dest )"),
            (Function, "inline vram_set_sprite_address( newaddress )"),
            (Function, "inline vram_set_sprite_address_i( newaddress )"),
            (Function, "inline vram_set_sprite_data( x, y, tile, attributes )"),
            (Function, "inline vram_sprite_dma_copy( oamptr )"),
            (Variable, "byte JOYSTICK_CNT0 :$4016"),
            (Variable, "byte JOYSTICK_CNT1 :$4017"),
            (Enum, "enum JOYSTICK"),
            (Function, "inline reset_joystick()"),
            (Function, "inline read_joystick0()"),
            (Function, "inline read_joystick1()"),
            (Function, "inline test_joystick1( buttonmask )"),
            (Function, "inline test_joystick1_prev( buttonmask )"),
            (Function, "inline test_button_release( buttonmask )"),
            (Function, "inline test_button_press( buttonmask )"),
            (Variable, "byte SQUAREWAVEA_CNT0 :$4000"),
            (Variable, "byte SQUAREWAVEA_CNT1 :$4001"),
            (Variable, "byte SQUAREWAVEA_FREQ0 :$4002"),
            (Variable, "byte SQUAREWAVEA_FREQ1 :$4003"),
            (Enum, "enum SQUAREWAVEA"),
            (Variable, "byte SQUAREWAVEB_CNT0 :$4004"),
            (Variable, "byte SQUAREWAVEB_CNT1 :$4005"),
            (Variable, "byte SQUAREWAVEB_FREQ0 :$4006"),
            (Variable, "byte SQUAREWAVEB_FREQ1 :$4007"),
            (Enum, "enum SQUAREWAVEB"),
            (Variable, "byte TRIANGLEWAVE_CNT0 :$4008"),
            (Variable, "byte TRIANGLEWAVE_CNT1 :$4009"),
            (Variable, "byte TRIANGLEWAVE_FREQ0 :$400A"),
            (Variable, "byte TRIANGLEWAVE_FREQ1 :$400B"),
            (Enum, "enum TRIANGLEWAVE"),
            (Variable, "byte NOISE_CNT0 :$400C"),
            (Variable, "byte NOISE_CNT1 :$400D"),
            (Variable, "byte NOISE_FREQ0 :$400E"),
            (Variable, "byte NOISE_FREQ1 :$400F"),
            (Variable, "byte PCM_CNT :$4010"),
            (Variable, "byte PCM_VOLUMECNT :$4011"),
            (Variable, "byte PCM_ADDRESS :$4012"),
            (Variable, "byte PCM_LENGTH :$4013"),
            (Variable, "byte SND_CNT :$4015"),
            (Enum, "enum SNDENABLE"),
            (Enum, "enum MMC5"),
            (Function, "inline mmc5_init()"),
            (Function, "inline mmc5_select_prg_8000_a()"),
            (Function, "inline mmc5_select_prg_8000( number )"),
            (Function, "inline mmc5_select_prg_8000i( number )"),
            (Function, "inline mmc5_save_prg_A000_bank_number()"),
            (Function, "inline mmc5_select_prg_A000_a()"),
            (Function, "inline mmc5_select_prg_A000( number )"),
            (Function, "inline mmc5_select_prg_A000i_raw( number )"),
            (Function, "inline mmc5_select_prg_A000i( number )"),
            (Function, "inline mmc5_select_prg_A000i_push( number )"),
            (Function, "inline mmc5_select_prg_A000_x_push( var )"),
            (Function, "inline mmc5_select_prg_A000_push( var )"),
            (Function, "inline mmc5_restore_prg_A000_pop()"),
            (Function, "inline mmc5_restore_prg_A000( number )"),
            (Function, "inline mmc5_select_prg_C000_a()"),
            (Function, "inline mmc5_select_prg_C000( number )"),
            (Function, "inline mmc5_select_prg_C000i( number )"),
            (Function, "inline mmc5_select_prg_E000_a()"),
            (Function, "inline mmc5_select_prg_E000( number )"),
            (Function, "inline mmc5_select_prg_E000i( number )"),
            (Function, "inline mmc5_multiply( valueA, valueB )"),
            (Function, "inline assign( dest, value )"),
            (Function, "inline assign_x( dest, value )"),
            (Function, "inline x_assign_x( dest, src )"),
            (Function, "inline x_assign_y( dest, src )"),
            (Function, "inline assign_y( dest, value )"),
            (Function, "inline x_assign( dest, src )"),
            (Function, "inline y_assign( dest, src )"),
            (Function, "inline assign_ind( dest, value )"),
            (Function, "inline assign_ind_y( dest, value )"),
            (Function, "inline ind_x_assign( dest, src )"),
            (Function, "inline ind_y_assign( dest, src )"),
            (Function, "inline assign_16_8( dest, value )"),
            (Function, "inline assign_16_8_x( dest, value )"),
            (Function, "inline assign_16_8_y( dest, value )"),
            (Function, "inline assign_16_16( dest, value )"),
            (Function, "inline assign_16_16_x( dest, value )"),
            (Function, "inline y_assign_16_16_x( dest, value )"),
            (Function, "inline assign_16_16_y( dest, value )"),
            (Function, "inline ind_assign_16_16_x( dest, value )"),
            (Function, "inline x_assign_16_16( dest, value )"),
            (Function, "inline x_assign_16_16_x( dest, value )"),
            (Function, "inline y_ind_assign_16_16( dest, value )"),
            (Function, "inline y_assign_16_16( dest, value )"),
            (Function, "inline assign_16i( dest, value )"),
            (Function, "inline assign_16i_x( dest, value )"),
            (Function, "inline assign_16i_y( dest, value )"),
            (Function, "inline zero_16( dest )"),
            (Function, "inline zero_32( dest )"),
            (Function, "inline zero_16_x( dest )"),
            (Function, "inline zero_16_y( dest )"),
            (Function, "inline tyx()"),
            (Function, "inline txy()"),
            (Function, "inline test( dest, mask )"),
            (Function, "inline test_x( dest, mask )"),
            (Function, "inline test_16_8( dest, mask )"),
            (Function, "inline test_16_16( dest, mask )"),
            (Function, "inline test_16i( dest, mask )"),
            (Function, "inline or( dest, mask )"),
            (Function, "inline or_x_a( dest )"),
            (Function, "inline or_x( dest, mask )"),
            (Function, "inline or_y_a( dest )"),
            (Function, "inline or_y( dest, mask )"),
            (Function, "inline or_16_8( dest, mask )"),
            (Function, "inline or_16_8_x( dest, mask )"),
            (Function, "inline or_16_16( dest, mask )"),
            (Function, "inline or_16_16_x( dest, mask )"),
            (Function, "inline or_16i( dest, mask )"),
            (Function, "inline or_16i_x( dest, mask )"),
            (Function, "inline xor( dest, mask )"),
            (Function, "inline xor_x( dest, mask )"),
            (Function, "inline xor_16_8( dest, mask )"),
            (Function, "inline xor_16_8_x( dest, mask )"),
            (Function, "inline xor_16_16( dest, mask )"),
            (Function, "inline xor_16_16_x( dest, mask )"),
            (Function, "inline xor_16i( dest, mask )"),
            (Function, "inline xor_16i_x( dest, mask )"),
            (Function, "inline and_8( dest, mask )"),
            (Function, "inline and_x( dest, mask )"),
            (Function, "inline and_y( dest, mask )"),
            (Function, "inline and_16_8( dest, mask )"),
            (Function, "inline and_16_8_x( dest, mask )"),
            (Function, "inline and_16_16( dest, mask )"),
            (Function, "inline and_16_16_x( dest, mask )"),
            (Function, "inline and_16i( dest, mask )"),
            (Function, "inline and_16i_x( dest, mask )"),
            (Function, "inline and_or( dest, and_mask, or_mask )"),
            (Function, "inline add( dest, value )"),
            (Function, "inline add_x( dest, value )"),
            (Function, "inline y_add( dest, value )"),
            (Function, "inline add_x_a( dest )"),
            (Function, "inline add_16_8_a( dest )"),
            (Function, "inline adds_16_8_a( dest )"),
            (Function, "inline add_16_8_a_x( dest )"),
            (Function, "inline adds_16_8_a_x( dest )"),
            (Function, "inline adds_16_8_a_x_to( src, dest )"),
            (Function, "inline add_16_8( dest, value )"),
            (Function, "inline adds_16_8( dest, value )"),
            (Function, "inline add_16_8_to( src, value, dest )"),
            (Function, "inline add_16_8yind_to( src, value, dest )"),
            (Function, "inline adds_16_8yind_to( src, value, dest )"),
            (Function, "inline add_16_8_a_to_x( src, dest )"),
            (Function, "inline add_16_8_x( dest, value )"),
            (Function, "inline adds_16_8_x( dest, value )"),
            (Function, "inline add_16_16( dest, value )"),
            (Function, "inline add_16_16_x( dest, value )"),
            (Function, "inline x_add_16_8_to( dest, value, src )"),
            (Function, "inline add_8y_16x_to_16( var8, var16, dest16 )"),
            (Function, "inline x_sub_16_8_to( dest, value, src )"),
            (Function, "inline add_16i( dest, value )"),
            (Function, "inline add_16i_x( dest, value )"),
            (Function, "inline sub( dest, value )"),
            (Function, "inline sub_x( dest, value )"),
            (Function, "inline sub_16_8_a( dest )"),
            (Function, "inline sub_16_8_a_to( value, dest )"),
            (Function, "inline sub_16_8_a_x( dest )"),
            (Function, "inline x_sub_16_8_a_to( value, dest )"),
            (Function, "inline y_sub_16_8_a_to( value, dest )"),
            (Function, "inline sub_16_8( dest, value )"),
            (Function, "inline sub_16_8_to( src, value, dest )"),
            (Function, "inline sub_16_8_x( dest, value )"),
            (Function, "inline sub_16_16( dest, value )"),
            (Function, "inline sub_16_16_to( valuea, valueb, dest )"),
            (Function, "inline add_16_16_to( valuea, valueb, dest )"),
            (Function, "inline sub16_16_x( dest, value )"),
            (Function, "inline sub_16i( dest, value )"),
            (Function, "inline sub_16i_x( dest, value )"),
            (Function, "inline mul_a( dest, multipiler )"),
            (Function, "inline mul_x_a( dest, multipiler )"),
            (Function, "inline mul( dest, multipiler )"),
            (Function, "inline mul_x( dest, multipiler )"),
            (Function, "inline mul_16_8( dest, multipiler )"),
            (Function, "inline mul_16_8_x( dest, multipiler )"),
            (Function, "inline asl2_a()"),
            (Function, "inline asl3_a()"),
            (Function, "inline asl4_a()"),
            (Function, "inline asl5_a()"),
            (Function, "inline asl6_a()"),
            (Function, "inline asl7_a()"),
            (Function, "inline asl_16_1( dest )"),
            (Function, "inline asl_16( dest, amount )"),
            (Function, "inline asl_16_to( dest, src, amount )"),
            (Function, "inline asl_8_to_16( dest, src, amount )"),
            (Function, "inline asl2_8_a_to_16( dest )"),
            (Function, "inline lsr2_a()"),
            (Function, "inline lsr3_a()"),
            (Function, "inline lsr4_a()"),
            (Function, "inline lsr5_a()"),
            (Function, "inline lsr6_a()"),
            (Function, "inline lsr7_a()"),
            (Function, "inline lsr_16( dest, amount )"),
            (Function, "inline lsr_16_to( dest, src, amount )"),
            (Function, "inline lsr_16_by_6_to_8( dest, src )"),
            (Function, "inline lsr_16_by_5_to_8( dest, src )"),
            (Function, "inline lsr_16_by_4_to_8( dest, src )"),
            (Function, "inline lsr_16_by_3_to_8( dest, src )"),
            (Function, "inline lsr_16_by_2_to_8( dest, src )"),
            (Function, "inline div( dest, amount )"),
            (Function, "inline div_with_rem( dest, amount )"),
            (Function, "inline div_16_8_to_x( dest, amount )"),
            (Function, "inline mod_16_by_240_to_8( dest, src )"),
            (Function, "inline mod_16_to_8( dest, src, val )"),
            (Function, "inline abs_a()"),
            (Function, "inline abs( number )"),
            (Function, "inline abs_16( number )"),
            (Function, "inline neg_a()"),
            (Function, "inline neg( number )"),
            (Function, "inline neg_16( number )"),
            (Function, "inline inc_16( number )"),
            (Function, "inline inc_16_limit( number )"),
            (Function, "inline inc_16_x( number )"),
            (Function, "inline dec_16( number )"),
            (Function, "inline dec_16_x( number )"),
            (Function, "inline clip_16( number )"),
            (Function, "inline compare( src, value )"),
            (Function, "inline compare_x( src, value )"),
            (Function, "inline x_compare_x( src, value )"),
            (Function, "inline compare_16_16( src, value )"),
            (Function, "inline compare_16_16_x( src, value )"),
            (Function, "inline compare_16_x_16_x( src, value )"),
            (Function, "inline compare_16_y_16_x( src, value )"),
            (Function, "inline compare_8_y_8_x( src, value )"),
            (Function, "inline compare_16_x_16_y( src, value )"),
            (Function, "inline compare_8_x_8_y( src, value )"),
            (Function, "inline compare_8_x_8_x( src, value )"),
            (Function, "inline compare_8_x_8( src, value )"),
            (Function, "inline compare_8_y_8_y( src, value )"),
            (Function, "inline compare_16_16_y( src, value )"),
            (Function, "inline compare_16i( src, value )"),
            (Function, "inline pusha()"),
            (Function, "inline popa()"),
            (Function, "inline toss16()"),
            (Function, "inline push( value )"),
            (Function, "inline push_x( src )"),
            (Function, "inline push_16( src )"),
            (Function, "inline push_16_x( src )"),
            (Function, "inline pop( dest )"),
            (Function, "inline pop_x( dest )"),
            (Function, "inline pop_16( dest )"),
            (Function, "inline pop_16_x( dest )"),
            (Function, "inline peek()"),
            (Function, "inline pushx()"),
            (Function, "inline popx()"),
            (Function, "inline peekx()"),
            (Function, "inline pushy()"),
            (Function, "inline popy()"),
            (Function, "inline peeky()"),
            (Function, "inline pushp()"),
            (Function, "inline popp()"),
            (Function, "inline pushsp()"),
            (Function, "inline popsp()"),
            (Function, "inline push_all()"),
            (Function, "inline pop_all()"),
            (Function, "inline memcpy_inline( dest, src, size )"),
            (Function, "inline memset_inline( memdest, value, memsize )"),
            (Enum, "enum COLOUR"),
            (Variable, "byte _b_temp"),
            (Variable, "word _w_temp"),
            (Variable, "pointer _p_temp"),
            (Variable, "pointer _jsrind_temp"),
            (Variable, "byte _b_remainder"),
            (Variable, "byte _random_value"),
            (Variable, "byte _random_ticks"),
            (Variable, "pointer _mem_src"),
            (Variable, "pointer _mem_dest"),
            (Variable, "byte counter"),
            (Variable, "byte palcol"),
            (Variable, "pointer paddr"),
            (Variable, "pointer pstr"),
            (Variable, "char msgbuf[64]"),
            (Function, "function Turn_Video_On()"),
            (Function, "function Turn_Video_Off()"),
            (Function, "function vram_write_hex_a()"),
            (Function, "inline vram_write_string_inl( addr, str )"),
            (Function, "function vram_write_string()"),
            (Variable, "byte setamt[]"),
            (Function, "function vram_init()"),
            (Function, "function palette_memset()"),
            (Function, "inline palette_memset_inl( col )"),
            (Function, "function pal_animate()"),
            (Function, "function pal_animate2()"),
            (Function, "inline wait_for( amount )"),
            (Function, "function wait_for_func()"),
            (Function, "function message_error()"),
            (Variable, "char strTitle[]"),
            (Variable, "char strHello[]"),
            (Function, "inline custom_system_initialize()"),
            (Function, "interrupt.irq int_irq()"),
            (Function, "interrupt.nmi int_nmi()"),
            (Function, "interrupt.start main()"),
            (Function, "function jsr_ind()")
        ]
        resolver = [
            (Label, "ENABLE_INTERRUPT"),
            (InstructionLine, "cli"),
            (Label, "DISABLE_INTERRUP"),
            (InstructionLine, "sei"),
            (Label, "ENABLE_DECIMAL_M"),
            (InstructionLine, "sei"),
            (Label, "DISABLE_DECIMAL_"),
            (InstructionLine, "cld"),
            (Label, "SET_CARRY_FLAG"),
            (InstructionLine, "sec"),
            (Label, "CLEAR_CARRY_FLAG"),
            (InstructionLine, "clc"),
            (Label, "RESET_STACK"),
            (InstructionLine, "ldx #0xFF"),
            (InstructionLine, "txs"),
            (Label, "NES_RESET"),
            (InstructionLine, "jmp $FFFC"),
            (Label, "SYSTEM_INITIALIZ"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta PPU.CNT0"),
            (InstructionLine, "sta PPU.CNT1"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (InstructionLine, "sta $4010"),
            (InstructionLine, "sta $4011"),
            (InstructionLine, "sta $4015"),
            (InstructionLine, "lda #0xC0"),
            (InstructionLine, "sta joystick.cnt1"),
            (Enum, "enum PPU"),
            (Typedef, "typedef struct OAM_ENTRY_"),
            (Typedef, "typedef struct PALENT_"),
            (Typedef, "typedef struct PALETTE_"),
            (Label, "PPU_CTL0_ASSIGN"),
            (InstructionLine, "lda newctl"),
            (InstructionLine, "sta _ppu_ctl0"),
            (InstructionLine, "sta PPU.CNT0"),
            (Label, "PPU_CTL0_SET"),
            (InstructionLine, "lda _ppu_ctl0"),
            (InstructionLine, "ora #mask"),
            (InstructionLine, "sta _ppu_ctl0"),
            (InstructionLine, "sta PPU.CNT0"),
            (Label, "PPU_CTL0_CLEAR"),
            (InstructionLine, "lda _ppu_ctl0"),
            (InstructionLine, "and #~(mask)"),
            (InstructionLine, "sta _ppu_ctl0"),
            (InstructionLine, "sta PPU.CNT0"),
            (Label, "PPU_CTL0_ADJUST"),
            (InstructionLine, "lda _ppu_ctl0"),
            (InstructionLine, "and #~(clearmask)"),
            (InstructionLine, "ora #setmask"),
            (InstructionLine, "sta _ppu_ctl0"),
            (InstructionLine, "sta PPU.CNT0"),
            (Label, "PPU_CTL0_XOR"),
            (InstructionLine, "lda _ppu_ctl0"),
            (InstructionLine, "eor #mask"),
            (InstructionLine, "sta _ppu_ctl0"),
            (InstructionLine, "sta PPU.CNT0"),
            (Label, "PPU_CTL0_TEST"),
            (InstructionLine, "lda mask"),
            (InstructionLine, "bit _ppu_ctl0"),
            (Label, "PPU_ENABLE_NMI"),
            (Label, "PPU_DISABLE_NMI"),
            (Label, "PPU_TURN_OFF"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (Label, "PPU_TURN_ON_DRAW"),
            (Label, "PPU_TURN_OFF_DRA"),
            (Label, "PPU_SET_NAMETABL"),
            (Label, "PPU_XOR_NAMETABL"),
            (Label, "PPU_CTL1_ASSIGN"),
            (InstructionLine, "lda newctl"),
            (InstructionLine, "sta _ppu_ctl1"),
            (InstructionLine, "sta PPU.CNT1"),
            (Label, "PPU_CTL1_SET"),
            (InstructionLine, "lda _ppu_ctl1"),
            (InstructionLine, "ora #mask"),
            (InstructionLine, "sta _ppu_ctl1"),
            (InstructionLine, "sta PPU.CNT1"),
            (Label, "PPU_CTL1_CLEAR"),
            (InstructionLine, "lda _ppu_ctl1"),
            (InstructionLine, "and #~(mask)"),
            (InstructionLine, "sta _ppu_ctl1"),
            (InstructionLine, "sta PPU.CNT1"),
            (Label, "PPU_CTL1_ADJUST"),
            (InstructionLine, "lda _ppu_ctl1"),
            (InstructionLine, "and #~(clearmask)"),
            (InstructionLine, "ora #setmask"),
            (InstructionLine, "sta _ppu_ctl1"),
            (InstructionLine, "sta PPU.CNT1"),
            (Label, "PPU_CTL1_TEST"),
            (InstructionLine, "lda mask"),
            (InstructionLine, "bit _ppu_ctl1"),
            (Label, "PPU_SET_PALETTE_"),
            (Label, "VBLANK_WAIT"),
            (Label, "HLA0"),
            (InstructionLine, "lda PPU.STATUS"),
            (InstructionLine, "bpl HLA0"),
            (Label, "VBLANK_WAIT_FULL"),
            (Label, "VBLANK_WAIT_FOR"),
            (InstructionLine, "ldx amount"),
            (Label, "HLA1"),
            (InstructionLine, "dex"),
            (InstructionLine, "bne HLA1"),
            (Label, "UNVBLANK_WAIT"),
            (Label, "HLA2"),
            (InstructionLine, "lda PPU.STATUS"),
            (InstructionLine, "bmi HLA2"),
            (Label, "TEST_SCANLINE"),
            (InstructionLine, "lda PPU.STATUS"),
            (InstructionLine, "and #%00100000"),
            (Label, "PPU_CLEAN_LATCH"),
            (InstructionLine, "lda PPU.STATUS"),
            (Label, "VRAM_CLEAR_ADDRE"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (Label, "VRAM_SET_ADDRESS"),
            (InstructionLine, "lda +([newaddress], 1)"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (InstructionLine, "lda +([newaddress], 0)"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (Label, "VRAM_SET_ADDRESS"),
            (InstructionLine, "lda #hi(newaddress)"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (InstructionLine, "lda #lo(newaddress)"),
            (InstructionLine, "sta PPU.ADDRESS"),
            (Label, "VRAM_SET_SCROLL"),
            (Label, "VRAM_WRITE"),
            (Label, "VRAM_WRITE_IND"),
            (Label, "VRAM_WRITE_X"),
            (Label, "VRAM_WRITE_IND_Y"),
            (Label, "VRAM_WRITE_A"),
            (InstructionLine, "sta PPU.IO"),
            (Label, "VRAM_WRITE_REGX"),
            (InstructionLine, "stx PPU.IO"),
            (Label, "VRAM_WRITE_16"),
            (Label, "VRAM_WRITE_16_I"),
            (Label, "VRAM_READ"),
            (Label, "VRAM_IND_READ"),
            (Label, "VRAM_IND_Y_READ"),
            (Label, "VRAM_READ_A"),
            (InstructionLine, "lda PPU.IO"),
            (Label, "VRAM_READ_16"),
            (Label, "VRAM_SET_SPRITE_"),
            (Label, "VRAM_SET_SPRITE_"),
            (Label, "VRAM_SET_SPRITE_"),
            (Label, "VRAM_SPRITE_DMA_"),
            (Variable, "byte JOYSTICK_CNT0 :$4016"),
            (Variable, "byte JOYSTICK_CNT1 :$4017"),
            (Enum, "enum JOYSTICK"),
            (Label, "RESET_JOYSTICK"),
            (Label, "READ_JOYSTICK0"),
            (InstructionLine, "lda JOYSTICK.CNT0"),
            (InstructionLine, "and #1"),
            (Label, "READ_JOYSTICK1"),
            (InstructionLine, "lda JOYSTICK.CNT1"),
            (InstructionLine, "and #1"),
            (Label, "TEST_JOYSTICK1"),
            (InstructionLine, "lda _joypad"),
            (InstructionLine, "and buttonmask"),
            (Label, "TEST_JOYSTICK1_P"),
            (InstructionLine, "lda _joypad_prev"),
            (InstructionLine, "and buttonmask"),
            (Label, "TEST_BUTTON_RELE"),
            (InstructionLine, "beq HLA3"),
            (Label, "HLA3"),
            (InstructionLine, "eor #0xFF"),
            (Label, "TEST_BUTTON_PRES"),
            (InstructionLine, "bne HLA4"),
            (InstructionLine, "eor #0xFF"),
            (Label, "HLA4"),
            (Variable, "byte SQUAREWAVEA_CNT0 :$4000"),
            (Variable, "byte SQUAREWAVEA_CNT1 :$4001"),
            (Variable, "byte SQUAREWAVEA_FREQ0 :$4002"),
            (Variable, "byte SQUAREWAVEA_FREQ1 :$4003"),
            (Enum, "enum SQUAREWAVEA"),
            (Variable, "byte SQUAREWAVEB_CNT0 :$4004"),
            (Variable, "byte SQUAREWAVEB_CNT1 :$4005"),
            (Variable, "byte SQUAREWAVEB_FREQ0 :$4006"),
            (Variable, "byte SQUAREWAVEB_FREQ1 :$4007"),
            (Enum, "enum SQUAREWAVEB"),
            (Variable, "byte TRIANGLEWAVE_CNT0 :$4008"),
            (Variable, "byte TRIANGLEWAVE_CNT1 :$4009"),
            (Variable, "byte TRIANGLEWAVE_FREQ0 :$400A"),
            (Variable, "byte TRIANGLEWAVE_FREQ1 :$400B"),
            (Enum, "enum TRIANGLEWAVE"),
            (Variable, "byte NOISE_CNT0 :$400C"),
            (Variable, "byte NOISE_CNT1 :$400D"),
            (Variable, "byte NOISE_FREQ0 :$400E"),
            (Variable, "byte NOISE_FREQ1 :$400F"),
            (Variable, "byte PCM_CNT :$4010"),
            (Variable, "byte PCM_VOLUMECNT :$4011"),
            (Variable, "byte PCM_ADDRESS :$4012"),
            (Variable, "byte PCM_LENGTH :$4013"),
            (Variable, "byte SND_CNT :$4015"),
            (Enum, "enum SNDENABLE"),
            (Enum, "enum MMC5"),
            (Label, "MMC5_INIT"),
            (InstructionLine, "lda #MMC5.GRAPHMODE_EXGRAPHIC"),
            (InstructionLine, "sta MMC5.GRAPHICS_MODE"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta MMC5.SPLIT_CNT"),
            (InstructionLine, "sta MMC5.SOUND_CH_OUTPUT"),
            (InstructionLine, "sta MMC5.SOUND_CH3_VOICE_CH"),
            (InstructionLine, "ldx #0"),
            (InstructionLine, "stx MMC5.BGCHR_BANK_SELECT_2K_0000"),
            (InstructionLine, "inx"),
            (InstructionLine, "stx MMC5.BGCHR_BANK_SELECT_2K_0800"),
            (InstructionLine, "inx"),
            (InstructionLine, "stx MMC5.BGCHR_BANK_SELECT_2K_1000"),
            (InstructionLine, "inx"),
            (InstructionLine, "stx MMC5.BGCHR_BANK_SELECT_2K_1800"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_8000"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "lda number"),
            (Label, "MMC5_SELECT_PRG_"),
            (Label, "MMC5_SAVE_PRG_A0"),
            (InstructionLine, "pha"),
            (InstructionLine, "pla"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "lda number"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "lda #|([number], [MMC5, SELECT_PRG_ACTIVATE])"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (Label, "MMC5_SELECT_PRG_"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "lda pBankA000_cur"),
            (InstructionLine, "pha"),
            (InstructionLine, "lda #|([number], [MMC5, SELECT_PRG_ACTIVATE])"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "lda pBankA000_cur"),
            (InstructionLine, "pha"),
            (InstructionLine, "lda"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "lda pBankA000_cur"),
            (InstructionLine, "pha"),
            (InstructionLine, "lda var"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (Label, "MMC5_RESTORE_PRG"),
            (InstructionLine, "pla"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (Label, "MMC5_RESTORE_PRG"),
            (InstructionLine, "lda pBankA000_prev"),
            (InstructionLine, "sta pBankA000_cur"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_A000"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_C000"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "lda number"),
            (Label, "MMC5_SELECT_PRG_"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "ora #MMC5.SELECT_PRG_ACTIVATE"),
            (InstructionLine, "sta MMC5.PRG_BANK_SELECT_E000"),
            (Label, "MMC5_SELECT_PRG_"),
            (InstructionLine, "lda number"),
            (Label, "MMC5_SELECT_PRG_"),
            (Label, "MMC5_MULTIPLY"),
            (Label, "ASSIGN"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta dest"),
            (Label, "ASSIGN_X"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta"),
            (Label, "X_ASSIGN_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (Label, "X_ASSIGN_Y"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (Label, "ASSIGN_Y"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta"),
            (Label, "X_ASSIGN"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta dest"),
            (Label, "Y_ASSIGN"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta dest"),
            (Label, "ASSIGN_IND"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta dest"),
            (Label, "ASSIGN_IND_Y"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta (dest), y"),
            (Label, "IND_X_ASSIGN"),
            (InstructionLine, "lda (src, x)"),
            (InstructionLine, "sta dest"),
            (Label, "IND_Y_ASSIGN"),
            (InstructionLine, "lda (src), y"),
            (InstructionLine, "sta dest"),
            (Label, "ASSIGN_16_8"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ASSIGN_16_8_X"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta"),
            (Label, "ASSIGN_16_8_Y"),
            (InstructionLine, "lda value"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta"),
            (Label, "ASSIGN_16_16"),
            (InstructionLine, "lda +([value], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([value], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ASSIGN_16_16_X"),
            (InstructionLine, "lda +([value], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([value], 1)"),
            (InstructionLine, "sta"),
            (Label, "Y_ASSIGN_16_16_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (Label, "ASSIGN_16_16_Y"),
            (InstructionLine, "lda +([value], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([value], 1)"),
            (InstructionLine, "sta"),
            (Label, "IND_ASSIGN_16_16"),
            (InstructionLine, "ldy #0"),
            (InstructionLine, "lda (value), y"),
            (InstructionLine, "sta"),
            (InstructionLine, "iny"),
            (InstructionLine, "lda (value), y"),
            (InstructionLine, "sta"),
            (Label, "X_ASSIGN_16_16"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "X_ASSIGN_16_16_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (Label, "Y_IND_ASSIGN_16_"),
            (InstructionLine, "lda (value), y"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "iny"),
            (InstructionLine, "lda (value), y"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "Y_ASSIGN_16_16"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ASSIGN_16I"),
            (InstructionLine, "lda #lo(value)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda #hi(value)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ASSIGN_16I_X"),
            (InstructionLine, "lda #lo(value)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda #hi(value)"),
            (InstructionLine, "sta"),
            (Label, "ASSIGN_16I_Y"),
            (InstructionLine, "lda #lo(value)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda #hi(value)"),
            (InstructionLine, "sta"),
            (Label, "ZERO_16"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ZERO_32"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "sta +([dest], 1)"),
            (InstructionLine, "sta +([dest], 2)"),
            (InstructionLine, "sta +([dest], 3)"),
            (Label, "ZERO_16_X"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta"),
            (InstructionLine, "sta"),
            (Label, "ZERO_16_Y"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta"),
            (InstructionLine, "sta"),
            (Label, "TYX"),
            (InstructionLine, "tya"),
            (InstructionLine, "tax"),
            (Label, "TXY"),
            (InstructionLine, "txa"),
            (InstructionLine, "tay"),
            (Label, "TEST"),
            (InstructionLine, "lda mask"),
            (InstructionLine, "bit dest"),
            (Label, "TEST_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "and mask"),
            (Label, "TEST_16_8"),
            (InstructionLine, "lda +([mask], 0)"),
            (InstructionLine, "bit +([dest], 0)"),
            (Label, "TEST_16_16"),
            (InstructionLine, "lda +([mask], 0)"),
            (InstructionLine, "bit +([dest], 0)"),
            (InstructionLine, "beq HLA5"),
            (InstructionLine, "lda +([mask], 1)"),
            (InstructionLine, "bit +([dest], 1)"),
            (Label, "HLA5"),
            (Label, "TEST_16I"),
            (InstructionLine, "lda #lo(mask)"),
            (InstructionLine, "bit +([dest], 0)"),
            (InstructionLine, "beq HLA6"),
            (InstructionLine, "lda #hi(mask)"),
            (InstructionLine, "bit +([dest], 1)"),
            (Label, "HLA6"),
            (Label, "OR"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "ora mask"),
            (InstructionLine, "sta dest"),
            (Label, "OR_X_A"),
            (InstructionLine, "ora"),
            (InstructionLine, "sta"),
            (Label, "OR_X"),
            (InstructionLine, "lda mask"),
            (Label, "OR_Y_A"),
            (InstructionLine, "ora"),
            (InstructionLine, "sta"),
            (Label, "OR_Y"),
            (InstructionLine, "lda mask"),
            (Label, "OR_16_8"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "ora mask"),
            (InstructionLine, "sta +([dest], 0)"),
            (Label, "OR_16_8_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "ora mask"),
            (InstructionLine, "sta"),
            (Label, "OR_16_16"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "ora +([mask], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "ora +([mask], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "OR_16_16_X"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "ora +([mask], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "ora +([mask], 1)"),
            (InstructionLine, "sta"),
            (Label, "OR_16I"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "ora #lo(mask)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "ora #hi(mask)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "OR_16I_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "ora #lo(mask)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "ora #hi(mask)"),
            (InstructionLine, "sta"),
            (Label, "XOR"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "eor mask"),
            (InstructionLine, "sta dest"),
            (Label, "XOR_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "eor mask"),
            (InstructionLine, "sta"),
            (Label, "XOR_16_8"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "eor mask"),
            (InstructionLine, "sta +([dest], 0)"),
            (Label, "XOR_16_8_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "eor mask"),
            (InstructionLine, "sta"),
            (Label, "XOR_16_16"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "eor +([mask], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "eor +([mask], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "XOR_16_16_X"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "eor +([mask], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "eor +([mask], 1)"),
            (InstructionLine, "sta"),
            (Label, "XOR_16I"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "eor #lo(mask)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "eor #hi(mask)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "XOR_16I_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "eor #lo(mask)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "eor #hi(mask)"),
            (InstructionLine, "sta"),
            (Label, "AND_8"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "and mask"),
            (InstructionLine, "sta dest"),
            (Label, "AND_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "and mask"),
            (InstructionLine, "sta"),
            (Label, "AND_Y"),
            (InstructionLine, "lda"),
            (InstructionLine, "and mask"),
            (InstructionLine, "sta"),
            (Label, "AND_16_8"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "and mask"),
            (InstructionLine, "sta +([dest], 0)"),
            (Label, "AND_16_8_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "and mask"),
            (InstructionLine, "sta"),
            (Label, "AND_16_16"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "and +([mask], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "and +([mask], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "AND_16_16_X"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "and +([mask], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "and +([mask], 1)"),
            (InstructionLine, "sta"),
            (Label, "AND_16I"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "and #lo(mask)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "and #hi(mask)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "AND_16I_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "and #lo(mask)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "and #hi(mask)"),
            (InstructionLine, "sta"),
            (Label, "AND_OR"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "and and_mask"),
            (InstructionLine, "ora or_mask"),
            (InstructionLine, "sta dest"),
            (Label, "ADD"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta dest"),
            (Label, "ADD_X"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta"),
            (Label, "Y_ADD"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta dest"),
            (Label, "ADD_X_A"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta"),
            (Label, "ADD_16_8_A"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc dest"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ADDS_16_8_A"),
            (InstructionLine, "bmi HLA7"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc dest"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (InstructionLine, "jmp HLA8"),
            (Label, "HLA7"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc dest"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "adc #0xFF"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "HLA8"),
            (Label, "ADD_16_8_A_X"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta"),
            (Label, "ADDS_16_8_A_X"),
            (InstructionLine, "bmi HLA9"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "jmp HLA10"),
            (Label, "HLA9"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0xFF"),
            (Label, "HLA10"),
            (InstructionLine, "sta"),
            (Label, "ADDS_16_8_A_X_TO"),
            (InstructionLine, "bmi HLA11"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (InstructionLine, "jmp HLA12"),
            (Label, "HLA11"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0xFF"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "HLA12"),
            (Label, "ADD_16_8"),
            (InstructionLine, "lda value"),
            (Label, "ADDS_16_8"),
            (InstructionLine, "lda value"),
            (Label, "ADD_16_8_TO"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ADD_16_8YIND_TO"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "adc (value), y"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ADDS_16_8YIND_TO"),
            (InstructionLine, "lda (value), y"),
            (InstructionLine, "bmi HLA13"),
            (InstructionLine, "ldx #0"),
            (InstructionLine, "jmp HLA14"),
            (Label, "HLA13"),
            (InstructionLine, "ldx #0xFF"),
            (Label, "HLA14"),
            (InstructionLine, "stx btemp"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc +([src], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "adc btemp"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ADD_16_8_A_TO_X"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc +([src], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta"),
            (Label, "ADD_16_8_X"),
            (InstructionLine, "lda value"),
            (Label, "ADDS_16_8_X"),
            (InstructionLine, "lda value"),
            (Label, "ADD_16_16"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "adc +([value], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ADD_16_16_X"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc +([value], 1)"),
            (InstructionLine, "sta"),
            (Label, "X_ADD_16_8_TO"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ADD_8Y_16X_TO_16"),
            (InstructionLine, "lda"),
            (InstructionLine, "bpl HLA15"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta +([dest16], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0xFF"),
            (InstructionLine, "jmp HLA16"),
            (Label, "HLA15"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc"),
            (InstructionLine, "sta +([dest16], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #0"),
            (Label, "HLA16"),
            (InstructionLine, "sta +([dest16], 1)"),
            (Label, "X_SUB_16_8_TO"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ADD_16I"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "adc #lo(value)"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "adc #hi(value)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ADD_16I_X"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #lo(value)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "adc #hi(value)"),
            (InstructionLine, "sta"),
            (Label, "SUB"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta dest"),
            (Label, "SUB_X"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta"),
            (Label, "SUB_16_8_A"),
            (InstructionLine, "sec"),
            (InstructionLine, "sta _b_temp"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "sbc _b_temp"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "SUB_16_8_A_TO"),
            (InstructionLine, "sec"),
            (InstructionLine, "sta _b_temp"),
            (InstructionLine, "lda +([value], 0)"),
            (InstructionLine, "sbc _b_temp"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([value], 1)"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "SUB_16_8_A_X"),
            (InstructionLine, "sec"),
            (InstructionLine, "sta _b_temp"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc _b_temp"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta"),
            (Label, "X_SUB_16_8_A_TO"),
            (InstructionLine, "sec"),
            (InstructionLine, "sta _b_temp"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc _b_temp"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "Y_SUB_16_8_A_TO"),
            (InstructionLine, "sec"),
            (InstructionLine, "sta _b_temp"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc _b_temp"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "SUB_16_8"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "SUB_16_8_TO"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "SUB_16_8_X"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc value"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #0"),
            (InstructionLine, "sta"),
            (Label, "SUB_16_16"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda +([dest], 0)"),
            (InstructionLine, "sbc +([value], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "sbc +([value], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "SUB_16_16_TO"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda +([valuea], 0)"),
            (InstructionLine, "sbc +([valueb], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([valuea], 1)"),
            (InstructionLine, "sbc +([valueb], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "ADD_16_16_TO"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda +([valuea], 0)"),
            (InstructionLine, "adc +([valueb], 0)"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda +([valuea], 1)"),
            (InstructionLine, "adc +([valueb], 1)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "SUB16_16_X"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc +([value], 0)"),
            (InstructionLine, "sta"),
            (InstructionLine, "sbc"),
            (InstructionLine, "adc +([value], 1)"),
            (InstructionLine, "sta"),
            (Label, "SUB_16I"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda dest"),
            (InstructionLine, "sbc #lo(value)"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([dest], 1)"),
            (InstructionLine, "sbc #hi(value)"),
            (InstructionLine, "sta +([dest], 1)"),
            (Label, "SUB_16I_X"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #lo(value)"),
            (InstructionLine, "sta"),
            (InstructionLine, "lda"),
            (InstructionLine, "sbc #hi(value)"),
            (InstructionLine, "sta"),
            (Label, "MUL_A"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "ldx dest"),
            (Label, "HLA17"),
            (InstructionLine, "bne HLA18"),
            (InstructionLine, "adc multipiler"),
            (InstructionLine, "dex"),
            (Label, "HLA18"),
            (Label, "MUL_X_A"),
            (InstructionLine, "clc"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "ldy"),
            (Label, "HLA19"),
            (InstructionLine, "bne HLA20"),
            (InstructionLine, "adc multipiler"),
            (InstructionLine, "dey"),
            (Label, "HLA20"),
            (Label, "MUL"),
            (InstructionLine, "sta dest"),
            (Label, "MUL_X"),
            (InstructionLine, "sta"),
            (Label, "MUL_16_8"),
            (InstructionLine, "ldx multipiler"),
            (Label, "HLA21"),
            (InstructionLine, "bne HLA22"),
            (InstructionLine, "dex"),
            (Label, "HLA22"),
            (Label, "MUL_16_8_X"),
            (InstructionLine, "ldx multipiler"),
            (Label, "HLA23"),
            (InstructionLine, "bne HLA24"),
            (InstructionLine, "dex"),
            (Label, "HLA24"),
            (Label, "ASL2_A"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (Label, "ASL3_A"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (Label, "ASL4_A"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (Label, "ASL5_A"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (Label, "ASL6_A"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (Label, "ASL7_A"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (Label, "ASL_16_1"),
            (InstructionLine, "asl +([dest], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (Label, "ASL_16"),
            (InstructionLine, "ldx amount"),
            (Label, "HLA25"),
            (InstructionLine, "bne HLA26"),
            (InstructionLine, "asl +([dest], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (InstructionLine, "dex"),
            (Label, "HLA26"),
            (Label, "ASL_16_TO"),
            (InstructionLine, "ldx amount"),
            (Label, "HLA27"),
            (InstructionLine, "bne HLA28"),
            (InstructionLine, "asl +([src], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (InstructionLine, "dex"),
            (Label, "HLA28"),
            (Label, "ASL_8_TO_16"),
            (InstructionLine, "lda src"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (InstructionLine, "ldx amount"),
            (Label, "HLA29"),
            (InstructionLine, "bne HLA30"),
            (InstructionLine, "asl +([dest], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (InstructionLine, "dex"),
            (Label, "HLA30"),
            (Label, "ASL2_8_A_TO_16"),
            (InstructionLine, "sta +([dest], 0)"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta +([dest], 1)"),
            (InstructionLine, "asl +([dest], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (InstructionLine, "asl +([dest], 0)"),
            (InstructionLine, "rol +([dest], 1)"),
            (Label, "LSR2_A"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (Label, "LSR3_A"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (Label, "LSR4_A"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (Label, "LSR5_A"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (Label, "LSR6_A"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (Label, "LSR7_A"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (Label, "LSR_16"),
            (InstructionLine, "ldx amount"),
            (Label, "HLA31"),
            (InstructionLine, "bne HLA32"),
            (InstructionLine, "lsr +([dest], 1)"),
            (InstructionLine, "ror +([dest], 0)"),
            (InstructionLine, "dex"),
            (Label, "HLA32"),
            (Label, "LSR_16_TO"),
            (InstructionLine, "ldx amount"),
            (Label, "HLA33"),
            (InstructionLine, "bne HLA34"),
            (InstructionLine, "lsr +([dest], 1)"),
            (InstructionLine, "ror +([dest], 0)"),
            (InstructionLine, "dex"),
            (Label, "HLA34"),
            (Label, "LSR_16_BY_6_TO_8"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "rol a"),
            (InstructionLine, "rol a"),
            (InstructionLine, "rol a"),
            (InstructionLine, "and #3"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "asl a"),
            (InstructionLine, "asl a"),
            (InstructionLine, "ora dest"),
            (InstructionLine, "sta dest"),
            (Label, "LSR_16_BY_5_TO_8"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "ora dest"),
            (InstructionLine, "sta dest"),
            (Label, "LSR_16_BY_4_TO_8"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "ora dest"),
            (InstructionLine, "sta dest"),
            (Label, "LSR_16_BY_3_TO_8"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "ora dest"),
            (InstructionLine, "sta dest"),
            (Label, "LSR_16_BY_2_TO_8"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "sta dest"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "ora dest"),
            (InstructionLine, "and #7"),
            (InstructionLine, "sta dest"),
            (Label, "DIV"),
            (InstructionLine, "sec"),
            (InstructionLine, "ldx #0"),
            (InstructionLine, "lda amount"),
            (Label, "HLA35"),
            (InstructionLine, "bne HLA36"),
            (InstructionLine, "bmi div_remainder"),
            (InstructionLine, "inx"),
            (InstructionLine, "sec"),
            (InstructionLine, "sbc dest"),
            (Label, "HLA36"),
            (InstructionLine, "jmp div_done"),
            (Label, "DIV_REMAINDER"),
            (InstructionLine, "dex"),
            (Label, "DIV_DONE"),
            (InstructionLine, "stx dest"),
            (Label, "DIV_WITH_REM"),
            (InstructionLine, "sec"),
            (InstructionLine, "ldx #0"),
            (InstructionLine, "lda dest"),
            (Label, "HLA37"),
            (InstructionLine, "bne HLA38"),
            (InstructionLine, "bmi div_remainder"),
            (InstructionLine, "inx"),
            (InstructionLine, "sec"),
            (InstructionLine, "sbc amount"),
            (Label, "HLA38"),
            (InstructionLine, "jmp div_done"),
            (Label, "DIV_REMAINDER"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc amount"),
            (InstructionLine, "sta _b_remainder"),
            (InstructionLine, "dex"),
            (Label, "DIV_DONE"),
            (InstructionLine, "stx dest"),
            (Label, "DIV_16_8_TO_X"),
            (InstructionLine, "ldx #0"),
            (Label, "_D168TX_LOOP"),
            (InstructionLine, "inx"),
            (InstructionLine, "bmi _d168tx_loop_end"),
            (InstructionLine, "bne _d168tx_loop"),
            (InstructionLine, "lda +([_w_temp], 0)"),
            (InstructionLine, "bne _d168tx_loop"),
            (Label, "_D168TX_LOOP_END"),
            (InstructionLine, "bne HLA39"),
            (InstructionLine, "dex"),
            (Label, "HLA39"),
            (Label, "MOD_16_BY_240_TO"),
            (InstructionLine, "lda src"),
            (InstructionLine, "sta +([_w_temp], 0)"),
            (InstructionLine, "ora +([src], 1)"),
            (InstructionLine, "bne HLA40"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "sta +([_w_temp], 1)"),
            (Label, "_LOOP"),
            (InstructionLine, "lda +([_w_temp], 1)"),
            (InstructionLine, "bmi _loop_end"),
            (InstructionLine, "bne _loop"),
            (InstructionLine, "lda +([_w_temp], 0)"),
            (InstructionLine, "bne _loop"),
            (Label, "_LOOP_END"),
            (InstructionLine, "beq _is_solid"),
            (InstructionLine, "lda _w_temp"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #1"),
            (Label, "HLA40"),
            (Label, "_IS_SOLID"),
            (InstructionLine, "sta dest"),
            (Label, "MOD_16_TO_8"),
            (InstructionLine, "lda src"),
            (InstructionLine, "sta +([_w_temp], 0)"),
            (InstructionLine, "ora +([src], 1)"),
            (InstructionLine, "bne HLA41"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "sta +([_w_temp], 1)"),
            (Label, "_LOOP"),
            (InstructionLine, "lda +([_w_temp], 1)"),
            (InstructionLine, "bmi _loop_end"),
            (InstructionLine, "bne _loop"),
            (InstructionLine, "lda +([_w_temp], 0)"),
            (InstructionLine, "bne _loop"),
            (Label, "_LOOP_END"),
            (InstructionLine, "beq _is_solid"),
            (InstructionLine, "lda _w_temp"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #1"),
            (Label, "HLA41"),
            (Label, "_IS_SOLID"),
            (InstructionLine, "sta dest"),
            (Label, "ABS_A"),
            (InstructionLine, "bmi HLA42"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #1"),
            (Label, "HLA42"),
            (Label, "ABS"),
            (InstructionLine, "lda number"),
            (InstructionLine, "bmi HLA43"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "sta number"),
            (InstructionLine, "inc number"),
            (Label, "HLA43"),
            (Label, "ABS_16"),
            (InstructionLine, "lda +([number], 1)"),
            (InstructionLine, "bmi HLA44"),
            (Label, "HLA44"),
            (Label, "NEG_A"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #1"),
            (Label, "NEG"),
            (InstructionLine, "lda number"),
            (InstructionLine, "eor #0xFF"),
            (InstructionLine, "sta number"),
            (InstructionLine, "inc number"),
            (Label, "NEG_16"),
            (InstructionLine, "sec"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sbc +([number], 0)"),
            (InstructionLine, "sta +([number], 0)"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sbc +([number], 1)"),
            (InstructionLine, "sta +([number], 1)"),
            (Label, "INC_16"),
            (InstructionLine, "inc +([number], 0)"),
            (InstructionLine, "beq HLA45"),
            (InstructionLine, "inc +([number], 1)"),
            (Label, "HLA45"),
            (Label, "INC_16_LIMIT"),
            (InstructionLine, "lda #0xFF"),
            (InstructionLine, "cmp +([number], 0)"),
            (InstructionLine, "bne _inc_nolimit_reached"),
            (InstructionLine, "cmp +([number], 1)"),
            (InstructionLine, "beq _inc_limit_reached"),
            (Label, "_INC_NOLIMIT_REA"),
            (InstructionLine, "inc +([number], 0)"),
            (InstructionLine, "beq HLA46"),
            (InstructionLine, "inc +([number], 1)"),
            (Label, "HLA46"),
            (Label, "_INC_LIMIT_REACH"),
            (Label, "INC_16_X"),
            (InstructionLine, "inc"),
            (InstructionLine, "beq HLA47"),
            (InstructionLine, "inc"),
            (Label, "HLA47"),
            (Label, "DEC_16"),
            (InstructionLine, "lda +([number], 0)"),
            (InstructionLine, "beq HLA48"),
            (InstructionLine, "dec +([number], 1)"),
            (Label, "HLA48"),
            (InstructionLine, "dec +([number], 0)"),
            (Label, "DEC_16_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "beq HLA49"),
            (InstructionLine, "dec"),
            (Label, "HLA49"),
            (InstructionLine, "dec"),
            (Label, "CLIP_16"),
            (InstructionLine, "lda +([number], 1)"),
            (InstructionLine, "bmi HLA50"),
            (Label, "HLA50"),
            (Label, "COMPARE"),
            (InstructionLine, "lda src"),
            (InstructionLine, "cmp value"),
            (Label, "COMPARE_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp value"),
            (Label, "X_COMPARE_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (Label, "COMPARE_16_16"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "cmp +([value], 1)"),
            (InstructionLine, "beq HLA51"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "cmp +([value], 0)"),
            (Label, "HLA51"),
            (Label, "COMPARE_16_16_X"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "cmp"),
            (InstructionLine, "beq HLA52"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "cmp"),
            (Label, "HLA52"),
            (Label, "COMPARE_16_X_16_"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (InstructionLine, "beq HLA53"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (Label, "HLA53"),
            (Label, "COMPARE_16_Y_16_"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (InstructionLine, "beq HLA54"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (Label, "HLA54"),
            (Label, "COMPARE_8_Y_8_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (Label, "COMPARE_16_X_16_"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (InstructionLine, "beq HLA55"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (Label, "HLA55"),
            (Label, "COMPARE_8_X_8_Y"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (Label, "COMPARE_8_X_8_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (Label, "COMPARE_8_X_8"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp value"),
            (Label, "COMPARE_8_Y_8_Y"),
            (InstructionLine, "lda"),
            (InstructionLine, "cmp"),
            (Label, "COMPARE_16_16_Y"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "cmp"),
            (InstructionLine, "beq HLA56"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "cmp"),
            (Label, "HLA56"),
            (Label, "COMPARE_16I"),
            (InstructionLine, "lda +([src], 1)"),
            (InstructionLine, "cmp #hi(value)"),
            (InstructionLine, "beq HLA57"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "cmp #lo(value)"),
            (Label, "HLA57"),
            (Label, "PUSHA"),
            (InstructionLine, "pha"),
            (Label, "POPA"),
            (InstructionLine, "pla"),
            (Label, "TOSS16"),
            (InstructionLine, "pla"),
            (InstructionLine, "pla"),
            (Label, "PUSH"),
            (InstructionLine, "lda value"),
            (Label, "PUSH_X"),
            (InstructionLine, "lda"),
            (Label, "PUSH_16"),
            (InstructionLine, "lda +([src], 0)"),
            (InstructionLine, "lda +([src], 1)"),
            (Label, "PUSH_16_X"),
            (InstructionLine, "lda"),
            (InstructionLine, "lda"),
            (Label, "POP"),
            (InstructionLine, "sta dest"),
            (Label, "POP_X"),
            (InstructionLine, "sta"),
            (Label, "POP_16"),
            (InstructionLine, "sta +([dest], 1)"),
            (InstructionLine, "sta +([dest], 0)"),
            (Label, "POP_16_X"),
            (InstructionLine, "sta"),
            (InstructionLine, "sta"),
            (Label, "PEEK"),
            (Label, "PUSHX"),
            (InstructionLine, "txa"),
            (Label, "POPX"),
            (InstructionLine, "tax"),
            (Label, "PEEKX"),
            (InstructionLine, "tax"),
            (Label, "PUSHY"),
            (InstructionLine, "tya"),
            (Label, "POPY"),
            (InstructionLine, "tay"),
            (Label, "PEEKY"),
            (InstructionLine, "tay"),
            (Label, "PUSHP"),
            (InstructionLine, "php"),
            (Label, "POPP"),
            (InstructionLine, "plp"),
            (Label, "PUSHSP"),
            (InstructionLine, "tsx"),
            (Label, "POPSP"),
            (InstructionLine, "txs"),
            (Label, "PUSH_ALL"),
            (Label, "POP_ALL"),
            (Label, "MEMCPY_INLINE"),
            (InstructionLine, "ldx #0"),
            (Label, "HLA58"),
            (InstructionLine, "lda"),
            (InstructionLine, "sta"),
            (InstructionLine, "inx"),
            (InstructionLine, "cpx size"),
            (InstructionLine, "bne HLA58"),
            (Label, "MEMSET_INLINE"),
            (InstructionLine, "lda value"),
            (InstructionLine, "ldx #0"),
            (Label, "HLA59"),
            (InstructionLine, "sta"),
            (InstructionLine, "inx"),
            (InstructionLine, "cpx memsize"),
            (InstructionLine, "bne HLA59"),
            (Enum, "enum COLOUR"),
            (Variable, "byte _b_temp"),
            (Variable, "word _w_temp"),
            (Variable, "pointer _p_temp"),
            (Variable, "pointer _jsrind_temp"),
            (Variable, "byte _b_remainder"),
            (Variable, "byte _random_value"),
            (Variable, "byte _random_ticks"),
            (Variable, "pointer _mem_src"),
            (Variable, "pointer _mem_dest"),
            (Variable, "byte counter"),
            (Variable, "byte palcol"),
            (Variable, "pointer paddr"),
            (Variable, "pointer pstr"),
            (Variable, "char msgbuf[64]"),
            (Label, "TURN_VIDEO_ON"),
            (InstructionLine, "rts"),
            (Label, "TURN_VIDEO_OFF"),
            (InstructionLine, "rts"),
            (Label, "VRAM_WRITE_HEX_A"),
            (InstructionLine, "pha"),
            (InstructionLine, "tax"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "lsr a"),
            (InstructionLine, "and #$0F"),
            (InstructionLine, "cmp #$A"),
            (InstructionLine, "bcs _hexxy0"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #$30"),
            (InstructionLine, "jmp _hexxy0d"),
            (Label, "_HEXXY0"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #0x37"),
            (Label, "_HEXXY0D"),
            (InstructionLine, "sta $2007"),
            (InstructionLine, "txa"),
            (InstructionLine, "and #$0F"),
            (InstructionLine, "cmp #$A"),
            (InstructionLine, "bcs _hexxy1"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #$30"),
            (InstructionLine, "jmp _hexxy1d"),
            (Label, "_HEXXY1"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #0x37"),
            (Label, "_HEXXY1D"),
            (InstructionLine, "sta $2007"),
            (InstructionLine, "pla"),
            (InstructionLine, "rts"),
            (Label, "VRAM_WRITE_STRIN"),
            (InstructionLine, "jsr VRAM_WRITE_STRIN"),
            (Label, "VRAM_WRITE_STRIN"),
            (InstructionLine, "ldy #0"),
            (Label, "HLA60"),
            (InstructionLine, "lda (pstr), y"),
            (InstructionLine, "beq HLA68"),
            (InstructionLine, "rts"),
            (Label, "HLA68"),
            (InstructionLine, "iny"),
            (InstructionLine, "jmp HLA60"),
            (InstructionLine, "rts"),
            (Variable, "byte setamt[]"),
            (Label, "VRAM_INIT"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "ldy #8"),
            (Label, "HLA61"),
            (InstructionLine, "lda"),
            (InstructionLine, "ldx #128"),
            (Label, "HLA69"),
            (InstructionLine, "dex"),
            (InstructionLine, "bne HLA69"),
            (InstructionLine, "dey"),
            (InstructionLine, "bne HLA61"),
            (InstructionLine, "rts"),
            (Label, "PALETTE_MEMSET"),
            (InstructionLine, "ldy #16"),
            (Label, "HLA62"),
            (InstructionLine, "dey"),
            (InstructionLine, "bne HLA62"),
            (InstructionLine, "rts"),
            (Label, "PALETTE_MEMSET_I"),
            (InstructionLine, "ldx col"),
            (InstructionLine, "jsr PALETTE_MEMSET"),
            (Label, "PAL_ANIMATE"),
            (InstructionLine, "lda palcol"),
            (InstructionLine, "clc"),
            (InstructionLine, "adc #0x10"),
            (InstructionLine, "sta palcol"),
            (InstructionLine, "and #0x40"),
            (InstructionLine, "php"),
            (InstructionLine, "lda palcol"),
            (InstructionLine, "plp"),
            (InstructionLine, "bne HLA63"),
            (InstructionLine, "eor #0x30"),
            (Label, "HLA63"),
            (InstructionLine, "and #0x3F"),
            (InstructionLine, "rts"),
            (Label, "PAL_ANIMATE2"),
            (InstructionLine, "ldx palcol"),
            (InstructionLine, "inx"),
            (InstructionLine, "txa"),
            (InstructionLine, "sta palcol"),
            (InstructionLine, "and #0x10"),
            (InstructionLine, "php"),
            (InstructionLine, "lda palcol"),
            (InstructionLine, "plp"),
            (InstructionLine, "bne HLA64"),
            (InstructionLine, "eor #0x0F"),
            (Label, "HLA64"),
            (InstructionLine, "and #0x0F"),
            (InstructionLine, "rts"),
            (Label, "WAIT_FOR"),
            (InstructionLine, "ldx amount"),
            (InstructionLine, "jsr WAIT_FOR_FUNC"),
            (Label, "WAIT_FOR_FUNC"),
            (Label, "HLA65"),
            (InstructionLine, "dex"),
            (InstructionLine, "bne HLA65"),
            (InstructionLine, "rts"),
            (Label, "MESSAGE_ERROR"),
            (Label, "HLA66"),
            (InstructionLine, "jsr PAL_ANIMATE"),
            (InstructionLine, "jmp HLA66"),
            (InstructionLine, "rts"),
            (Variable, "char strTitle[]"),
            (Variable, "char strHello[]"),
            (Label, "CUSTOM_SYSTEM_IN"),
            (InstructionLine, "lda #0"),
            (InstructionLine, "sta PPU.CNT0"),
            (InstructionLine, "sta PPU.CNT1"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (InstructionLine, "sta PPU.BG_SCROLL"),
            (InstructionLine, "sta $4010"),
            (InstructionLine, "sta $4011"),
            (InstructionLine, "sta $4015"),
            (InstructionLine, "lda #0xC0"),
            (InstructionLine, "sta joystick.cnt1"),
            (Label, "INT_IRQ"),
            (InstructionLine, "rti"),
            (Label, "INT_NMI"),
            (InstructionLine, "rti"),
            (Label, "MAIN"),
            (InstructionLine, "jsr VRAM_INIT"),
            (InstructionLine, "jsr TURN_VIDEO_OFF"),
            (InstructionLine, "jsr TURN_VIDEO_ON"),
            (Label, "HLA67"),
            (InstructionLine, "jsr PAL_ANIMATE"),
            (InstructionLine, "jmp HLA67"),
            (InstructionLine, "rti"),
            (Label, "JSR_IND"),
            (InstructionLine, "jmp paddr"),
            (InstructionLine, "rts")
        ]
        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self._checkScannerParserResolver(cc, scanner, parser, resolver)

