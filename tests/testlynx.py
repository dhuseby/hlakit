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
from hlakit.platform.lynx import LynxPreprocessor, LynxCompiler
from hlakit.platform.lynx.loader import LynxLoader
from hlakit.platform.lynx.lnx import LnxOff
from hlakit.platform.lynx.rom import LynxRomOrg, LynxRomEnd, LynxRomBank, LynxRomPadding

class LynxPreprocessorTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the Lynx Preprocessor
    """

    def setUp(self):
        Session().parse_args(['--platform=Lynx'])

    def tearDown(self):
        Session().preprocessor().reset_state()

    def testLynxPreprocessor(self):
        self.assertTrue(isinstance(Session().preprocessor(), LynxPreprocessor))

    pp_lynxloader = '#lynx.loader %s\n'

    def testLynxLoader(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_lynxloader % 'loader'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxLoader))
        self.assertEquals(pp.get_output()[1].get_fn(), 'loader')

    def testBadLynxLoader(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_lynxloader % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    pp_lnxoff = '#lnx.off\n'

    def testLnxOff(self):
        pp = Session().preprocessor() 

        pp.parse(StringIO(self.pp_lnxoff))
        self.assertTrue(isinstance(pp.get_output()[1], LnxOff))

    pp_romorg = '#lynx.rom.org %s\n'
    pp_romend = '#lynx.rom.end\n'
    pp_rombank = '#lynx.rom.bank %s\n'

    def testRomOrg(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_romorg % '0x10'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomOrg))
        self.assertEquals(int(pp.get_output()[1].get_segment()), 0x10)
        self.assertEquals(int(pp.get_output()[1].get_counter()), 0)
        self.assertEquals(pp.get_output()[1].get_maxsize(), None)

    def testRomOrgCounter(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_romorg % '0x20, 0x0100'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomOrg))
        self.assertEquals(int(pp.get_output()[1].get_segment()), 0x20)
        self.assertEquals(int(pp.get_output()[1].get_counter()), 0x0100)
        self.assertEquals(pp.get_output()[1].get_maxsize(), None)

    def testRomOrgCounterMaxsize(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_romorg % '0x20, 0x0100, 0x1000'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomOrg))
        self.assertEquals(int(pp.get_output()[1].get_segment()), 0x20)
        self.assertEquals(int(pp.get_output()[1].get_counter()), 0x0100)
        self.assertEquals(int(pp.get_output()[1].get_maxsize()), 0x1000)

    def testRomOrgLabel(self):
        pp = Session().preprocessor()

        pp.set_symbol('FOO', 0x01)
        pp.parse(StringIO(self.pp_romorg % 'FOO'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomOrg))
        self.assertEquals(int(pp.get_output()[1].get_segment()), 0x01)
        self.assertEquals(int(pp.get_output()[1].get_counter()), 0)
        self.assertEquals(pp.get_output()[1].get_maxsize(), None)

    def testRomOrgMaxsizeLabel(self):
        pp = Session().preprocessor()

        pp.set_symbol('FOO', 0x40)
        pp.set_symbol('BAR', 0x0400)
        pp.parse(StringIO(self.pp_romorg % 'FOO, BAR'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomOrg))
        self.assertEquals(int(pp.get_output()[1].get_segment()), 0x40)
        self.assertEquals(int(pp.get_output()[1].get_counter()), 0x0400)
        self.assertEquals(pp.get_output()[1].get_maxsize(), None)

    def testRomOrgCounterMaxsizeLabel(self):
        pp = Session().preprocessor()

        pp.set_symbol('FOO', 0x20)
        pp.set_symbol('BAR', 0x0200)
        pp.set_symbol('BAZ', 0x2000)
        pp.parse(StringIO(self.pp_romorg % 'FOO, BAR, BAZ'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomOrg))
        self.assertEquals(int(pp.get_output()[1].get_segment()), 0x20)
        self.assertEquals(int(pp.get_output()[1].get_counter()), 0x0200)
        self.assertEquals(int(pp.get_output()[1].get_maxsize()), 0x2000)

    def testRomOrgCounterWithComment(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_romorg % '0x01, 0x0100 // hello'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomOrg))
        self.assertEquals(int(pp.get_output()[1].get_segment()), 0x01)
        self.assertEquals(int(pp.get_output()[1].get_counter()), 0x0100)
        self.assertEquals(pp.get_output()[1].get_maxsize(), None)

    def testBadRomOrg(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_romorg % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testRomEnd(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_romend))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomEnd))

    def testRomBank(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_rombank % '1'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomBank))
        self.assertEquals(int(pp.get_output()[1].get_number()), 1)

    def testRomBanksizeLabel(self):
        pp = Session().preprocessor()

        pp.set_symbol('FOO', 0)
        pp.parse(StringIO(self.pp_rombank % 'FOO'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomBank))
        self.assertEquals(int(pp.get_output()[1].get_number()), 0)

    def testBadRomBank(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_rombank % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    pp_setpad = '#lynx.rom.padding %s\n'

    def testRomPaddingNum(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_setpad % '0xFF'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomPadding))
        self.assertEquals(pp.get_output()[1].get_value(), 0xFF)

    def testRomPaddingString(self):
        pp = Session().preprocessor()

        pp.parse(StringIO(self.pp_setpad % '"Foo"'))
        self.assertTrue(isinstance(pp.get_output()[1], LynxRomPadding))
        self.assertEquals(pp.get_output()[1].get_value(), 'Foo')

    def testBadRomPadding(self):
        pp = Session().preprocessor()

        try:
            pp.parse(StringIO(self.pp_setpad % ''))
            self.assertTrue(False)
        except ParseException:
            pass


class LynxCompilerTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the Lynx Compiler
    """

    def setUp(self):
        Session().parse_args(['--platform=Lynx'])

    def tearDown(self):
        Session().compiler().reset_state()

    def testLynxPreprocessor(self):
        self.assertTrue(isinstance(Session().compiler(), LynxCompiler))


