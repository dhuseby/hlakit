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
from hlakit.platform.lynx import LynxPreprocessor
from hlakit.platform.lynx.loader import LynxLoader
from hlakit.platform.lynx.lnx import LnxOff

class LynxPreprocessorTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the Lynx Preprocessor
    """

    def setUp(self):
        session = Session()
        session.preprocessor().reset_state()

    def tearDown(self):
        pass

    def testLynxPreprocessor(self):
        session = Session()
        session.parse_args(['--platform=Lynx'])
        self.assertTrue(isinstance(session._target.preprocessor(), LynxPreprocessor))

    pp_lynxloader = '#lynx.loader %s\n'

    def testLynxLoader(self):
        session = Session()
        session.parse_args(['--platform=Lynx'])
        pp = session.preprocessor() 

        pp.parse(StringIO(self.pp_lynxloader % 'loader'))
        self.assertTrue(isinstance(pp.get_output()[0], LynxLoader))
        self.assertEquals(pp.get_output()[0].get_fn(), 'loader')

    def testBadLynxLoader(self):
        session = Session()
        session.parse_args(['--platform=Lynx'])
        pp = session.preprocessor()

        try:
            pp.parse(StringIO(self.pp_lynxloader % ''))
            self.assertTrue(False)
        except ParseException:
            pass

    pp_lnxoff = '#lnx.off\n'

    def testLnxOff(self):
        session = Session()
        session.parse_args(['--platform=Lynx'])
        pp = session.preprocessor() 

        pp.parse(StringIO(self.pp_lnxoff))
        self.assertTrue(isinstance(pp.get_output()[0], LnxOff))


