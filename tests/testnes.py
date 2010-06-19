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
from hlakit.platform.nes import NESPreprocessor
from hlakit.platform.nes.chr import ChrBanksize, ChrBank, ChrLink
from hlakit.platform.nes.ines import iNESMapper, iNESMirroring

class NESPreprocessorTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the NES Preprocessor
    """

    def setUp(self):
        session = Session()
        session.preprocessor().reset_state()

    def tearDown(self):
        pass

    def testNESPreprocessor(self):
        session = Session()
        session.parse_args(['--platform=NES'])
        self.assertTrue(isinstance(session._target.preprocessor(), NESPreprocessor))

    pp_chrbanksize = '#chr.banksize %s\n'

    def testChrBanksize(self):
        session = Session()
        session.parse_args(['--platform=NES'])
        pp = session.preprocessor() 

        pp.parse(StringIO(self.pp_chrbanksize % '1K'))
        self.assertTrue(isinstance(pp.get_output()[0], ChrBanksize))
        self.assertEquals(int(pp.get_output()[0].get_size()), 1024)

    def testBadChrBanksize(self):
        session = Session()
        session.parse_args(['--cpu=generic'])
        pp = session.preprocessor()

        try:
            pp.parse(StringIO(self.pp_chrbanksize % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    pp_inesmapper = '#ines.mapper %s\n'
    pp_inesmirroring = '#ines.mirroring %s\n'

    def testiNESMapperName(self):
        session = Session()
        session.parse_args(['--platform=NES'])
        pp = session.preprocessor() 

        pp.parse(StringIO(self.pp_inesmapper % '"NROM"'))
        self.assertTrue(isinstance(pp.get_output()[0], iNESMapper))
        self.assertEquals(pp.get_output()[0].get_mapper(), 'NROM')

    def testiNESMapperNumber(self):
        session = Session()
        session.parse_args(['--platform=NES'])
        pp = session.preprocessor() 

        pp.parse(StringIO(self.pp_inesmapper % '0'))
        self.assertTrue(isinstance(pp.get_output()[0], iNESMapper))
        self.assertEquals(int(pp.get_output()[0].get_mapper()), 0)

    def testBadiNESMapper(self):
        session = Session()
        session.parse_args(['--platform=NES'])
        pp = session.preprocessor()

        try:
            pp.parse(StringIO(self.pp_inesmapper % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testiNESMirroringVertical(self):
        session = Session()
        session.parse_args(['--platform=NES'])
        pp = session.preprocessor() 

        pp.parse(StringIO(self.pp_inesmirroring % '"vertical"'))
        self.assertTrue(isinstance(pp.get_output()[0], iNESMirroring))
        self.assertEquals(pp.get_output()[0].get_mirroring(), 'vertical')

    def testiNESMirroringHorizontal(self):
        session = Session()
        session.parse_args(['--platform=NES'])
        pp = session.preprocessor() 

        pp.parse(StringIO(self.pp_inesmirroring % '"horizontal"'))
        self.assertTrue(isinstance(pp.get_output()[0], iNESMirroring))
        self.assertEquals(pp.get_output()[0].get_mirroring(), 'horizontal')

    def testBadiNESMirroring(self):
        session = Session()
        session.parse_args(['--platform=NES'])
        pp = session.preprocessor()

        try:
            pp.parse(StringIO(self.pp_inesmirroring % '"blah"'))
            self.assertTrue(False)
        except ParseFatalException:
            pass



