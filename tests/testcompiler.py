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
from hlakit.common.compiler import Compiler
from hlakit.common.session import Session, CommandLineError
from hlakit.common.symboltable import SymbolTable
from hlakit.common.typeregistry import TypeRegistry
from hlakit.common.codeblock import CodeBlock
from hlakit.common.codeline import CodeLine
from hlakit.common.type_ import Type
from hlakit.common.struct import Struct

class CompilerTester(unittest.TestCase):
    """
    This class aggregates all of the tests for the compiler.
    """

    def setUp(self):
        Session().parse_args(['--cpu=generic'])

    def tearDown(self):
        Session().compiler().reset_state()
        TypeRegistry().reset_state()
        SymbolTable().reset_state()

    def testCompiler(self):
        session = Session()
        self.assertTrue(isinstance(session.compiler(), Compiler))

    def testInitialTypes(self):
        tr = TypeRegistry()
        types = Session().compiler().basic_types()
        for t in types:
            self.assertTrue(tr[t.get_name()] != None)

    def testSimpleType(self):
        cc = Session().compiler()
        st = SymbolTable()
        tr = TypeRegistry()

        cc.compile([CodeBlock([CodeLine('byte')])])
        self.assertTrue(isinstance(cc.get_output()[0], Type))
        self.assertEquals(cc.get_output()[0].get_name(), 'byte')
   
    cc_struct = 'struct foo { byte x, y\nword i\n }'

    def testStructType(self):
        cc = Session().compiler()
        st = SymbolTable()
        tr = TypeRegistry()

        cc.compile([CodeBlock([CodeLine(self.cc_struct)])])
        self.assertTrue(isinstance(cc.get_output()[0], Struct))
        self.assertEquals(cc.get_output()[0].get_name(), 'struct foo')
        self.assertTrue(isinstance(cc.get_output()[0].get_member('x'), Struct.Member))
        self.assertEquals(cc.get_output()[0].get_member('x').get_name(), 'x')
        self.assertEquals(cc.get_output()[0].get_member('x').get_type(), 'byte')
        self.assertTrue(isinstance(cc.get_output()[0].get_member('y'), Struct.Member))
        self.assertEquals(cc.get_output()[0].get_member('y').get_name(), 'y')
        self.assertEquals(cc.get_output()[0].get_member('y').get_type(), 'byte')
        self.assertTrue(isinstance(cc.get_output()[0].get_member('i'), Struct.Member))
        self.assertEquals(cc.get_output()[0].get_member('i').get_name(), 'i')
        self.assertEquals(cc.get_output()[0].get_member('i').get_type(), 'word')
   
    def testNestedStructType(self):
        cc = Session().compiler()
        st = SymbolTable()
        tr = TypeRegistry()

        cc.compile([CodeBlock([CodeLine('struct bar { %s f\n }' % self.cc_struct)])])
        self.assertTrue(isinstance(cc.get_output()[0], Struct))
        self.assertEquals(cc.get_output()[0].get_name(), 'struct bar')
        self.assertTrue(isinstance(cc.get_output()[0].get_member('f'), Struct.Member))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('f').get_member('x'), Struct.Member))

    """
    def testBasicVar(self):
        cc = Session().compiler()
        st = SymbolTable()
        tr = TypeRegistry()

        cc.compile([CodeBlock([CodeLine('byte b')])])
        self.assertTrue(isinstance(st['b'], Variable))
        self.assertEquals(st['b'].get_type(), 'byte')
        self.assertTrue(isinstance(tr[st['b'].get_type()], Type))
        self.assertEquals(tr[st['b'].get_type()].get_name(), 'byte')

    def testSharedVar(self):
        cc = Session().compiler()
        st = SymbolTable()
        tr = TypeRegistry()

        cc.compile([CodeBlock([CodeLine('shared pointer p')])])
        self.assertTrue(isinstance(st['p'], Variable))
        self.assertTrue(st['p'].is_shared())
        self.assertEquals(st['p'].get_type(), 'pointer')
        self.assertTrue(isinstance(tr[st['p'].get_type()], Type))
        self.assertEquals(tr[st['p'].get_type()].get_name(), 'pointer')

    def testTypedefVar(self):
        cc = Session().compiler()
        st = SymbolTable()
        tr = TypeRegistry()

        cc.compile([CodeBlock([CodeLine('typedef word FOO')])])
        self.assertTrue(isinstance(st['p'], Variable))
        self.assertTrue(st['p'].is_shared())
        self.assertEquals(st['p'].get_type(), 'pointer')
        self.assertTrue(isinstance(tr[st['p'].get_type()], Type))
        self.assertEquals(tr[st['p'].get_type()].get_name(), 'pointer')
    """
