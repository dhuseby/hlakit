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
from hlakit.common.functiontype import FunctionType
from hlakit.common.functionparameter import FunctionParameter
from hlakit.common.function import Function
from hlakit.common.functioncall import FunctionCall
from hlakit.common.type_ import Type
from hlakit.common.name import Name
from hlakit.common.struct import Struct
from hlakit.common.typedef import Typedef
from hlakit.common.variable import Variable
from hlakit.common.numericvalue import NumericValue
from hlakit.common.arrayvalue import ArrayValue, StringValue
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd

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

    def testFunctionCall(self):
        cc = Session().compiler()

        # pre-define the function 'foo'
        st = SymbolTable()
        st.reset_state()
        st.new_symbol(Function(Name('foo'), FunctionType('function')))

        # compile a call to foo()
        cc.compile([CodeBlock([CodeLine('foo()')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')

        # reset state
        st.reset_state()

    def testFunctionFunctionDecl(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('function foo() { }')])])
        self.assertEquals(len(cc.get_output()), 3)
        self.assertTrue(isinstance(cc.get_output()[0], Function))
        self.assertTrue(isinstance(cc.get_output()[1], ScopeBegin))
        self.assertTrue(isinstance(cc.get_output()[2], ScopeEnd))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertFalse(cc.get_output()[0].get_noreturn())
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'function')

    def testFunctionInlineDecl(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('inline foo() { }')])])
        self.assertEquals(len(cc.get_output()), 3)
        self.assertTrue(isinstance(cc.get_output()[0], Function))
        self.assertTrue(isinstance(cc.get_output()[1], ScopeBegin))
        self.assertTrue(isinstance(cc.get_output()[2], ScopeEnd))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'inline')

    def testFunctionInterruptDecl(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('interrupt foo() { }')])])
        self.assertEquals(len(cc.get_output()), 3)
        self.assertTrue(isinstance(cc.get_output()[0], Function))
        self.assertTrue(isinstance(cc.get_output()[1], ScopeBegin))
        self.assertTrue(isinstance(cc.get_output()[2], ScopeEnd))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'interrupt')

    def testFunctionInterruptWithNameDecl(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('interrupt.start foo() { }')])])
        self.assertEquals(len(cc.get_output()), 3)
        self.assertTrue(isinstance(cc.get_output()[0], Function))
        self.assertTrue(isinstance(cc.get_output()[1], ScopeBegin))
        self.assertTrue(isinstance(cc.get_output()[2], ScopeEnd))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_type().get_name(), Name))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'interrupt')
        self.assertEquals(cc.get_output()[0].get_type().get_name(), 'start')

    def testFunctionBadFunctionDecl(self):
        cc = Session().compiler()
        
        try:
            cc.compile([CodeBlock([CodeLine('function.foo bar() { }')])])
            self.assertTrue(False)
        except:
            pass

    def testFunctionBadFunctionDecl2(self):
        cc = Session().compiler()
        
        try:
            cc.compile([CodeBlock([CodeLine('function bar(foo) { }')])])
            self.assertTrue(False)
        except:
            pass

    def testFunctionBadInlineDecl(self):
        cc = Session().compiler()
        
        try:
            cc.compile([CodeBlock([CodeLine('inline.foo bar() { }')])])
            self.assertTrue(False)
        except:
            pass

    def testFunctionBadInlineDecl2(self):
        cc = Session().compiler()
        
        try:
            cc.compile([CodeBlock([CodeLine('inline bar(foo) { }')])])
            self.assertTrue(False)
        except:
            pass

    def testFunctionNoReturnFunctionDecl(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('function noreturn foo() { }')])])
        self.assertEquals(len(cc.get_output()), 3)
        self.assertTrue(isinstance(cc.get_output()[0], Function))
        self.assertTrue(isinstance(cc.get_output()[1], ScopeBegin))
        self.assertTrue(isinstance(cc.get_output()[2], ScopeEnd))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertTrue(cc.get_output()[0].get_noreturn())
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'function')

    def testFunctionNoReturnInterruptDecl(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('interrupt noreturn foo() { }')])])
        self.assertEquals(len(cc.get_output()), 3)
        self.assertTrue(isinstance(cc.get_output()[0], Function))
        self.assertTrue(isinstance(cc.get_output()[1], ScopeBegin))
        self.assertTrue(isinstance(cc.get_output()[2], ScopeEnd))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertTrue(cc.get_output()[0].get_noreturn())
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'interrupt')

    def testFunctionBadNoReturnInlineDecl(self):
        cc = Session().compiler()
        
        try:
            cc.compile([CodeBlock([CodeLine('inline noreturn bar(foo) { }')])])
            self.assertTrue(False)
        except:
            pass

    def testFunctionInlineWithOneParamDecl(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('inline foo(bar) { }')])])
        self.assertEquals(len(cc.get_output()), 3)
        self.assertTrue(isinstance(cc.get_output()[0], Function))
        self.assertTrue(isinstance(cc.get_output()[1], ScopeBegin))
        self.assertTrue(isinstance(cc.get_output()[2], ScopeEnd))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_params(), list))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], Name))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'inline')
        self.assertEquals(cc.get_output()[0].get_params()[0].get_name(), 'bar')

    def testFunctionInlineWithMultipleParamDecl(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('inline foo(bar,baz, qux) { }')])])
        self.assertEquals(len(cc.get_output()), 3)
        self.assertTrue(isinstance(cc.get_output()[0], Function))
        self.assertTrue(isinstance(cc.get_output()[1], ScopeBegin))
        self.assertTrue(isinstance(cc.get_output()[2], ScopeEnd))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_params(), list))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 3)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[1], Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[2], Name))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'inline')
        self.assertEquals(cc.get_output()[0].get_params()[0].get_name(), 'bar')
        self.assertEquals(cc.get_output()[0].get_params()[1].get_name(), 'baz')
        self.assertEquals(cc.get_output()[0].get_params()[2].get_name(), 'qux')

    def testFunctionInlineWithStructRefParamDecl(self):
        cc = Session().compiler()

        # pre-define the function 'foo'
        st = SymbolTable()
        st.reset_state()
        st.new_symbol(Function(Name('foo'), FunctionType('inline'), 
                      [FunctionParameter('one')]))

        cc.compile([CodeBlock([CodeLine('foo(bar.baz)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_params(), list))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'inline')
        self.assertEquals(cc.get_output()[0].get_params()[0].get_symbol(), 'bar.baz')

        # reset state
        st.reset_state()

    def testFunctionInlineWithMultipleStructRefParamDecl(self):
        cc = Session().compiler()

        # pre-define the function 'foo'
        st = SymbolTable()
        st.reset_state()
        st.new_symbol(Function(Name('foo'), FunctionType('inline'),
                      [FunctionParameter('one'), FunctionParameter('two'), FunctionParameter('three')]))

        cc.compile([CodeBlock([CodeLine('foo(bar.food,baz, qux.free)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_params(), list))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 3)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[1], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[2], FunctionParameter))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'inline')
        self.assertEquals(cc.get_output()[0].get_params()[0].get_symbol(), 'bar.food')
        self.assertEquals(cc.get_output()[0].get_params()[1].get_symbol(), 'baz')
        self.assertEquals(cc.get_output()[0].get_params()[2].get_symbol(), 'qux.free')

        # reset state
        st.reset_state()

    def testFunctionInlineWithOneValueDecl(self):
        cc = Session().compiler()

        # pre-define the function 'foo'
        st = SymbolTable()
        st.reset_state()
        st.new_symbol(Function(Name('foo'), FunctionType('inline'), 
                      [FunctionParameter('one')]))

        cc.compile([CodeBlock([CodeLine('foo(0x0400)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_params(), list))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'inline')
        self.assertEquals(int(cc.get_output()[0].get_params()[0].get_value()), 0x0400)

        # reset state
        st.reset_state()

    def testFunctionInlineWithMultipleValueDecl(self):
        cc = Session().compiler()

        # pre-define the function 'foo'
        st = SymbolTable()
        st.reset_state()
        st.new_symbol(Function(Name('foo'), FunctionType('inline'),
                      [FunctionParameter('one'), FunctionParameter('two'), 
                       FunctionParameter('three'), FunctionParameter('four'),
                       FunctionParameter('five')]))

        cc.compile([CodeBlock([CodeLine('foo(0x0400,1024,$0400,1K,%10000000000)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_params(), list))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 5)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[1], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[2], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[3], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[4], FunctionParameter))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'inline')
        self.assertEquals(int(cc.get_output()[0].get_params()[0].get_value()), 1024)
        self.assertEquals(int(cc.get_output()[0].get_params()[1].get_value()), 1024)
        self.assertEquals(int(cc.get_output()[0].get_params()[2].get_value()), 1024)
        self.assertEquals(int(cc.get_output()[0].get_params()[3].get_value()), 1024)
        self.assertEquals(int(cc.get_output()[0].get_params()[4].get_value()), 1024)

        # reset state
        st.reset_state()

    def testFunctionInlineWithMultipleMixedParamDecl(self):
        cc = Session().compiler()

        # pre-define the function 'foo'
        st = SymbolTable()
        st.reset_state()
        st.new_symbol(Function(Name('foo'), FunctionType('inline'),
                      [FunctionParameter('one'), FunctionParameter('two'), FunctionParameter('three')]))

        cc.compile([CodeBlock([CodeLine('foo(bar.food,baz, 1K)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_type(), FunctionType))
        self.assertTrue(isinstance(cc.get_output()[0].get_name(), Name))
        self.assertTrue(isinstance(cc.get_output()[0].get_params(), list))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 3)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[1], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[2], FunctionParameter))
        self.assertEquals(cc.get_output()[0].get_name().get_name(), 'foo')
        self.assertEquals(cc.get_output()[0].get_type().get_type(), 'inline')
        self.assertEquals(cc.get_output()[0].get_params()[0].get_symbol(), 'bar.food')
        self.assertEquals(cc.get_output()[0].get_params()[1].get_symbol(), 'baz')
        self.assertEquals(int(cc.get_output()[0].get_params()[2].get_value()), 1024)

        # reset state
        st.reset_state()

    def testSizeOfName(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(Foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(cc.get_output()[0].get_params()[0].get_symbol().get_name(), 'Foo')

    def testSizeOfStructRef(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(struct bar)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Struct))
        self.assertEquals(cc.get_output()[0].get_params()[0].get_symbol().get_name(), 'struct bar')

    def testSizeOfFullStruct(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(struct baz { byte b[10], c })')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Struct))
        self.assertEquals(cc.get_output()[0].get_params()[0].get_symbol().get_name(), 'struct baz')

    def testSizeOfDottedVarReference(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(foo.bar.baz)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(cc.get_output()[0].get_params()[0].get_symbol().get_name(), 'foo.bar.baz')

    def testNestedSizeOf(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(sizeof(foo))')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionCall))
        self.assertTrue(len(cc.get_output()[0].get_params()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(cc.get_output()[0].get_params()[0].get_params()[0].get_symbol().get_name(), 'foo')

    def testSizeOfImmediate(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof(0x0012)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_params()[0].get_value()), 0x0012)

    def testSizeOfString(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof("hello world")')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_value(), StringValue))
        self.assertEquals(str(cc.get_output()[0].get_params()[0].get_value()), 'hello world')

    def testSizeOfArray(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('sizeof({ 1, 2, 3 })')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_value(), ArrayValue))

    def testHiOfImmediate(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('hi(0x0012)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_params()[0].get_value()), 0x0012)

    def testHiOfVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('hi(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(str(cc.get_output()[0].get_params()[0].get_symbol().get_name()), 'foo')


    def testHiOfStructReference(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('hi(foo.bar.baz)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(str(cc.get_output()[0].get_params()[0].get_symbol().get_name()), 'foo.bar.baz')
    def testLoOfImmediate(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('lo(0x0012)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_params()[0].get_value()), 0x0012)

    def testLoOfVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('lo(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(str(cc.get_output()[0].get_params()[0].get_symbol().get_name()), 'foo')


    def testLoOfStructReference(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('lo(foo.bar.baz)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(str(cc.get_output()[0].get_params()[0].get_symbol().get_name()), 'foo.bar.baz')
    def testNyHiOfImmediate(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('nyhi(0x12)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_params()[0].get_value()), 0x0012)

    def testNyHiOfVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('nyhi(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(str(cc.get_output()[0].get_params()[0].get_symbol().get_name()), 'foo')


    def testNyHiOfStructReference(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('nyhi(foo.bar.baz)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(str(cc.get_output()[0].get_params()[0].get_symbol().get_name()), 'foo.bar.baz')
    def testNyLoOfImmediate(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('nylo(0x12)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_value(), NumericValue))
        self.assertEquals(int(cc.get_output()[0].get_params()[0].get_value()), 0x0012)

    def testNyLoOfVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('nylo(foo)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(str(cc.get_output()[0].get_params()[0].get_symbol().get_name()), 'foo')


    def testNyLoOfStructReference(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('nylo(foo.bar.baz)')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(str(cc.get_output()[0].get_params()[0].get_symbol().get_name()), 'foo.bar.baz')
    def testHiLoOfVariable(self):
        cc = Session().compiler()

        cc.compile([CodeBlock([CodeLine('hi(lo(foo))')])])
        self.assertTrue(isinstance(cc.get_output()[0], FunctionCall))
        self.assertTrue(len(cc.get_output()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0], FunctionCall))
        self.assertTrue(len(cc.get_output()[0].get_params()[0].get_params()) == 1)
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_params()[0], FunctionParameter))
        self.assertTrue(isinstance(cc.get_output()[0].get_params()[0].get_params()[0].get_symbol(), Name))
        self.assertEquals(cc.get_output()[0].get_params()[0].get_params()[0].get_symbol().get_name(), 'foo')


