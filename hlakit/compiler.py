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

        # full declaration
        variable_declaration = Forward()

        # defines simple variable decls
        simple_variable_decl = Optional(typedef_.setResultsName('typedef')) + \
                               Optional(shared_.setResultsName('shared')) + \
                               Optional(struct_.setResultsName('struct')) + \
                               type_.setResultsName('type') + \
                               Group(variable_initialization + \
                                     ZeroOrMore(Suppress(',') + \
                                          variable_initialization)).setResultsName('vars')
        # parses full struct definitions and var decls
        struct_variable_decl = Optional(typedef_.setResultsName('typedef')) + \
                               Optional(shared_.setResultsName('shared')) + \
                               struct_.setResultsName('struct') + \
                               type_.setResultsName('type') + \
                               Optional(colon_ + address_.setResultsName('address')) + \
                               lbrace_ + \
                               OneOrMore(variable_declaration).setResultsName('members') + \
                               rbrace_ 
        # all variable rules
        variable_declaration << (struct_variable_decl | \
                                 simple_variable_decl)
        variable_declaration.setParseAction(VariableDeclaration())

        # put the expressions in the compiler exprs
        variable_exprs.append(('variable_stub', variable_stub))
        variable_exprs.append(('variable_declaration', variable_declaration))

        return variable_exprs


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
        if SymbolTable.instance()[tokens.name] != None:
            raise ParseFatalException('variable "%s" is already declared' % tokens.name)

        # create the variable, leave the type unset for now
        return Variable(tokens.name, None, False, address, array, size)


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
                # create the type
                type_ = StructType(t)

                # add the members
                for m in tokens.members:
                    # make sure that the global symbol of the struct
                    # member is deleted
                    SymbolTable.instance().remove(m.get_name())

                    # add the member type to the struct type
                    type_.add_member(m.get_name(), m.get_type())
            else:
                # look up the type
                type_ = TypeRegistry.instance()[t]

                # make sure there are no members being defined
                if len(tokens.members):
                    raise ParseFatalError('trying to redefine struct %s' % name_)

            # DOES THIS GO HERE?
            #if typedef:
            #    TypedefType(tokens.type, type_.get_name(), address)

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
            # PROBABLY NEED TO PUT TYPEDEF HERE SOMEWHERE
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



