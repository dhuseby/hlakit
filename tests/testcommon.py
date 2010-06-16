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

THIS SOFTWARE IS PROVIDED BY DAVID HUSEBY `AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
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

import unittest
from hlakit.common.session import Session, CommandLineError
from hlakit.cpu.mos6502 import MOS6502
from hlakit.platform.nes import NES

class CommandLineOptionsTester(unittest.TestCase):
    """
    This class aggregates all of the tests for parsing command line options.
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testNoParameters(self):
        try:
            # make sure this throws 
            session = Session([])
            self.assertTrue(False)
        except CommandLineError, e:
            return
        self.assetTrue(False)

    def testBogusCPU(self):
        try:
            session = Session(['--cpu=blah'])
            self.assertTrue(False)
        except CommandLineError, e:
            return
        self.assetTrue(False)

    def testBogusPlatform(self):
        try:
            session = Session(['--platform=blah'])
            self.assertTrue(False)
        except CommandLineError, e:
            return
        self.assetTrue(False)

    def test6502CPU(self):
        session = Session(['--cpu=6502'])
        self.assertTrue(isinstance(session._target, MOS6502))

    def testNESPlatform(self):
        session = Session(['--platform=NES'])
        self.assertTrue(isinstance(session._target, NES))
        
    def testNESPlatform2(self):
        session = Session(['--platform=Nes'])
        self.assertTrue(isinstance(session._target, NES))

    def testSingleFile(self):
        session = Session(['--cpu=6502', 'foo.s'])
        self.assertEquals(session.get_args()[0], 'foo.s')


