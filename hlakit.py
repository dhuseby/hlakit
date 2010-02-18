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
from hlakit.machine import *

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
    MACHINE = {
        'nes': 'NES',
        'lynx': 'Lynx'
    }
    def __init__(self):
        self._options = None
        self._args = None
        self._cpu = None
        self._machine = None

        # calculate the script dir
        self._app_dir = os.path.dirname(os.path.realpath(__file__))

        parser = optparse.OptionParser(version = "%prog " + HLAKIT_VERSION)
        parser.add_option('--cpu', default=None, dest='cpu',
            help='specifying the cpu activates the assembly opcodes for the given cpu.\n'
                'you probably want to specify a machine instead if you are coding for\n'
                'a specific machine.  if you want to just create a generic binary for\n'
                'a given cpu, then this is the option for you.')
        parser.add_option('--machine', default=None, dest='machine',
            help='specifying the machine activates machine specific preprocessor directives\n'
                'and implies the cpu so you don\'t have to specify the cpu.')
        parser.add_option('-I', '--include', action="append", default=[], dest='include',
            help='specify directories to search for include files')

        (self._options, self._args) = parser.parse_args()

        # check for required options
        if (not self._options.machine) and (not self._options.cpu):
            parser.error('You must specify either a machine with --machine or a cpu with --cpu')

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

    def get_cpu(self, logger):
        # call this just in case they call get_cpu first
        self.get_machine(logger)

        # if the cpu was not created then they must have specified
        # --cpu instead of --machine
        if self._cpu == None:
            cpu = self._options.cpu
            cpu_ctor = globals()[Options.CPU[cpu.lower()]]
            self._cpu = cpu_ctor(self, logger)

        return self._cpu

    def get_machine(self, logger):

        # create the machine instance if it hasn't already been created
        if self._machine == None:
            machine = self._options.machine
            if machine:
                machine_ctor = globals()[Options.MACHINE[machine.lower()]]
                self._machine = machine_ctor(self, logger)
                cpu = self._machine.get_cpu()
                cpu_ctor = globals()[Options.CPU[cpu.lower()]]
                self._cpu = cpu_ctor(self, logger)

        return self._machine

def main():
    options = Options()
    p = hlakit.Preprocessor(options)
    c = hlakit.Compiler(options)
    #l = hlakit.Linker(options)
    
    for f in options.get_args():

        # calculate the correct path to the file 
        fpath = options.get_file_path(f)

        # open the file
        inf = open(fpath, 'r')

        # parse the file 
        pp_tokens = p.parse(inf)

        # close the file
        inf.close()

        # compile the tokenstream
        cc_tokens = c.compile(pp_tokens)

        # linke the compiled tokens into a binary
        #l.link(cc_tokens)

        # dump the tokens
        print "TOKEN STREAM:"
        print cc_tokens

if __name__ == "__main__":
    
    sys.exit(main())
