#!/usr/bin/env python

import os
import sys

from optparse import OptionGroup
from optparse import OptionParser
from pyparsing import *


# get the directory that we're running in
script_dir = os.path.dirname(os.path.realpath(__file__))
include_dirs = []
lib_dirs = []


class Options(object):
    def __init__(self):
        self._options = None
        self._args = None

        parser = OptionParser()
        parser.add_option('--cpu', default=None, dest='cpu')
        parser.add_option('--platform', default=None, dest='platform')

        (self._options, self._args) = parser.parse_args()

    def __getitem__(self, key):
        if self._options.has_key(key):
            return self._options[key]

        raise KeyError(key)

    def __setitem__(self, key, value):
        self._options[key] = value

    def get_args(self):
        return self._args


class Compiler(object):

    def __init__(self):
        self._expressions = {}

    def _init_include_expr(self):

        # define include literal
        self._include = Literal('#include')

        # ==> #include "foo.h"

        # define a quoted file path 
        self._literal_file_path = quotedString(Word(alphanums + '/.'))
        self._literal_file_path.setParseAction(removeQuotes)

        # define a literal include line
        self._literal_include_line = Suppress(self._include) + self._literal_file_path
        #self._literal_include_line.setParseAction(_include_literal_file)

        # ==> #include <foo.h>

        # define an angle bracketed file path
        self._implied_file_path = Supress(Literal('<')) + Word(alphanums + '/.') + Supress(Literal('>'))
        
        # define an implied include line
        self._implied_include_line = Suppress(self._include) + self._implied_file_path
        #self._implied_include_line.setParseAction(_include_implied_file)

        # build the "include" expression in the top level map of expressions
        self._expressions['include'] = Or([self._literal_include_line, self._implied_include_line])

    def compile(self, f):
        pass


def main():
    options = Options()
    print options._options
    print options._args


if __name__ == "__main__":
    
    sys.exit(main())
