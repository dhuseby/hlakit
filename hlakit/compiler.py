"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

import os
import sys
from pyparsing import *
from cpu import *
from platform import *
from tokens import *
from types import *
from symbols import *
from values import *

class Compiler(object):

    def __init__(self, options = None, logger = None):

        # init the base class
        super(Compiler, self).__init__()

        # initialize the platform and cpu
        self._platform = options.get_platform(logger)
        self._cpu = options.get_cpu(logger)

        # store our options
        self._options = options

        # initialize the map of expressions
        self._exprs = []

        # compiler symbols table
        self._symbols = {}

        # the parser used
        self._parser = None

        # build the type registry
        self._init_compiler_types()

        # build the compiler expressions
        self._init_compiler_exprs()

    def get_exprs(self):
        return self._exprs

    def compile(self, tokens):
        # initialize the parser
        expr_or = Or([])
        for e in self._exprs:
            expr_or.append(e[1])

        # build final parser
        self._parser = ZeroOrMore(expr_or)

        cc_tokens = []
        for token in tokens:
            if type(token) is CodeBlock:
                # add in the tokens from the compiler parser
                print "Compiling:\n" + str(token)
                cc_tokens.extend(self._parser.parseString(str(token), parseAll=True))
            else:
                # non-CodeBlock tokens get passed through because they are
                # probably linker related (e.g. #incbin, #bank.tell, etc)
                cc_tokens.append(token)

        return cc_tokens

    def _init_compiler_exprs(self):

        # add in the expressions for parsing the basic structures of the language
        self._exprs.extend(self._get_variable_exprs())
        self._exprs.extend(self._get_conditional_exprs())
        self._exprs.extend(self._get_function_exprs())

        # add in the platform and cpu preprocessor exprs
        self._init_platform_exprs()
        self._init_cpu_exprs()

    def _init_platform_exprs(self):
        # this gets all of the compiler expressions from the platform 
        # specific defintion class
        if self._platform:
            self._exprs.extend(self._platform.get_compiler_exprs())

    def _init_cpu_exprs(self):
        # this gets all fo the compiler expressions from the cpu specific
        # definition class
        if self._cpu:
            self._exprs.extend(self._cpu.get_compiler_exprs())

    def _init_compiler_types(self):
        # register the basic types
        ByteType.register()
        CharType.register()
        BoolType.register()
        WordType.register()

        self._init_platform_types()
        self._init_cpu_types()

    def _init_platform_types(self):
        # register the platform specific types
        if self._platform:
            self._platform.init_compiler_types()

    def _init_cpu_types(self):
        # register the cpu specific types
        if self._cpu:
            self._cpu.init_compiler_types()

    def _get_variable_exprs(self):

        variable_exprs = []

        # punctuation
        equal_ = Suppress('=')
        colon_ = Suppress(':')
        lbrace_ = Suppress('{')
        rbrace_ = Suppress('}')
        lbracket_ = Suppress('[')
        rbracket_ = Suppress(']')
        
        # keywords
        shared_ = Keyword('shared')
        typedef_ = Keyword('typedef')
        struct_ = Keyword('struct')

        # name
        name_ = Word(alphas, alphanums + '_')

        # type
        type_ = Word(alphas, alphanums + '_')

        # address
        address_ = NumericValue.exprs()

        # size
        size_ = NumericValue.exprs()

        # value
        value_ = Value.exprs()
       
        # variable declaration
        # TODO: add support for multi-dimensioned arrays 
        variable_stub = name_.setResultsName('name') + \
                        Optional(lbracket_ + \
                            Optional(size_.setResultsName('size')) + \
                            rbracket_).setResultsName('array') + \
                        Optional(colon_ + address_.setResultsName('address'))
        variable_stub.setParseAction(VariableStub())

        # variable initialization
        variable_initialization = variable_stub.setResultsName('variable') + \
                                  Optional(equal_ + value_.setResultsName('value'))

        # defines simple variable decls
        simple_variable_decl = Optional(shared_.setResultsName('shared')) + \
                               Optional(struct_.setResultsName('struct')) + \
                               type_.setResultsName('type') + \
                               Group(variable_initialization + \
                                   ZeroOrMore(Suppress(',') + \
                                       variable_initialization)).setResultsName('vars')

        # struct member var
        struct_var_stub = name_.setResultsName('name') + \
                          Optional(lbracket_ + \
                                   Optional(size_.setResultsName('size')) + \
                                   rbracket_).setResultsName('array')
        struct_var_stub.setParseAction(VariableStub(False))

        # struct members
        struct_member_decl = Optional(struct_.setResultsName('struct')) + \
                             type_.setResultsName('type') + \
                             Group(struct_var_stub + \
                                 ZeroOrMore(Suppress(',') + \
                                     struct_var_stub)).setResultsName('vars')

        # parses full struct definitions and var decls
        struct_type_decl = Optional(typedef_.setResultsName('typedef')) + \
                           Optional(shared_.setResultsName('shared')) + \
                           struct_.setResultsName('struct') + \
                           type_.setResultsName('type') + \
                           Optional(colon_ + address_.setResultsName('address')) + \
                           lbrace_ + \
                           OneOrMore(struct_member_decl).setResultsName('members') + \
                           rbrace_ 
        
        # typedef
        typedef_declaration = typedef_.setResultsName('typedef') + \
                              Optional(shared_.setResultsName('shared')) + \
                              Optional(struct_.setResultsName('struct')) + \
                              type_.setResultsName('type') + \
                              name_.setResultsName('name') + \
                              Optional(lbracket_ + \
                                       Optional(size_.setResultsName('size')) + \
                                       rbracket_).setResultsName('array') + \
                              Optional(colon_ + address_.setResultsName('address'))
        typedef_declaration.setParseAction(TypedefDeclaration())

        # variable decls
        simple_variable_decl.setParseAction(VariableDeclaration())
        struct_type_decl.setParseAction(StructDeclaration())
        struct_member_decl.setParseAction(StructMemberDeclaration())

        # put the expressions in the compiler exprs
        variable_exprs.append(('struct_var_stub', struct_var_stub))
        variable_exprs.append(('variable_stub', variable_stub))
        variable_exprs.append(('simple_variable_decl', simple_variable_decl))
        variable_exprs.append(('struct_declaration', struct_type_decl))
        variable_exprs.append(('typedef_declaration', typedef_declaration))

        return variable_exprs

    def _get_function_exprs(self):

        function_exprs = []

        # punctuation
        lbrace_ = Suppress('{')
        rbrace_ = Suppress('}')
        lparen_ = Suppress('(')
        rparen_ = Suppress(')')

        # keywords
        function_ = Keyword('function')
        interrupt_ = Keyword('interrupt')
        inline_ = Keyword('inline')
        noreturn_ = Keyword('noreturn')

        # name
        name_ = Word(alphas, alphanums + '_')

        # immediate
        immediate_ = Suppress('#') + NumericValue.exprs()

        # register
        register_ = Or([Keyword('a'),
                        Keyword('x'),
                        Keyword('y'),
                        Keyword('p'),
                        Keyword('s'),\
                        Keyword('pc')])

        # opcodes
        opcode_ = Or([Keyword('ldy'),
                      Keyword('lda')])

        # parameter
        parameter_ = Or([immediate_, register_])
        
        # assembly
        assembly_line = opcode_.setResultsName('opcode') + \
                        Optional(parameter_.setResultsName('first') + \
                                 Optional(Suppress(',') + \
                                          parameter_.setResultsName('second')))

        # function expression
        function_definition = Or([function_, interrupt_, inline_]).setResultsName('type') + \
                              Optional(noreturn_).setResultsName('noreturn') + \
                              name_.setResultsName('name') + \
                              lparen_ + \
                              Optional(name_ + ZeroOrMore(Suppress(',') + name_)).setResultsName('params') + \
                              rparen_ + \
                              lbrace_ + \
                              ZeroOrMore(assembly_line).setResultsName('code') + \
                              rbrace_
        function_definition.setParseAction(FunctionDeclaration())

        # put the expressions in the list
        function_exprs.append(('function_defintion', function_definition))

        return function_exprs

    def _get_conditional_exprs(self):

        conditional_exprs = []

        return conditional_exprs




class ParserNode(object):
    """
    defines the interface of all parser node functors
    """
    def __call__(self, pstring, location, tokens):
        pass

class VariableStub(ParserNode):
    """
    handles parsing a variable name, it's optional array size, and optinal
    address
    """
    def __init__(self, define=True):
        self._define = define

    def __call__(self, pstring, location, tokens):
        if 'name' not in tokens.keys():
            raise ParseFatalException('variable declaration missing name')

        # is this an array variable?
        array = 'array' in tokens.keys()

        # get the array size if it exists
        size = None
        if array and 'size' in tokens.keys():
            size = tokens.size
 
        # is there an address for this variable defined?
        address = None
        if 'address' in tokens.keys():
            address = tokens.address

        # check the symbol table to see if the variable is already declared
        if SymbolTable.instance()[tokens.name] != None and self._define:
            raise ParseFatalException('variable "%s" is already declared' % tokens.name)

        # create the variable, leave the type unset for now
        return Variable(tokens.name, None, False, address, array, size, self._define)

class StructDeclaration(ParserNode):
    """
    handles parsing struct type declarations
    """
    def __call__(self, pstring, location, tokens):
        if 'type' not in tokens.keys():
            raise ParseFatalException('variable declaration is missing type')

        # is this a struct type?
        if 'struct' not in tokens.keys():
            raise ParseFatalException('struct decl missing struct keyword')

        # is this a typedef?
        typedef = 'typedef' in tokens.keys()

        # is this a shared variable?
        shared = 'shared' in tokens.keys()

        type_ = None
        
        # get address if there is one
        address = None
        if 'address' in tokens.keys():
            address = tokens.address

        # we need to look up/create the struct type
        t = 'struct ' + tokens.type
        if TypeRegistry.instance()[t] is not None:
            raise ParseFatalException('struct type already defined')
        
        # create the type
        type_ = StructType(t)

        # add the members
        for m in tokens.members:
            # add the member type to the struct type
            type_.add_member(m.get_name(), m.get_type())

        # if there is a typedef keyword, then typedef the name
        # of the struct to 'struct name' so that just the name
        # can be used in the code
        if typedef:
            TypedefType(tokens.type, type_.get_name(), address, True)

        return []


class StructMemberDeclaration(ParserNode):
    """
    handles parsing struct members
    """
    def __call__(self, pstring, location, tokens):
        if 'type' not in tokens.keys():
            raise ParseFatalException('variable declaration is missing type')

        # is this a struct type?
        struct = 'struct' in tokens.keys()

        type_ = None
        if struct:
            # we need to look up/create the struct type
            t = 'struct ' + tokens.type
            if TypeRegistry.instance()[t] is None:
                raise ParseFatalException('cannot define new structs when declaring a variable')
            # look up the type
            type_ = TypeRegistry.instance()[t]

            # make sure there are no members being defined
            if len(tokens.members):
                raise ParseFatalError('trying to redefine struct %s' % name_)

        else:
            # process a simple variable decl
            t = tokens.type

            if TypeRegistry.instance()[t] is None:
                raise ParseFatalException('unknown type: %s' % t)

            # make sure the first variable is declared
            if len(tokens.vars) == 0:
                raise ParseFatalException('var decl is missing')

            type_ = TypeRegistry.instance()[t]

        if type_ is None:
            raise ParseFataException('invalid type in declaration')

        # build the variables if there are any
        ret = []
        for v in tokens.vars:
            if isinstance(v, Variable):
                # fill in what we know about the first variable
                v.set_type(type_)

                # add it to the list of tokens to return
                ret.append(v)
            else:
                raise ParseFatalException('unknown token type in var list declaration')

        # return the tokens list
        return ret

class VariableDeclaration(ParserNode):
    """
    handles parsing a basic variable declaration
    """
    def __call__(self, pstring, location, tokens):
        if 'type' not in tokens.keys():
            raise ParseFatalException('variable declaration is missing type')

        # is this a typedef?
        typedef = 'typedef' in tokens.keys()
        
        # is this a shared variable?
        shared = 'shared' in tokens.keys()

        # is this a struct type?
        struct = 'struct' in tokens.keys()

        type_ = None
        if struct:
            # get address if there is one
            address = None
            if 'address' in tokens.keys():
                address = tokens.address

            # we need to look up/create the struct type
            t = 'struct ' + tokens.type
            if TypeRegistry.instance()[t] is None:
                raise ParseFatalException('cannot define new structs when declaring a variable')
            # look up the type
            type_ = TypeRegistry.instance()[t]

            # make sure there are no members being defined
            if len(tokens.members):
                raise ParseFatalError('trying to redefine struct %s' % name_)

        else:
            # process a simple variable decl
            t = tokens.type

            if TypeRegistry.instance()[t] is None:
                raise ParseFatalException('unknown type: %s' % t)

            # make sure the first variable is declared
            if len(tokens.vars) == 0:
                raise ParseFatalException('var decl is missing')

            type_ = TypeRegistry.instance()[t]

        if type_ is None:
            raise ParseFataException('invalid type in declaration')

        # build the variables if there are any
        ret = []
        for v in tokens.vars:
            if isinstance(v, Variable):
                # fill in what we know about the first variable
                v.set_type(type_)
                v.set_shared(shared)

                # add it to the list of tokens to return
                ret.append(v)
            elif isinstance(v, Value):
                # create an assign token for the previous variable
                ret.append(AssignValue(ret[-1], v))
            elif isinstance(v, AssignValue):
                # if it is an already parsed value assing, just append
                # it to the list of tokens
                ret.append(v)
            else:
                raise ParseFatalException('unknown token type in var list declaration')

        # return the tokens list
        return ret

class TypedefDeclaration(ParserNode):
    """
    handles parsing a typedef
    """
    def __call__(self, pstring, location, tokens):
        if 'typedef' not in tokens.keys():
            raise ParseFatalException('typedef missing keyword')

        if 'type' not in tokens.keys():
            raise ParseFatalException('original type missing in typedef')

        if 'name' not in tokens.keys():
            raise ParseFatalException('aliased type missing in typedef')

        # is the original type shared?
        shared = 'shared' in tokens.keys()

        # is this a struct type?
        struct = 'struct' in tokens.keys()

        # is this an array variable?
        array = 'array' in tokens.keys()

        # get the array size if it exists
        size = None
        if array and 'size' in tokens.keys():
            size = tokens.size

        # is there an address for this variable defined?
        address = None
        if 'address' in tokens.keys():
            address = tokens.address

        # get the original type name
        type_name = tokens.type
        if struct:
            type_name = 'struct ' + type_name

        # check to see if the type is registered
        if TypeRegistry.instance()[type_name] is None:
            raise ParseFatalException('cannot typedef unknown type %s' % type_name)

        # create the typedef, it handles registering the typedef
        TypedefType(tokens.name, type_name, address, struct, array, size)

        # return no tokens
        return []

class FunctionDeclaration(ParserNode):
    """
    handles parsing function declarations
    """
    def __call__(self, pstring, location, tokens):
        import pdb; pdb.set_trace()
        return []

        """
        if 'name' not in tokens.keys():
            raise ParseFatalException('variable declaration missing name')

        # is this an array variable?
        array = 'array' in tokens.keys()

        # get the array size if it exists
        size = None
        if array and 'size' in tokens.keys():
            size = tokens.size
 
        # is there an address for this variable defined?
        address = None
        if 'address' in tokens.keys():
            address = tokens.address

        # check the symbol table to see if the variable is already declared
        if SymbolTable.instance()[tokens.name] != None and self._define:
            raise ParseFatalException('variable "%s" is already declared' % tokens.name)

        # create the variable, leave the type unset for now
        return Variable(tokens.name, None, False, address, array, size, self._define)
        """

