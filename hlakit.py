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
        self._app_dir = os.path.dirname(os.path.realpath(__file__))

        parser = optparse.OptionParser(version = "%prog " + HLAKIT_VERSION)
        parser.add_option('--cpu', default=None, dest='cpu',
                          help='specifying the cpu activates the assembly opcodes for the given cpu.\n'
                               'you probably want to specify a platform instead if you are coding for\n'
                               'a specific machine.  if you want to just create a generic binary for\n'
                               'a given cpu, then this is the option for you.')
        parser.add_option('--platform', default=None, dest='platform',
                          help='specifying the platform activates platform specific preprocessor directives\n'
                               'and implies the cpu so you don\'t have to specify the cpu.')
        parser.add_option('-L', '--lib', action="append", default=[], dest='lib',
                          help='specify directories to search for source files implementing board \n'
                               'support functions')
        parser.add_option('-I', '--include', action="append", default=[], dest='include',
                          help='specify directories to search for include files')

        (self._options, self._args) = parser.parse_args()

        # check for required options
        if (not self._options.platform) and (not self._options.cpu):
            parser.error('You must specify either a platform with --platform or a cpu with --cpu')

    def get_include_dirs(self):
        return self._options.include

    def get_lib_dirs(self):
        return self._options.lib

    def get_options(self):
        return self._options

    def get_args(self):
        return self._args

    def get_file_dir(self, f, search_paths = None):

        # calculate the correct path to the file 
        if f[0] == '/':
            # if it starts with a '/' then it is an absolute path
            return os.path.dirname(f)
    
        # if no search_paths are provided, then default to the app dir
        if search_paths == None:
            search_paths = [ self.get_app_dir() ]

        # look in the search paths for the file they specified
        for path in search_paths:
            if path[0] == '/':
                test_path = os.path.join(path, f)
            else:
                test_path = os.path.join(self.get_app_dir(), path, f)

            # if we've found it, then return the dir it resides in
            if os.path.exists(test_path):
                return os.path.dirname(test_path)

        return None

    def get_file_path(self, f, search_paths = None):
        # calculate the correct path to the file 
        if f[0] == '/':
            # if it starts with a '/' then it is an absolute path
            return f
       
        # if no search_paths are provided, then default to the app dir
        if search_paths == None:
            search_paths = [ self.get_app_dir() ]

        # look in the search paths for the file they specified
        for path in search_paths:
            if path[0] == '/':
                test_path = os.path.join(path, f)
            else:
                test_path = os.path.join(self.get_app_dir(), path, f)

            # if we've found it, then return the dir it resides in
            if os.path.exists(test_path):
                return test_path

        return None

    def get_app_dir(self):
        return self._app_dir

def main():
    options = Options()
    print options._options
    print options._args

    p = hlakit.Preprocessor(options)
    # c = hlakit.Compiler(options)
    for f in options.get_args():

        # calculate the correct path to the file 
        fpath = options.get_file_path(f)

        # open the file
        inf = open(fpath, 'r')

        # parse the file 
        tokens = p.parse(inf)

        # close the file
        inf.close()

        # compile the tokenstream
        # c.compile(tokens)

        # dump the tokens
        print "TOKEN STREAM:"
        print tokens

if __name__ == "__main__":
    
    sys.exit(main())
