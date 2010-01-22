#!/usr/bin/env python

import os
import sys
import optparse
import hlakit

from pyparsing import *

# globals
HLAKIT_VERSION = "0.0.1"

class Options(object):
    def __init__(self):
        self._options = None
        self._args = None

        # calculate the script dir
        self._script_dir = os.path.dirname(os.path.realpath(__file__))

        parser = optparse.OptionParser(version = "%prog " + HLAKIT_VERSION)
        parser.add_option('--cpu', default=None, dest='cpu')
        parser.add_option('--platform', default=None, dest='platform')
        parser.add_option('-L', '--lib', action="append", default=[], dest='lib')
        parser.add_option('-I', '--include', action="append", default=[], dest='include')

        (self._options, self._args) = parser.parse_args()

    def get_include_dirs(self):
        return self._options.include

    def get_lib_dirs(self):
        return self._options.lib

    def get_options(self):
        return self._options

    def get_args(self):
        return self._args

    def get_script_dir(self):
        return self._script_dir

class HLAParser(hlakit.Parser):

    class StateFrame(object):
        """
        Helper class that holds an entire state frame
        """
        def __init__(self, f, exprs):
           
            # the current file name
            self._file = f

           # initialize the pyparsing parser as ZeroOrMore(Or())
            # of all of the expressions 
            expr_or = Or([])
            for e in exprs.iteritems():
                expr_or.append(e[1])
            
            self._parser = ZeroOrMore(expr_or)


    def __init__(self, options = None):

        super(HLAParser, self).__init__()

        # store the options
        self._options = options

        # state stack for tracking the current file being parsed
        self._state_stack = []

        # current state frame
        self._state = None

        # initialize the expressions 
        self._exprs = {}

        # load up all of the expression creator objects 
        self._preprocessor = hlakit.Preprocessor(self)

        # add them to the expressions map
        self._exprs.update(self._preprocessor.get_exprs())

    def get_options(self):
        return self._options

    def _do_parse(self):
        # parse the file
        print "Parsing: %s" % self._state._file.name
        tokens = self._state._parser.parseFile(self._state._file, True)
        print "Done parsing: %s" % self._state._file.name
        return tokens

    def parse(self, f):

        # push our current state if we're recursively parsing
        if self._state:
            # push our current state on the stack
            self._state_stack.append(self._state)

        # set up a new context
        self._state = HLAParser.StateFrame(f, self._exprs)

        # do the parse
        tokens = self._do_parse()

        # restore previous state if there is one
        if len(self._state_stack):
            self._state = self._state_stack.pop()

        return tokens
        
def main():
    options = Options()
    print options._options
    print options._args

    p = HLAParser(options)
    for f in options.get_args():

        # calculate the correct path to the file 
        if f[0] == '/':
            fpath = f
        else:
            fpath = os.path.join(options.get_script_dir(), f)

        # open the file
        inf = open(fpath, 'r')

        # parse the file 
        tokens = p.parse(inf)

        # close the file
        inf.close()

        # dump the tokens
        print tokens

if __name__ == "__main__":
    
    sys.exit(main())
