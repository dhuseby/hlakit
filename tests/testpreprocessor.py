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
from StringIO import StringIO
from hlakit.common.session import Session, CommandLineError
from hlakit.cpu.mos6502 import MOS6502Preprocessor
from hlakit.platform.nes import NES

class PreprocessorTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the preprocessor.
    """

    pp_define = '#define FOO\n'
    pp_define_value = '#define FOO 1\n'
    pp_define_string = '#define FOO "blah blah blah"\n'
    pp_undef = '#undef FOO\n'
    pp_ifdef = '#ifdef FOO\n'
    pp_define_bar = '#define BAR\n'
    pp_endif = '#endif\n'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test6502Preprocessor(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        self.assertTrue(isinstance(session._target.preprocessor(), MOS6502Preprocessor))

    def testPpDefine(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()
        pp.parse(StringIO(self.pp_define))
        self.assertTrue(pp.has_symbol('FOO'))

    def testPpDefineValue(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()
        pp.parse(StringIO(self.pp_define_value))
        self.assertEquals(pp.get_symbol('FOO'), '1')

    def testPpDefineString(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()
        pp.parse(StringIO(self.pp_define_string))
        self.assertEquals(pp.get_symbol('FOO'), '"blah blah blah"')

    def testPpUndef(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()
        pp.parse(StringIO(self.pp_define))
        self.assertTrue(pp.has_symbol('FOO'))
        pp.parse(StringIO(self.pp_undef))
        self.assertFalse(pp.has_symbol('FOO'))

    def testPpIfdef(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        # #define FOO
        pp.parse(StringIO(self.pp_define))
        self.assertTrue(pp.has_symbol('FOO'))
        self.assertEquals(len(pp.get_ignore_stack()), 1)

        # #ifdef FOO
        pp.parse(StringIO(self.pp_ifdef))
        self.assertEquals(len(pp.get_ignore_stack()), 2)
        self.assertEquals(pp.ignore_stack_top(), False)
        self.assertFalse(pp.ignore())

        # #define BAR
        pp.parse(StringIO(self.pp_define_bar))
        self.assertTrue(pp.has_symbol('BAR'))

        # #endif
        pp.parse(StringIO(self.pp_endif))
        self.assertEquals(len(pp.get_ignore_stack()), 1)

