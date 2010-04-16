"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

import os
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
        self._exprs.extend(self._get_basic_exprs())

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

    def _get_basic_exprs(self):

        basic_exprs = []

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
        variable_declaration = Optional(shared_.setResultsName('shared')) + \
                               type_ + \
                               name_.setResultsName('name') + \
                               Optional(lbracket_ + \
                                        Optional(size_.setResultsName('size')) + \
                                        rbracket_).setResultsName('array') + \
                            Optional(colon_ + address_.setResultsName('address'))
        variable_declaration.setParseAction(VariableDeclaration())

        # variable initialization
        variable_initialization = variable_declaration.setResultsName('variable') + \
                                  Optional(equal_ + value_.setResultsName('value'))
        variable_initialization.setParseAction(VariableInitialization())

        """
        # standard variable
        initialize_variable = basic_variable + \
                            Optional(equal_ + number_.setResultsName('value'))
        initialize_variable.setParseAction(InitializeVariable())

        # variable list
        variable_list_item_declare = label_.setResultsName('label') + \
                            Optional(colon_ + number_.setResultsName('address'))
        variable_list_item_declare.setParseAction(self._variable_list_item_declare)

        variable_list_item = variable_list_item_declare + \
                             Optional(equal_ + number_.setResultsName('value'))
        variable_list_item.setParseAction(self._variable_list_item)

        variable_list = standard_variable.setResultsName('var') + \
                        OneOrMore(Suppress(',') + variable_list_item).setResultsName('var_list')
        variable_list.setParseAction(self._variable_list)

        # arrays
        
        # define quoted string for the messages
        array_value_string = Word(printables)
        array_value_string = quotedString(array_value_string)
        array_value_string.setParseAction(removeQuotes)

        # define array value block
        array_value = Optional(OneOrMore(label_ + Suppress(':')).setResultsName('label_list')) + \
                      number_.setResultsName('number')
        array_value.setParseAction(self._array_value)

        array_value_block = lbrace_ + \
                            array_value.setResultsName('value') + \
                            ZeroOrMore(Suppress(',') + array_value).setResultsName('value_list') + \
                            rbrace_
        array_value_block.setParseAction(self._array_value_block)

        # array declaration
        array_variable_string = Optional(shared_.setResultsName('shared')) + \
                         type_.setResultsName('type') + \
                         label_.setResultsName('label') + \
                         lbracket_ + \
                         Optional(number_.setResultsName('size')) + \
                         rbracket_ + \
                         Optional(colon_ + number_.setResultsName('address')) + \
                         Optional(equal_ + array_value_string.setResultsName('value'))
        array_variable_string.setParseAction(self._array_variable_string)
        array_variable_block = Optional(shared_.setResultsName('shared')) + \
                         type_.setResultsName('type') + \
                         label_.setResultsName('label') + \
                         lbracket_ + \
                         Optional(number_.setResultsName('size')) + \
                         rbracket_ + \
                         Optional(colon_ + number_.setResultsName('address')) + \
                         Optional(equal_ + array_value_block).setResultsName('value')
        array_variable_block.setParseAction(self._array_variable_block)

        # struct declaration
        struct_block = lbrace_ + \
                       OneOrMore(standard_variable | \
                                 variable_list | \
                                 array_variable_string | \
                                 array_variable_block).setResultsName('var_list') + \
                       rbrace_
        struct_block.setParseAction(self._struct_block)

        # this separates 'struct foo' out for use in typedefs as well
        struct_type = struct_ + label_.setResultsName('type')

        # this is for the declaration of variables with a struct type
        struct_label_item = label_.setResultsName('label') + \
                            Optional(colon_  + number_.setResultsName('address'))
        struct_label_item.setParseAction(self._struct_label_item)
        struct_label_list = struct_label_item.setResultsName('label') + \
                            ZeroOrMore(Suppress(',') + struct_label_item).setResultsName('label_list')

        # full struct variable declaration
        struct_variable = Optional(shared_.setResultsName('shared')) + \
                        struct_type + \
                        Optional(colon_ + number_.setResultsName('address')) + \
                        struct_block.setResultsName('members') + \
                        Optional(struct_label_list)
        struct_variable.setParseAction(self._struct_variable)

        # typedefs
        basic_typedef = typedef_ + basic_variable
        """

        # put the expressions in the compiler exprs
        basic_exprs.append(('variable_declaration', variable_declaration))
        basic_exprs.append(('variable_initialization', variable_initialization))
        """
        self._compiler_exprs.append(('standard_variable', standard_variable))
        self._compiler_exprs.append(('variable_list', variable_list))
        self._compiler_exprs.append(('array_variable_string', array_variable_string))
        self._compiler_exprs.append(('array_variable_block', array_variable_block))
        self._compiler_exprs.append(('struct_block', struct_block))
        self._compiler_exprs.append(('struct_variable', struct_variable))
        """

        return basic_exprs


class ParserNode(object):
    """
    defines the interface of all parser node functors
    """
    def __call__(self, pstring, location, tokens):
        pass

class VariableDeclaration(ParserNode):
    """
    handles parsing a basic variable declaration
    """
    def __call__(self, pstring, location, tokens):
        if 'type' not in tokens.keys():
            raise ParseFatalException('variable declaration is missing type')

        if 'name' not in tokens.keys():
            raise ParseFatalException('variable declaration is missing name')

        # is this a struct type?
        struct = 'struct' in tokens.keys()

        # is this a shared variable?
        shared = 'shared' in tokens.keys()

        # is this an array variable?
        array = 'array' in tokens.keys()

        size = None
        if array and 'size' in tokens.keys():
            size = tokens.size
       
        # is there an address for this variable defined?
        address = None
        if 'address' in tokens.keys():
            address = tokens.address
       
        type_name = tokens.type
        if struct:
            type_name = 'struct ' + type_name

        # check to see if the type is registered
        if TypeRegistry.instance()[type_name] is None:
            raise ParseFatalException('unknown type %s' % tokens.type)

        # check the symbol table to see if the variable is already declared
        if SymbolTable.instance()[tokens.name] != None:
            raise ParseFatalException('variable "%s" is already declared' % tokens.name)

        # create the variable, this adds it to the symbol table
        return Variable(tokens.name, TypeRegistry.instance()[type_name], 
                        shared, address, array, size)

class VariableInitialization(ParserNode):
    """
    handles parsing a variable initialization
    """
    def __call__(self, pstring, location, tokens):
        if 'variable' not in tokens.keys():
            raise ParseFatalException('variable assignment missing variable')

        if 'value' not in tokens.keys():
            raise ParseFatalException('variable assignment missing value')

        return AssignValue(tokens.variable, tokens.value)
