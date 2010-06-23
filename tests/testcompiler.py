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
from hlakit.common.sizeof import SizeOf, SizeOfParameter
from hlakit.common.hi import Hi
from hlakit.common.lo import Lo
from hlakit.common.maskparameter import MaskParameter
from hlakit.common.type_ import Type
from hlakit.common.name import Name
from hlakit.common.struct import Struct
from hlakit.common.typedef import Typedef
from hlakit.common.variable import Variable
from hlakit.common.numericvalue import NumericValue
from hlakit.common.arrayvalue import ArrayValue, StringValue

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

        cc.compile([CodeBlock([CodeLine('byte')])])
        self.assertTrue(isinstance(cc.get_output()[0], Type))
        self.assertEquals(cc.get_output()[0].get_name(), 'byte')
   
    cc_struct = 'struct foo { byte x, y word i }'

    def testStructType(self):
        cc = Session().compiler()

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

    def testStructRef(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('struct foo')])])
        self.assertTrue(isinstance(cc.get_output()[0], Struct))
        self.assertEquals(cc.get_output()[0].get_name(), 'struct foo')
   
    def testBadStructType(self):
        cc = Session().compiler()

        try:
            cc.compile([CodeBlock([CodeLine('struct foo {}')])])
            self.assertTrue(False)
        except:
            pass

    def testNestedStructType(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('struct bar { %s f }' % self.cc_struct)])])
        self.assertTrue(isinstance(cc.get_output()[0], Struct))
        self.assertEquals(cc.get_output()[0].get_name(), 'struct bar')
        self.assertTrue(isinstance(cc.get_output()[0].get_member('f'), Struct.Member))
        self.assertTrue(isinstance(cc.get_output()[0].get_member('f').get_member('x'), Struct.Member))

    def testStructArrayMember(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('struct bar { byte f[10] }')])])
        self.assertTrue(isinstance(cc.get_output()[0], Struct))
        self.assertEquals(cc.get_output()[0].get_name(), 'struct bar')
        self.assertTrue(isinstance(cc.get_output()[0].get_member('f'), Struct.Member))
        self.assertTrue(cc.get_output()[0].get_member('f').is_array())
        self.assertEquals(cc.get_output()[0].get_member('f').get_array_size(), 10)

    def testStructBadArrayMember(self):
        cc = Session().compiler()
        
        try:
            cc.compile([CodeBlock([CodeLine('struct bar { byte f[] }')])])
            self.assertTrue(False)
        except:
            pass

    def testStructMemberListWithArrays(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('struct bar { byte a, b[10], c, d[2] }')])])
        self.assertTrue(isinstance(cc.get_output()[0], Struct))
        self.assertEquals(cc.get_output()[0].get_name(), 'struct bar')
        self.assertTrue(cc.get_output()[0].get_member('b').is_array())
        self.assertEquals(cc.get_output()[0].get_member('b').get_array_size(), 10)
        self.assertTrue(cc.get_output()[0].get_member('d').is_array())
        self.assertEquals(cc.get_output()[0].get_member('d').get_array_size(), 2)

    def testBasicTypedef(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('typedef byte INT')])])
        self.assertTrue(isinstance(cc.get_output()[0], Typedef))
        self.assertEquals(cc.get_output()[0].get_name(), 'INT')
        self.assertEquals(cc.get_output()[0].get_aliased_type(), 'byte')

    def testBasicTypedefArrayImplicitSize(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('typedef byte INT[]')])])
        self.assertTrue(isinstance(cc.get_output()[0], Typedef))
        self.assertEquals(cc.get_output()[0].get_name(), 'INT')
        self.assertEquals(cc.get_output()[0].get_aliased_type(), 'byte')
        self.assertTrue(cc.get_output()[0].is_array())
        self.assertEquals(cc.get_output()[0].get_array_size(), None)

    def testBasicTypedefArrayExplicitSize(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('typedef byte INT[5]')])])
        self.assertTrue(isinstance(cc.get_output()[0], Typedef))
        self.assertEquals(cc.get_output()[0].get_name(), 'INT')
        self.assertEquals(cc.get_output()[0].get_aliased_type(), 'byte')
        self.assertTrue(cc.get_output()[0].is_array())
        self.assertEquals(cc.get_output()[0].get_array_size(), 5)

    def testTypedefStructArrayMember(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('typedef struct bar { byte f[10] } b')])])
        self.assertTrue(isinstance(cc.get_output()[0], Typedef))
        self.assertEquals(cc.get_output()[0].get_name(), 'b')
        self.assertTrue(isinstance(cc.get_output()[0].get_aliased_type(), Struct))
        self.assertEquals(cc.get_output()[0].get_aliased_type(), 'struct bar')
        self.assertTrue(isinstance(cc.get_output()[0].get_aliased_type().get_member('f'), Struct.Member))
        self.assertTrue(cc.get_output()[0].get_aliased_type().get_member('f').is_array())
        self.assertEquals(cc.get_output()[0].get_aliased_type().get_member('f').get_array_size(), 10)

    def testBasicVar(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('byte b')])])
        self.assertTrue(isinstance(cc.get_output()[0], Variable))
        self.assertEquals(cc.get_output()[0].get_type(), 'byte')
        self.assertEquals(cc.get_output()[0].get_name(), 'b')
        self.assertFalse(cc.get_output()[0].is_array())
        self.assertFalse(cc.get_output()[0].is_shared())
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), Type))
        self.assertEquals(cc.get_output()[0].get_type().get_name(), 'byte')

    def testStructVar(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('struct bar { byte x } b')])])
        self.assertTrue(isinstance(cc.get_output()[0], Variable))
        self.assertEquals(cc.get_output()[0].get_type(), 'struct bar')
        self.assertEquals(cc.get_output()[0].get_name(), 'b')
        self.assertFalse(cc.get_output()[0].is_array())
        self.assertFalse(cc.get_output()[0].is_shared())
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), Type))
        self.assertEquals(cc.get_output()[0].get_type().get_name(), 'struct bar')

    def testSharedVar(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('shared pointer p')])])
        self.assertTrue(isinstance(cc.get_output()[0], Variable))
        self.assertEquals(cc.get_output()[0].get_type(), 'pointer')
        self.assertEquals(cc.get_output()[0].get_name(), 'p')
        self.assertTrue(cc.get_output()[0].is_shared())
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), Type))
        self.assertEquals(cc.get_output()[0].get_type().get_name(), 'pointer')

    def testArrayVarImplicitSize(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('pointer p[]')])])
        self.assertTrue(isinstance(cc.get_output()[0], Variable))
        self.assertEquals(cc.get_output()[0].get_type(), 'pointer')
        self.assertEquals(cc.get_output()[0].get_name(), 'p')
        self.assertTrue(cc.get_output()[0].is_array())
        self.assertEquals(cc.get_output()[0].get_array_size(), None)

    def testArrayVarExplicitSize(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('word w[7]')])])
        self.assertTrue(isinstance(cc.get_output()[0], Variable))
        self.assertEquals(cc.get_output()[0].get_type(), 'word')
        self.assertEquals(cc.get_output()[0].get_name(), 'w')
        self.assertTrue(cc.get_output()[0].is_array())
        self.assertEquals(cc.get_output()[0].get_array_size(), 7)

    def testVarWithAddress(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('byte a : 0x0200')])])
        self.assertTrue(isinstance(cc.get_output()[0], Variable))
        self.assertEquals(cc.get_output()[0].get_type(), 'byte')
        self.assertEquals(cc.get_output()[0].get_name(), 'a')
        self.assertFalse(cc.get_output()[0].is_array())
        self.assertFalse(cc.get_output()[0].is_shared())
        self.assertEquals(int(cc.get_output()[0].get_address()), 0x0200)
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), Type))
        self.assertEquals(cc.get_output()[0].get_type().get_name(), 'byte')

    def testSharedStructArrayAddressVar(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('shared struct bar { byte x[4] } c[11] : 0x1234')])])
        self.assertTrue(isinstance(cc.get_output()[0], Variable))
        self.assertEquals(cc.get_output()[0].get_type(), 'struct bar')
        self.assertEquals(cc.get_output()[0].get_name(), 'c')
        self.assertTrue(cc.get_output()[0].is_array())
        self.assertTrue(cc.get_output()[0].is_shared())
        self.assertEquals(int(cc.get_output()[0].get_address()), 0x1234)
        self.assertEquals(cc.get_output()[0].get_array_size(), 11)
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), Type))
        self.assertEquals(cc.get_output()[0].get_type().get_name(), 'struct bar')

    def testStructReferenceVar(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('struct baz d')])])
        self.assertTrue(isinstance(cc.get_output()[0], Variable))
        self.assertEquals(cc.get_output()[0].get_type(), 'struct baz')
        self.assertEquals(cc.get_output()[0].get_name(), 'd')
        self.assertFalse(cc.get_output()[0].is_array())
        self.assertFalse(cc.get_output()[0].is_shared())
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), Type))
        self.assertEquals(cc.get_output()[0].get_type().get_name(), 'struct baz')

    def testSizeOfName(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(Foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], SizeOf))
        self.assertTrue(isinstance(cc.get_output()[0].get_param(), SizeOfParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_param().get_symbol(), Name))
        self.assertEquals(cc.get_output()[0].get_param().get_symbol().get_name(), 'Foo')

    def testSizeOfStructRef(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(struct bar)')])])
        self.assertTrue(isinstance(cc.get_output()[0], SizeOf))
        self.assertTrue(isinstance(cc.get_output()[0].get_param(), SizeOfParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_param().get_symbol(), Struct))
        self.assertEquals(cc.get_output()[0].get_param().get_symbol().get_name(), 'struct bar')

    def testSizeOfFullStruct(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(struct baz { byte b[10], c })')])])
        self.assertTrue(isinstance(cc.get_output()[0], SizeOf))
        self.assertTrue(isinstance(cc.get_output()[0].get_param(), SizeOfParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_param().get_symbol(), Struct))
        self.assertEquals(cc.get_output()[0].get_param().get_symbol().get_name(), 'struct baz')

    def testSizeOfDottedVarReference(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(foo.bar.baz)')])])
        self.assertTrue(isinstance(cc.get_output()[0], SizeOf))
        self.assertTrue(isinstance(cc.get_output()[0].get_param(), SizeOfParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_param().get_symbol(), Name))
        self.assertEquals(cc.get_output()[0].get_param().get_symbol().get_name(), 'foo.bar.baz')

    def testNestedSizeOf(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(sizeof(foo))')])])
        self.assertTrue(isinstance(cc.get_output()[0], SizeOf))
        self.assertTrue(isinstance(cc.get_output()[0].get_param(), SizeOf))
        self.assertTrue(isinstance(cc.get_output()[0].get_param().get_param(), SizeOfParameter))
        self.assertEquals(cc.get_output()[0].get_param().get_param().get_symbol().get_name(), 'foo')

    def testSizeOfImmediate(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(0x0012)')])])
        self.assertTrue(isinstance(cc.get_output()[0], SizeOf))
        self.assertTrue(isinstance(cc.get_output()[0].get_param(), SizeOfParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_param().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_param().get_value()), 0x0012)

    def testSizeOfString(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof("hello world")')])])
        self.assertTrue(isinstance(cc.get_output()[0], SizeOf))
        self.assertTrue(isinstance(cc.get_output()[0].get_param(), SizeOfParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_param().get_value(), StringValue))
        self.assertEquals(str(cc.get_output()[0].get_param().get_value()), 'hello world')

    def testSizeOfArray(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof({ 1, 2, 3 })')])])
        self.assertTrue(isinstance(cc.get_output()[0], SizeOf))
        self.assertTrue(isinstance(cc.get_output()[0].get_param(), SizeOfParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_param().get_value(), ArrayValue))

    def testHiOfImmediate(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('hi(0x0012)')])])
        self.assertTrue(isinstance(cc.get_output()[0], Hi))
        self.assertTrue(isinstance(cc.get_output()[0].get_param(), MaskParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_param().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_param().get_value()), 0x0012)
        
    def testLoOfImmediate(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('lo(0x0012)')])])
        self.assertTrue(isinstance(cc.get_output()[0], Lo))
        self.assertTrue(isinstance(cc.get_output()[0].get_param(), MaskParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_param().get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_param().get_value()), 0x0012)



