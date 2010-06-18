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
    pp_define_bar = '#define BAR\n'
    pp_undef = '#undef FOO\n'
    pp_ifdef = '#ifdef FOO\n'
    pp_ifndef = '#ifndef FOO\n'
    pp_else = '#else\n'
    pp_endif = '#endif\n'
    pp_todo = '#todo %s\n'
    pp_warning = '#warning %s\n'
    pp_error = '#error %s\n'
    pp_include = '#include %s\n'
    pp_incbin = '#incbin %s\n'

    def setUp(self):
        session = Session()
        session.preprocessor().reset_state()

    def tearDown(self):
        pass

    def test6502Preprocessor(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        self.assertTrue(isinstance(session._target.preprocessor(), MOS6502Preprocessor))

    def testDefine(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()
        pp.parse(StringIO(self.pp_define))
        self.assertTrue(pp.has_symbol('FOO'))
    
    def testDefineValue(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()
        pp.parse(StringIO(self.pp_define_value))
        self.assertEquals(pp.get_symbol('FOO'), '1')

    def testDefineString(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()
        pp.parse(StringIO(self.pp_define_string))
        self.assertEquals(pp.get_symbol('FOO'), '"blah blah blah"')

    def testUndef(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()
        pp.parse(StringIO(self.pp_define))
        self.assertTrue(pp.has_symbol('FOO'))
        pp.parse(StringIO(self.pp_undef))
        self.assertFalse(pp.has_symbol('FOO'), 'FOO shouldn\'t be defined')

    def testIfdef(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        #define FOO
        pp.parse(StringIO(self.pp_define))
        self.assertTrue(pp.has_symbol('FOO'))
        self.assertEquals(len(pp.get_ignore_stack()), 1)

        #ifdef FOO
        pp.parse(StringIO(self.pp_ifdef))
        self.assertEquals(len(pp.get_ignore_stack()), 2)
        self.assertFalse(pp.ignore_stack_top())
        self.assertFalse(pp.ignore())

        #define BAR
        pp.parse(StringIO(self.pp_define_bar))
        self.assertTrue(pp.has_symbol('BAR'))

        #endif
        pp.parse(StringIO(self.pp_endif))
        self.assertEquals(len(pp.get_ignore_stack()), 1)
        
        self.assertTrue(pp.has_symbol('BAR'))

    def testIfndef(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()
        
        self.assertEquals(len(pp.get_ignore_stack()), 1)

        #ifndef FOO
        pp.parse(StringIO(self.pp_ifndef))
        self.assertEquals(len(pp.get_ignore_stack()), 2)
        self.assertFalse(pp.ignore_stack_top())
        self.assertFalse(pp.ignore())

        #define BAR
        pp.parse(StringIO(self.pp_define_bar))
        self.assertTrue(pp.has_symbol('BAR'))

        #endif
        pp.parse(StringIO(self.pp_endif))
        self.assertEquals(len(pp.get_ignore_stack()), 1)
        
        self.assertTrue(pp.has_symbol('BAR'))

    def testElse(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        #ifdef FOO
        pp.parse(StringIO(self.pp_ifdef))
        self.assertEquals(len(pp.get_ignore_stack()), 2)
        self.assertTrue(pp.ignore_stack_top())
        self.assertTrue(pp.ignore())

        #define FOO
        pp.parse(StringIO(self.pp_define))
        self.assertFalse(pp.has_symbol('FOO'))
        self.assertTrue(pp.ignore())

        #else
        pp.parse(StringIO(self.pp_else))
        self.assertEquals(len(pp.get_ignore_stack()), 2)
        self.assertFalse(pp.ignore_stack_top())
        self.assertFalse(pp.ignore())

        #define BAR
        pp.parse(StringIO(self.pp_define_bar))
        self.assertTrue(pp.has_symbol('BAR'))

        #endif
        pp.parse(StringIO(self.pp_endif))
        self.assertEquals(len(pp.get_ignore_stack()), 1)
        
        self.assertFalse(pp.has_symbol('FOO'))
        self.assertTrue(pp.has_symbol('BAR'))

    def testBadUndef(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()
        
        #undef FOO 
        pp.parse(StringIO(self.pp_undef))

    def testTodo(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        #todo "Hello World"
        pp.parse(StringIO(self.pp_todo % '"Hello World!"'))


    def testBadTodo(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        #todo
        try:
            pp.parse(StringIO(self.pp_todo))
            self.assertTrue(False)
        except ParseException, e:
            pass

    def testWarning(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        #warning "Hello World"
        pp.parse(StringIO(self.pp_warning % '"Hello World!"'))


    def testBadWarning(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        #warning
        try:
            pp.parse(StringIO(self.pp_warning))
            self.assertTrue(False)
        except ParseException, e:
            pass

    def testError(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        #error "Hello World"
        try:
            pp.parse(StringIO(self.pp_error % '"Hello World!"'))
            self.assertTrue(False)
        except ParseFatalException, e:
            pass


    def testBadError(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        #error
        try:
            pp.parse(StringIO(self.pp_error))
            self.assertTrue(False)
        except ParseException, e:
            pass

    def testImpliedInclude(self):
        session = Session()
        session.parse_args(['--cpu=6502', '--include=tests'])
        pp = session.preprocessor()

        pp.parse(StringIO(self.pp_include % '<dummy.h>'))
        self.assertTrue(pp.has_symbol('FOO'))

    def testImpliedDirInclude(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        path = '<%s>' % os.path.join('tests', 'dummy.h')
        pp.parse(StringIO(self.pp_include % path))
        self.assertTrue(pp.has_symbol('FOO'))

    def testLiteralInclude(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        path = '"%s"' % os.path.join('tests', 'dummy.h')
        pp.parse(StringIO(self.pp_include % path))
        self.assertTrue(pp.has_symbol('FOO'))

    def testFullPathLiteralInclude(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        full_path = '"%s"' % os.path.join(os.getcwd(), 'tests', 'dummy.h')
        pp.parse(StringIO(self.pp_include % full_path))
        self.assertTrue(pp.has_symbol('FOO'))

    def testBadImpliedInclude(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        try:
            pp.parse(StringIO(self.pp_include % '<dummy.h>'))
            self.assertTrue(False)
        except ParseFatalException, e:
            pass

    def testBadLiteralInclude(self):
        session = Session()
        session.parse_args(['--cpu=6502'])
        pp = session.preprocessor()

        try:
            pp.parse(StringIO(self.pp_include % '"dummy.y"'))
            self.assertTrue(False)
        except ParseFatalException, e:
            pass

    def testImpliedIncbin(self):
        pass

    def testLiteralIncbin(self):
        pass

    def testFullPathLiteralIncbin(self):
        pass

    def testBadImpliedIncbin(self):
        pass

    def testBadLiteralIncbin(self):
        pass

