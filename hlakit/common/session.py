"""
HLAKit
Copyright (c) 2010 David Huseby. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY DAVID HUSEBY `AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of David Huseby.
"""

import os
import sys
import optparse

HLAKIT_VERSION = "0.0.2"

class CommandLineError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class Session(object):
    """
    This encapsulates the global configuration of a given session using hlakit.
    It handles parsing the command line parameters and providing an interface
    to the 
    """

    # definitions for supported CPU's 
    CPU = {
        '6502': {
            'file': 'mos6502', 
            'class': 'MOS6502', 
            'desc': 'MOS Technologies 6502 8-bit CPU'
        }
        #'z80': {
        #    'file': 'z80',
        #    'class': 'Z80',
        #    'desc': 'Zilog Z80 8-bit CPU'
        #},
        #'LR35902': {
        #    'file': 'lr35902',
        #    'class': 'LR35902',
        #    'desc': 'Sharp Z80 Variant in the original Nintendo Game Boy'
        #},
        #'68k': {
        #    'file': 'motorola68000',
        #    'class': 'Motorola68k',
        #    'desc': 'Motorola 68k 32-bit CPU'
        #}
    }
    PLATFORM = {
        'nes': {
            'file': 'nes',
            'class': 'NES',
            'cpu': 'mos6502',
            'desc': 'Nintendo Entertainment System'
        },
        #'lynx': {
        #    'file': 'lynx',
        #    'class': 'Lynx',
        #    'cpu': 'mos6502',
        #    'desc': 'Atari Lynx Portable System'
        #}
        #'gameboy': {
        #    'file': 'gameboy',
        #    'class': 'GameBoy',
        #    'desc': 'Nintendo GameBoy System'
        #}
    }

    def __init__(self, args):
        self._options = None
        self._args = None
        self._target = None

        # parse the command line options
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

        (self._options, self._args) = parser.parse_args(args)

        # check for required options
        if (not self._options.platform) and (not self._options.cpu):
            raise CommandLineError('You must specify either a platform with ' \
                         '--platform or a cpu with --cpu\n')

        # get a handle to the compile target
        if self._options.platform != None:
            # if they specified a platform, then look up the module
            # and class name and instantiate an instance of the target
            platform = self._options.platform.lower()

            if not self.PLATFORM.has_key(platform):
                raise CommandLineError('You specified an unknown platform name.\n\n' \
                                       'The supported platform(s) are:\n' \
                                       '\t%s\n' % '\n\t'.join(self.PLATFORM))

            platform_file = self.PLATFORM[platform]['file']
            platform_class = self.PLATFORM[platform]['class']
            platform_module = '.'.join(['hlakit', 'platform', platform_file])
            module_symbols = __import__(platform_module, fromlist=[platform_class])
            platform_ctor = getattr(module_symbols, platform_class)
            self._target = platform_ctor()
        else:
            # otherwise they specified a cpu so look up its module and class
            # and instantiate an instance as the target
            cpu = self._options.cpu.lower()

            if not self.CPU.has_key(cpu):
                raise CommandLineError('You specified an unknown CPU name.\n\n' \
                                       'The supported CPU(s) are:\n' \
                                       '\t%s\n' % '\n\t'.join(self.CPU))

            cpu_file = self.CPU[cpu]['file']
            cpu_class = self.CPU[cpu]['class']
            cpu_module = '.'.join(['hlakit', 'cpu', cpu_file])
            module_symbols = __import__(cpu_module, fromlist=[cpu_class])
            cpu_ctor = getattr(module_symbols, cpu_class)
            self._target = cpu_ctor()

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
    
        # look in the search paths for the file they specified
        for path in search_paths:
            if path[0] == '/':
                test_path = os.path.join(path, f)
            else:
                test_path = os.path.join(os.getcwd(), path, f)

            # if we've found it, then return the dir it resides in
            if os.path.exists(test_path):
                return os.path.dirname(test_path)

        return None

    def get_file_path(self, f, search_paths = []):
        # calculate the correct path to the file 
        if f[0] == '/':
            # if it starts with a '/' then it is an absolute path
            return f
       
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

    def preprocessor(self):
        return self._target.preprocessor()

    def compiler(self):
        return self._target.compiler()

    def linker(self):
        return self._target.linker()

    def build(self):
        pp = self.preprocessor()
        cc = self.compiler()
        ll = self.linker()

        for f in self.get_args():

            # calculate the correct path to the file 
            fpath = self.get_file_path(f)
            
            # make sure the file was found 
            if fpath is None:
                continue;

            print 'processing file: %s' % fpath

            # open the file
            #inf = open(fpath, 'r')

            # parse the file 
            #pp_tokens = pp.parse(inf)
            #for t in pp_tokens:
            #    print "%s: %s" % (type(t), t)

            # close the file
            #inf.close()

            # compile the tokenstream
            #cc_tokens = cc.compile(pp_tokens)

            # linke the compiled tokens into a binary
            #ll.link(cc_tokens)

            # dump the tokens
            #print "TOKEN STREAM:"
            #for t in cc_tokens:
            #    print "%s: %s" % (type(t), t)

            #TypeRegistry.instance().dump()
            #SymbolTable.instance().dump()

