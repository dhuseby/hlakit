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

        # build the compiler expressions
        self._init_compiler_exprs()

        # build the type registry
        self._init_compiler_types()

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

