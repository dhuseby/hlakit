"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

import os
from cpu import *
from machine import *

from pyparsing import *

class Compiler(object):

    def __init__(self, options = None, logger = None):

        # init the base class
        super(Compiler, self).__init__()

        # initialize the machine and cpu
        self._machine = options.get_machine(logger)
        self._cpu = options.get_cpu(logger)

        # store our options
        self._options = options

        # initialize the map of expressions
        self._exprs = []

        # compiler symbols table
        self._symbols = {}

        # build the compiler expressions
        self._init_compiler_exprs()

    def get_exprs(self):
        return self._exprs

    def compile(self, tokens):
        return tokens

    def _init_compiler_exprs(self):
        """
        # add in the generic HLA expressions
        self._init_function_exprs()
        self._init_while_exprs()
        self._init_for_exprs()
        self._init_if_exprs()
        # add in the machine and cpu preprocessor exprs
        self._init_machine_exprs()
        self._init_cpu_exprs()
        # note that generic exprs must be last
        self._init_generic_exprs()
        """
        pass


