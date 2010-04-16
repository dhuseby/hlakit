#!/usr/bin/env python
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
import optparse
import hlakit
from hlakit.cpu import *
from hlakit.platform import *
from hlakit.types import *
from hlakit.symbols import *

from pyparsing import *

# globals
HLAKIT_VERSION = "0.0.2"

class Options(object):
    """
    This encapsulates the command line options and the options related
    functions.
    """

    CPU = {
        '6502': 'MOS6502',
        'mos6502': 'MOS6502',
    }
    PLATFORM = {
        'nes': 'NES',
        'lynx': 'Lynx'
    }
    def __init__(self):
        self._options = None
        self._args = None
        self._cpu = None
        self._platform = None

        # calculate the script dir
        self._app_dir = os.path.dirname(os.path.realpath(__file__))

        parser = optparse.OptionParser(version = "%prog " + HLAKIT_VERSION)
        parser.add_option('--cpu', default=None, dest='cpu',
            help='specifying the cpu activates the assembly opcodes for the given cpu.\n'
                'you probably want to specify a platform instead if you are coding for\n'
                'a specific platform (e.g. NES).  if you want to just create a generic\n'
                'binary for a given cpu, then this is the option for you.')
        parser.add_option('--platform', default=None, dest='platform',
            help='specifying the platform activates platform specific preprocessor\n'
                 'directives and implies the cpu so you don\'t have to specify the cpu.')
        parser.add_option('-I', '--include', action="append", default=[], dest='include',
            help='specify directories to search for include files')

        (self._options, self._args) = parser.parse_args()

        # check for required options
        if (not self._options.platform) and (not self._options.cpu):
            parser.error('You must specify either a platform with --platform or a cpu with --cpu\n')

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

    def get_file_path(self, f, search_paths = []):
        # calculate the correct path to the file 
        if f[0] == '/':
            # if it starts with a '/' then it is an absolute path
            return f
       
        # if no search_paths are provided, then default to the app dir
        if len(search_paths) == 0:
            search_paths = [ os.getcwd(), self.get_app_dir() ]

        # add in the included directories
        if len(self._options.include) > 0:
            search_paths.extend(self._options.include)

        # look in the search paths for the file they specified
        for path in search_paths:
            if path[0] == '/':
                test_path = os.path.join(path, f)
            else:
                test_path = os.path.join(os.getcwd(), path, f)

            # if we've found it, then return the dir it resides in
            if os.path.exists(test_path):
                return test_path

        return None

    def get_app_dir(self):
        return self._app_dir

    def get_cpu(self, logger):
        # call this just in case they call get_cpu first
        self.get_platform(logger)

        # if the cpu was not created then they must have specified
        # --cpu instead of --platform
        if self._cpu == None:
            cpu = self._options.cpu
            cpu_ctor = globals()[Options.CPU[cpu.lower()]]
            self._cpu = cpu_ctor(self, logger)

        return self._cpu

    def get_platform(self, logger):

        # create the platform instance if it hasn't already been created
        if self._platform == None:
            platform = self._options.platform
            if platform:
                platform_ctor = globals()[Options.PLATFORM[platform.lower()]]
                self._platform = platform_ctor(self, logger)
                cpu = self._platform.get_cpu()
                cpu_ctor = globals()[Options.CPU[cpu.lower()]]
                self._cpu = cpu_ctor(self, logger)

        return self._platform

def main():
    options = Options()
    p = hlakit.Preprocessor(options)
    c = hlakit.Compiler(options)
    #l = hlakit.Linker(options)
    
    for f in options.get_args():

        # calculate the correct path to the file 
        fpath = options.get_file_path(f)
        
        # make sure the file was found 
        if fpath is None:
            continue;

        # open the file
        inf = open(fpath, 'r')

        # parse the file 
        pp_tokens = p.parse(inf)
        for t in pp_tokens:
            print "%s: %s" % (type(t), t)

        # close the file
        inf.close()

        # compile the tokenstream
        cc_tokens = c.compile(pp_tokens)

        # linke the compiled tokens into a binary
        #l.link(cc_tokens)

        # dump the tokens
        print "TOKEN STREAM:"
        for t in cc_tokens:
            print "%s: %s" % (type(t), t)

        TypeRegistry.instance().dump()
        SymbolTable.instance().dump()

if __name__ == "__main__":
    
    sys.exit(main())
