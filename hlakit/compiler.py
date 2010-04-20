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
        type_name_ = Word(alphas, alphanums + '_')
        type_ = Optional(Keyword('struct').setResultsName('struct')) + \
                type_name_.setResultsName('type')

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
        variable_declaration = Optional(shared_.setResultsName('shared')) + \
                               type_ + \
                               variable_initialization
        variable_declaration.setParseAction(VariableDeclaration())

        # variable list
        variable_list = variable_declaration + \
                        OneOrMore(Suppress(',') + \
                                  variable_initialization)
        variable_list.setParseAction(VariableListDeclaration())

        # typedef
        typedef_declaration = typedef_.setResultsName('typedef') + \
                              Optional(shared_.setResultsName('shared')) + \
                              type_ + \
                              name_.setResultsName('alias')
        typedef_declaration.setParseAction(TypedefDeclaration())

        # put the expressions in the compiler exprs
        variable_exprs.append(('variable_stub', variable_stub))
        variable_exprs.append(('variable_declaration', variable_declaration))
        variable_exprs.append(('variable_list', variable_list))
        variable_exprs.append(('typedef_declaration', typedef_declaration))

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

        if 'variable' not in tokens.keys():
            raise ParseFatalException('variable declaration is missing')

        # is this a shared variable?
        shared = 'shared' in tokens.keys()

        # is this a struct type?
        struct = 'struct' in tokens.keys()

        # get the type name
        type_name = tokens.type
        if struct:
            type_name = 'struct ' + type_name

        # get the value if there is one
        value = None
        if 'value' in tokens.keys():
            value = tokens.value

        # get the variable
        v = tokens.variable

        # check to see if the type is registered
        if TypeRegistry.instance()[type_name] is None:
            raise ParseFatalException('unknown type %s' % type_name)

        # check the symbol table to make sure it is already declared
        if SymbolTable.instance()[v.get_name()] == None:
            raise ParseFatalException('variable "%s" is not properly declared' % v.get_name())

        # make sure we have a variable
        if not isinstance(v, Variable):
            raise ParseFatalException('variable declaration is the wrong type')

        # we need to update the variable declaration to fill out the
        # rest of its data members
        v.set_type(TypeRegistry.instance()[type_name])
        v.set_shared(shared)

        # if there was a value, then return a list of tokens, one for
        # the variable and one for the assignment of the variable
        if value:
            return [v, AssignValue(v, value)]

        # return the updated variable
        return v

class VariableListDeclaration(ParserNode):
    """
    handles parsing a variable name, it's optional array size, and optinal
    address
    """
    def __call__(self, pstring, location, tokens):
        if len(tokens) < 1:
            raise ParseFatalException('variable list missing first variable')

        if not isinstance(tokens[0], Variable):
            raise ParseFatalException('first object in variable list not a variable')

        # get the first variable since it has all of the extra info that
        # applies to the rest of the variables
        first = tokens[0]

        # start the array of tokens to return
        ret = [ first ]

        for i in range(1,len(tokens)):
            # get the next object in the list
            t = tokens[i]

            if isinstance(t, Variable):
                # fill in what we know about the first variable
                t.set_type(first.get_type())
                t.set_shared(first.is_shared())

                # add it to the list of tokens to return
                ret.append(t)
            elif isinstance(t, Value):
                # create an assign token for the previous variable
                ret.append(AssignValue(ret[-1], t))
            elif isinstance(t, AssignValue):
                # if it is an already parsed value assing, just append
                # it to the list of tokens
                ret.append(t)
            else:
                raise ParseFatalException('unknown token type in var list declaration')

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

        if 'alias' not in tokens.keys():
            raise ParseFatalException('aliased type missing in typedef')

        # is the original type shared?
        shared = 'shared' in tokens.keys()

        # is this a struct type?
        struct = 'struct' in tokens.keys()

        # get the original type name
        type_name = tokens.type
        if struct:
            type_name = 'struct ' + type_name

        # check to see if the type is registered
        if TypeRegistry.instance()[type_name] is None:
            raise ParseFatalException('cannot typedef unknown type %s' % type_name)

        # create the typedef, it handles registering the typedef
        TypedefType(tokens.alias, type_name)

        # return no tokens
        return []


