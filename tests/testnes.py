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
from hlakit.common.session import Session
from hlakit.platform.nes import NESPreprocessor, NESCompiler
from hlakit.platform.nes.chr import ChrBanksize, ChrBank, ChrLink
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

    def testChrBanksize(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_chrbanksize % '1K'))
        self.assertTrue(isinstance(pp.get_output()[0], ChrBanksize))
        self.assertEquals(int(pp.get_output()[0].get_size()), 1024)

    def testBadChrBanksize(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_chrbanksize % ''))
            self.assertTrue(False)
        except ParseException:
            pass

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
        self.assertTrue(isinstance(pp.get_output()[0], iNESMapper))
        self.assertEquals(pp.get_output()[0].get_mapper(), 'NROM')

    def testiNESMapperNumber(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesmapper % '0'))
        self.assertTrue(isinstance(pp.get_output()[0], iNESMapper))
        self.assertEquals(int(pp.get_output()[0].get_mapper()), 0)

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
        self.assertTrue(isinstance(pp.get_output()[0], iNESMirroring))
        self.assertEquals(pp.get_output()[0].get_mirroring(), 'vertical')

    def testiNESMirroringHorizontal(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesmirroring % '"horizontal"'))
        self.assertTrue(isinstance(pp.get_output()[0], iNESMirroring))
        self.assertEquals(pp.get_output()[0].get_mirroring(), 'horizontal')

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
        self.assertTrue(isinstance(pp.get_output()[0], iNESFourscreen))
        self.assertEquals(pp.get_output()[0].get_fourscreen(), 'yes')

    def testiNESFourscreenNo(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesfourscreen % '"no"'))
        self.assertTrue(isinstance(pp.get_output()[0], iNESFourscreen))
        self.assertEquals(pp.get_output()[0].get_fourscreen(), 'no')

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
        self.assertTrue(isinstance(pp.get_output()[0], iNESBattery))
        self.assertEquals(pp.get_output()[0].get_battery(), 'yes')

    def testiNESBatteryNo(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inesbattery % '"no"'))
        self.assertTrue(isinstance(pp.get_output()[0], iNESBattery))
        self.assertEquals(pp.get_output()[0].get_battery(), 'no')

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
        self.assertTrue(isinstance(pp.get_output()[0], iNESTrainer))
        self.assertEquals(pp.get_output()[0].get_trainer(), 'yes')

    def testiNESTrainerNo(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_inestrainer % '"no"'))
        self.assertTrue(isinstance(pp.get_output()[0], iNESTrainer))
        self.assertEquals(pp.get_output()[0].get_trainer(), 'no')

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
        self.assertTrue(isinstance(pp.get_output()[0], iNESPrgRepeat))
        self.assertEquals(int(pp.get_output()[0].get_repeat()), 4)

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
        self.assertTrue(isinstance(pp.get_output()[0], iNESChrRepeat))
        self.assertEquals(int(pp.get_output()[0].get_repeat()), 4)

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
        self.assertTrue(isinstance(pp.get_output()[0], iNESOff))


class NESCompilerTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the NES Compiler
    """

    def setUp(self):
        Session().parse_args(['--platform=NES'])

    def tearDown(self):
        Session().compiler().reset_state()

    def testNESCompiler(self):
        self.assertTrue(isinstance(Session().compiler(), NESCompiler))


