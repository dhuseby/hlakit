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
from hlakit.common.typeregistry import TypeRegistry
from hlakit.common.codeblock import CodeBlock
from hlakit.common.codeline import CodeLine
from hlakit.common.numericvalue import NumericValue
from hlakit.common.functiontype import FunctionType
from hlakit.common.functionparameter import FunctionParameter
from hlakit.common.function import Function
from hlakit.common.functioncall import FunctionCall
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd
from hlakit.common.immediate import Immediate
from hlakit.common.typedef import Typedef
from hlakit.common.type_ import Type
from hlakit.common.variable import Variable
from hlakit.cpu.mos6502 import MOS6502Preprocessor, MOS6502Compiler
from hlakit.cpu.mos6502.interrupt import InterruptStart, InterruptNMI, InterruptIRQ
from hlakit.cpu.mos6502.register import Register
from hlakit.cpu.mos6502.opcode import Opcode
from hlakit.cpu.mos6502.operand import Operand
from hlakit.cpu.mos6502.instructionline import InstructionLine
from hlakit.cpu.mos6502.conditional import Conditional
from hlakit.platform.nes import NESPreprocessor, NESCompiler
from hlakit.platform.nes.chr import ChrBanksize, ChrBank, ChrLink, ChrEnd
from hlakit.platform.nes.ines import iNESMapper, iNESMirroring, iNESFourscreen, iNESBattery, iNESTrainer, iNESPrgRepeat, iNESChrRepeat, iNESOff

class NESPreprocessorTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the NES Preprocessor
    """

    def setUp(self):
        Session().parse_args(['--platform=NES'])

    def tearDown(self):
        Session().preprocessor().reset_state()

    def testNESPreprocessor(self):
        self.assertTrue(isinstance(Session().preprocessor(), NESPreprocessor))

    pp_chrbanksize = '#chr.banksize %s\n'
    pp_chrend = '#chr.end'

    def testChrBanksize(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_chrbanksize % '1K'))
        self.assertTrue(isinstance(pp.get_output()[1], ChrBanksize))
        self.assertEquals(int(pp.get_output()[1].get_size()), 1024)

    def testChrBanksizeLabel(self):
        pp = Session().preprocessor() 

        pp.set_symbol('FOO', 1024)
        pp.parse(StringIO(self.pp_chrbanksize % 'FOO'))
        self.assertTrue(isinstance(pp.get_output()[1], ChrBanksize))
        self.assertEquals(int(pp.get_output()[1].get_size()), 1024)

    def testBadChrBanksize(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_chrbanksize % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    #TODO: tests for #chr.bank and #chr.link

    def testChrEnd(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_chrend))
        self.assertTrue(isinstance(pp.get_output()[1], ChrEnd))

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

        pp.parse(StringIO(self.pp_inesmapper % '"NROM"'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESMapper))
        self.assertEquals(pp.get_output()[1].get_mapper(), 'NROM')

    def testiNESMapperNumber(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesmapper % '0'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESMapper))
        self.assertEquals(int(pp.get_output()[1].get_mapper()), 0)

    def testBadiNESMapper(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_inesmapper % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testiNESMirroringVertical(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesmirroring % '"vertical"'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESMirroring))
        self.assertEquals(pp.get_output()[1].get_mirroring(), 'vertical')

    def testiNESMirroringHorizontal(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesmirroring % '"horizontal"'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESMirroring))
        self.assertEquals(pp.get_output()[1].get_mirroring(), 'horizontal')

    def testBadiNESMirroring(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_inesmirroring % '"blah"'))
            self.assertTrue(False)
        except ParseFatalException:
            pass

    def testiNESFourscreenYes(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesfourscreen % '"yes"'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESFourscreen))
        self.assertEquals(pp.get_output()[1].get_fourscreen(), 'yes')

    def testiNESFourscreenNo(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesfourscreen % '"no"'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESFourscreen))
        self.assertEquals(pp.get_output()[1].get_fourscreen(), 'no')

    def testBadiNESFourscreen(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_inesfourscreen % '"blah"'))
            self.assertTrue(False)
        except ParseFatalException:
            pass

    def testiNESBatterYes(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesbattery % '"yes"'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESBattery))
        self.assertEquals(pp.get_output()[1].get_battery(), 'yes')

    def testiNESBatteryNo(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesbattery % '"no"'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESBattery))
        self.assertEquals(pp.get_output()[1].get_battery(), 'no')

    def testBadiNESBattery(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_inesbattery % '"blah"'))
            self.assertTrue(False)
        except ParseFatalException:
            pass

    def testiNESTrainerYes(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inestrainer % '"yes"'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESTrainer))
        self.assertEquals(pp.get_output()[1].get_trainer(), 'yes')

    def testiNESTrainerNo(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inestrainer % '"no"'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESTrainer))
        self.assertEquals(pp.get_output()[1].get_trainer(), 'no')

    def testBadiNESTrainer(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_inestrainer % '"blah"'))
            self.assertTrue(False)
        except ParseFatalException:
            pass

    def testiNESPrgRepeat(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesprgrepeat % '4'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESPrgRepeat))
        self.assertEquals(int(pp.get_output()[1].get_repeat()), 4)

    def testBadiNESPrgRepeat(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_inesprgrepeat % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testiNESChrRepeat(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_ineschrrepeat % '4'))
        self.assertTrue(isinstance(pp.get_output()[1], iNESChrRepeat))
        self.assertEquals(int(pp.get_output()[1].get_repeat()), 4)

    def testBadiNESChrRepeat(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_ineschrrepeat % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testiNESOff(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesoff))
        self.assertTrue(isinstance(pp.get_output()[1], iNESOff))


class NESCompilerTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the NES Compiler
    """

    def setUp(self):
        Session().parse_args(['--platform=NES'])

    def tearDown(self):
        Session().compiler().reset_state()
        TypeRegistry().reset_state()
        SymbolTable().reset_state()

    def testNESCompiler(self):
        self.assertTrue(isinstance(Session().compiler(), NESCompiler))

    def testSystemInitialize(self):
        code = """
            inline system_initialize()
            {
                disable_decimal_mode()
                disable_interrupts()
                reset_stack()  // this is why this MUST be inline!
                vblank_wait()
                // clear the registers
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
            """
        types = [ Function,
                  ScopeBegin,
                  FunctionCall,
                  FunctionCall,
                  FunctionCall,
                  FunctionCall,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  InstructionLine,
                  FunctionCall,
                  ScopeEnd ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

    def testPPUEnum(self):
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

    def testFunkyFunctionCall(self):
        code = """
            inline ppu_turn_off_draw()
            {
            ppu_disable_nmi()
            ppu_ctl1_clear(%00010000|%00001000)
            }
            """
        types = [ Function,
                  ScopeBegin,
                  FunctionCall,
                  FunctionCall,
                  ScopeEnd ]

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]))

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
            byte y,
            tile,
            attributes,
            x
            } OAM_ENTRY

            typedef struct PALENT_ {
            byte colBackground,
            col1,
            col2,
            col3
            } PALENT

            typedef struct PALETTE_ {
            PALENT pal0,
            pal1,
            pal2,
            pal3
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
            """
        '''
            inline vblank_wait_full()
            {
            vblank_wait()
            unvblank_wait()
            }
            inline vblank_wait_for(amount)
            {
            ldx amount
            do {
            vblank_wait_full()
            dex
            } while (nonzero)
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
            ind_assign(PPU.IO, value)
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
            if (zero) {
            test_joystick1_prev(buttonmask)
            }
            eor #0xFF
            }
            inline test_button_press(buttonmask)
            {
            test_joystick1(buttonmask)    // return(
            if (nonzero) {      //   if(joypad&buttonmask)
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
            sta [dest]
            }
            inline assign_ind_y(dest,value)
            {
            lda value
            sta [dest],y
            }
            inline ind_x_assign(dest,src)
            {
            lda [src,x]
            sta dest
            }
            inline ind_y_assign(dest,src)
            {
            lda [src],y
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
            lda [value],y
            sta dest+0,x
            iny
            lda [value],y
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
            lda [value],y
            sta dest +0
            iny
            lda [value],y
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
            if (zero) {
            lda mask+1
            bit dest+1
            }
            }
            inline test_16i(dest,mask)
            {
            lda #lo(mask)
            bit dest+0
            if (zero) {
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
            if (negative) {
            clc
            adc dest
            sta dest
            lda dest+1
            adc #0xFF
            sta dest+1
            } else {
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
            if (negative) {
            clc
            adc dest+0,x
            sta dest+0,x
            lda dest+1,x
            adc #0xFF
            } else {
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
            if (negative) {
            clc
            adc src+0,x
            sta dest+0
            lda src+1,x
            adc #0xFF
            sta dest+1
            } else {
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
            adc [value],y
            sta dest+0
            lda src+1
            adc #0
            sta dest+1
            }
            inline adds_16_8yind_to(src,value,dest)
            {
            lda [value],y
            if (negative) {
            ldx #0xFF
            } else {
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
            if (positive) {
            clc
            adc var16 +0,x
            sta dest16+0
            lda var16 +1,x
            adc #0
            } else {
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
            while (nonzero) {
            adc multipiler
            dex
            }
            }
            inline mul_x_a( dest, multipiler )
            {
            clc
            lda #0
            ldy dest,x
            while (nonzero) {
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
            while (nonzero) {
            add_16_16( _w_temp, dest )
            dex
            }
            assign_16_16( dest, _w_temp )
            }
            inline mul_16_8_x( dest, multipiler )
            {
            zero_16(_w_temp)
            ldx multipiler
            while (nonzero) {
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
            while (not zero) {
            asl dest+0
            rol dest+1
            dex
            }
            }
            inline asl_16_to( dest, src, amount )
            {
            assign_16_16(src,dest)
            ldx amount
            while (not zero) {
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
            while (not zero) {
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
            while (not zero) {
            lsr dest+1
            ror dest+0
            dex
            }
            }
            inline lsr_16_to( dest, src, amount )
            {
            assign_16_16(src,dest)
            ldx amount
            while (not zero) {
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
            lsr3_a()    //
            sta dest    //
            lda src+1    // A |= HIGH(B) << 5
            asl5_a()    //
            ora dest    //
            sta dest    //
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
            while (nonzero) {
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
            inline div_with_rem( dest, amount )
            {
            sec
            ldx #0
            lda dest
            while (nonzero) {
            bmi div_done_remainder
            inx
            sec
            sbc amount
            }
            assign(_b_remainder, #0)
            jmp div_done
            div_done_remainder:
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
            if (not zero) {
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
            if (not zero) {
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
            if (is minus) {
            eor #0xFF
            clc
            adc #1
            }
            }
            inline abs(number)
            {
            lda number
            if (is minus) {
            eor #0xFF
            sta number
            inc number
            }
            }
            inline abs_16(number)
            {
            lda number+1
            if (is minus) {
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
            {/*
            ldx number+0
            inx
            if(not zero) {
            ldx number+1
            inx
            if(not zero) {
            inc number+0
            if(zero)
            inc number+1
            }
            }*/
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
            if (negative) {
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
            if (equal) {
            lda src+0
            cmp value+0
            }
            }
            inline compare_16_16_x(src, value)
            {
            lda src+1
            cmp value+1, x
            if (equal) {
            lda src+0
            cmp value+0, x
            }
            }
            inline compare_16_x_16_x(src, value)
            {
            lda src+1, x
            cmp value+1, x
            if (equal) {
            lda src+0, x
            cmp value+0, x
            }
            }
            inline compare_16_y_16_x(src, value)
            {
            lda src+1, y
            cmp value+1, x
            if (equal) {
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
            if (equal) {
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
            if (equal) {
            lda src+0
            cmp value+0, y
            }
            }
            inline compare_16i(src, value)
            {
            lda src+1
            cmp #hi(value)
            if (equal) {
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
            do {
            lda src,x
            sta dest,x
            inx
            cpx size
            } while (nonzero)
            }
            inline memset_inline( memdest, value, memsize)
            {
            lda value
            ldx #0
            do {
            sta memdest,x
            inx
            cpx memsize
            } while (nonzero)
            }

            enum COLOUR {
            BLUE  = 0x01,
            RED  = 0x05,
            YELLOW = 0x07,
            GREEN  = 0x09,
            }

            byte _b_temp
            word _w_temp
            pointer _p_temp, _jsrind_temp
            byte _b_remainder,
            _random_value,
            _random_ticks
            pointer _mem_src, _mem_dest

            byte counter, palcol
            pointer paddr, pstr
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
            forever {
            lda [pstr], y
            if (zero) {
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
            do {
            lda setamt-1,y
            ldx #128
            do {
            vram_write_a()
            dex
            } while (not zero)
            dey
            } while (not zero)
            vram_write_string_inl(0x2000+0x40, strTitle)
            vram_clear_address()
            }
            function palette_memset()
            {
            unvblank_wait()
            vblank_wait()
            vram_set_address_i(0x3F00)
            ldy #16
            do {
            vram_write_regx()
            dey
            } while (not equal)
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
            if (set) {
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
            if (set) {
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
            do {
            vblank_wait_full()
            dex
            } while (nonzero)
            }
            function message_error()
            {
            assign(palcol, #COLOUR.RED)
            forever {
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
            forever {
            wait_for(#6)
            pal_animate()
            }
            }
            function jsr_ind()
            {
            jmp [paddr]
            }
        '''

        types=[ Function,
                ScopeBegin,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                FunctionCall,
                FunctionCall,
                FunctionCall,
                FunctionCall,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                FunctionCall,
                ScopeEnd,
                
                Enum,










                
                Typedef,
                
                
                
                
                
                
                Typedef,
                
                
                
                
                
                
                Typedef,
                
                
                
                
                
                
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
               
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                FunctionCall,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                FunctionCall,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                FunctionCall,
                FunctionCall,
                FunctionCall,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                FunctionCall,
                FunctionCall,
                ScopeEnd,

                Function,
                ScopeBegin,
                FunctionCall,
                FunctionCall,
                ScopeEnd,

                Function,
                ScopeBegin,
                FunctionCall,
                ScopeEnd,

                Function,
                ScopeBegin,
                FunctionCall,
                ScopeEnd,

                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,

                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,

                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,

                Function,
                ScopeBegin,
                FunctionCall,
                ScopeEnd,

                Function,
                ScopeBegin,
                Conditional,
                InstructionLine,
                Conditional,
                ScopeEnd]
        '''
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                FunctionCall,
                ScopeEnd,
                Function,
                ScopeBegin,
                Type,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                Function,
                ScopeBegin,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                FunctionCall,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                FunctionCall,
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                Function,
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
                ScopeEnd,
                Function,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                Conditional,
                ScopeBegin,
                InstructionLine,
                InstructionLine,
                InstructionLine,
                ScopeEnd,
                Conditional,
                ScopeEnd,
                Enum,
                Type,
                Type,
                Type,
                Function,
                ScopeBegin,
                Type,
                Type,
                Type]
        '''

        cc = Session().compiler()
        cb = build_code_block(code)
        cc.compile([cb])
        self.assertEquals(len(cc.get_output()), len(types))
        for i in range(0,len(types)):
            self.assertTrue(isinstance(cc.get_output()[i], types[i]), "%d: %s != %s (%s)" % (i, type(cc.get_output()[i]), types[i], cc.get_output()[i]))

