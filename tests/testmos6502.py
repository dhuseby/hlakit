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
from hlakit.cpu.mos6502 import MOS6502Preprocessor
from hlakit.cpu.mos6502.interrupt import InterruptStart, InterruptNMI, InterruptIRQ

class MOS6502PreprocessorTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the 6502 Preprocessor
    """

    def setUp(self):
        session = Session()
        session.preprocessor().reset_state()

    def tearDown(self):
        pass

    def test6502Preprocessor(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        self.assertTrue(isinstance(session._target.preprocessor(), MOS6502Preprocessor))

    pp_intstart = '#interrupt.start %s\n'
    pp_intnmi = '#interrupt.nmi %s\n'
    pp_intirq = '#interrupt.irq %s\n'

    def testInterruptStart(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        pp.parse(StringIO(self.pp_intstart % 'start'))
        self.assertTrue(isinstance(pp.get_output()[1], InterruptStart))
        self.assertEquals(pp.get_output()[1].get_fn(), 'start')

    def testBadInterruptStart(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        try:
            pp.parse(StringIO(self.pp_intstart % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testInterruptNMI(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        pp.parse(StringIO(self.pp_intnmi % 'vblank'))
        self.assertTrue(isinstance(pp.get_output()[1], InterruptNMI))
        self.assertEquals(pp.get_output()[1].get_fn(), 'vblank')

    def testBadInterruptNMI(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        try:
            pp.parse(StringIO(self.pp_intnmi % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    def testInterruptIRQ(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        pp.parse(StringIO(self.pp_intirq % 'timer'))
        self.assertTrue(isinstance(pp.get_output()[1], InterruptIRQ))
        self.assertEquals(pp.get_output()[1].get_fn(), 'timer')

    def testBadInterruptStart(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        try:
            pp.parse(StringIO(self.pp_intirq % ''))
            self.assertTrue(False)
        except ParseException:
            pass

