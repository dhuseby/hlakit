"""
HLAKit Session Tests
Copyright (c) 2010-2011 David Huseby. All rights reserved.

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
from cStringIO import StringIO
from hlakit.common.session import Session, CommandLineError
from hlakit.platform.generic import Generic
from hlakit.cpu.mos6502 import MOS6502

class CommandLineOptionsTester(unittest.TestCase):
    """
    This class aggregates all of the tests for parsing command line options.
    """
    def setUp(self):
        self.old_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')

    def tearDown(self):
        sys.stderr.close()
        sys.stderr = self.old_stderr

    def testBogusCPU(self):
        session = Session()
        self.assertRaises(CommandLineError, session.parse_args, ['--cpu=blah'])
    
    def testBogusPlatform(self):
        session = Session()
        self.assertRaises(CommandLineError, session.parse_args, ['--platform=blah'])
    
    def testGeneric6502Platform(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        session.initialize_target()
        self.assertIsInstance(session._target, Generic)
        self.assertIsInstance(session._target._cpu, MOS6502)

    def testGenericPlatform(self):
        session = Session()
        self.assertRaises(CommandLineError, session.parse_args, ['--platform=generic'])

    def testI(self):
        session = Session()
        session.parse_args(['--cpu=6502', '-Itests'])
        self.assertIsInstance(session.get_include_dirs(), list)
        self.assertEquals(session.get_include_dirs(), ['tests'])

    def testInclude(self):
        session = Session()
        session.parse_args(['--cpu=6502', '--include=tests'])
        self.assertIsInstance(session.get_include_dirs(), list)
        self.assertEquals(session.get_include_dirs(), ['tests'])

    def testMultipleFiles(self):
        session = Session()
        session.parse_args(['--cpu=6502', 'bar.s', 'foo.s'])
        self.assertIsInstance(session.get_args(), list)
        self.assertEquals(session.get_args()[0], 'bar.s')
        self.assertEquals(session.get_args()[1], 'foo.s')

    def testNoParameters(self):
        session = Session()
        self.assertRaises(CommandLineError, session.parse_args, [])

    def testSingleFile(self):
        session = Session()
        session.parse_args(['--cpu=6502', 'foo.s'])
        self.assertIsInstance(session.get_args(), list)
        self.assertEquals(session.get_args()[0], 'foo.s')

