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
from cStringIO import StringIO
from hlakit.common.target import Target
from hlakit.common.session import Session, CommandLineError
from hlakit.common.buffer import Buffer

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
            session = Session()
            session.parse_args([])
            self.assertTrue(False)
        except CommandLineError, e:
            return
        self.assetTrue(False)

    def testBogusCPU(self):
        try:
            session = Session()
            session.parse_args(['--cpu=blah'])
            self.assertTrue(False)
        except CommandLineError, e:
            return
        self.assetTrue(False)

    def testBogusPlatform(self):
        try:
            session = Session()
            session.parse_args(['--platform=blah'])
            self.assertTrue(False)
        except CommandLineError, e:
            return
        self.assetTrue(False)

    def testCPU(self):
        session = Session()
        session.parse_args(['--cpu=generic'])
        self.assertTrue(isinstance(session._target, Target))

    def testSingleFile(self):
        session = Session()
        session.parse_args(['--cpu=generic', 'foo.s'])
        self.assertEquals(session.get_args()[0], 'foo.s')

    def testMultipleFiles(self):
        session = Session()
        session.parse_args(['--cpu=generic', 'bar.s', 'foo.s'])
        self.assertEquals(session.get_args()[0], 'bar.s')
        self.assertEquals(session.get_args()[1], 'foo.s')

    def testPathResolution(self):
        absolute_path = os.path.join(os.getcwd(), 'tests', 'dummy.s')
        session = Session()
        session.parse_args(['--cpu=generic', 'tests/dummy.s', absolute_path])
        self.assertEquals(session.get_file_path(session.get_args()[0]), absolute_path)
        self.assertEquals(session.get_file_path(session.get_args()[1]), absolute_path)

    def testDirResolution(self):
        absolute_dir = os.path.join(os.getcwd(), 'tests')
        absolute_path = os.path.join(absolute_dir, 'dummy.s')
        session = Session()
        session.parse_args(['--cpu=generic', absolute_path])
        self.assertEquals(session.get_file_dir(session.get_args()[0]), absolute_dir)

    def testI(self):
        session = Session()
        session.parse_args(['--cpu=generic', '-Itests'])
        self.assertEquals(session.get_include_dirs(), ['tests'])

    def testInclude(self):
        session = Session()
        session.parse_args(['--cpu=generic', '--include=tests'])
        self.assertEquals(session.get_include_dirs(), ['tests'])


class BufferTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the Buffer base class
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBufferPaddingByte(self):
        buf = Buffer(0)
        buf.set_padding_value(0xAA)
        buf.reserve(12)
        outf = StringIO()
        buf.save(outf)
        self.assertEquals(outf.getvalue(), '\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA')

    def testBufferPaddingWord(self):
        buf = Buffer(0)
        buf.set_padding_value(0xAA55)
        buf.reserve(12)
        outf = StringIO()
        buf.save(outf)
        self.assertEquals(outf.getvalue(), '\x55\xAA\x55\xAA\x55\xAA\x55\xAA\x55\xAA\x55\xAA')

    def testBufferPaddingDWord(self):
        buf = Buffer(0)
        buf.set_padding_value(0xDEADBEEF)
        buf.reserve(12)
        outf = StringIO()
        buf.save(outf)
        self.assertEquals(outf.getvalue(), '\xEF\xBE\xAD\xDE\xEF\xBE\xAD\xDE\xEF\xBE\xAD\xDE')

