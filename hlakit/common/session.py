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

THIS SOFTWARE IS PROVIDED BY DAVID HUSEBY ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DAVID HUSEBY OR
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

class DummyOptions(object):
    pass

class Session(object):
    """
    This encapsulates the global configuration of a given session using hlakit.
    It handles parsing the command line parameters and providing an interface
    to the 
    """

    # definitions for supported CPU's 
    CPU = {
        'generic' : {
            'module': 'common.target',
            'class': 'Target',
            'desc': 'Generic Target'
        },
        '6502': {
            'module': 'cpu.mos6502', 
            'class': 'MOS6502', 
            'desc': 'MOS Technologies 6502 8-bit CPU'
        }
        #'z80': {
        #    'module': 'cpu.z80',
        #    'class': 'Z80',
        #    'desc': 'Zilog Z80 8-bit CPU'
        #},
        #'LR35902': {
        #    'module': 'cpu.lr35902',
        #    'class': 'LR35902',
        #    'desc': 'Sharp Z80 Variant in the original Nintendo Game Boy'
        #},
        #'68k': {
        #    'module': 'cpu.motorola68000',
        #    'class': 'Motorola68k',
        #    'desc': 'Motorola 68k 32-bit CPU'
        #}
    }
    PLATFORM = {
        'nes': {
            'module': 'platform.nes',
            'class': 'NES',
            'cpu': 'mos6502',
            'desc': 'Nintendo Entertainment System'
        },
        'lynx': {
            'module': 'platform.lynx',
            'class': 'Lynx',
            'cpu': 'mos6502',
            'desc': 'Atari Lynx Portable System'
        }
        #'gameboy': {
        #    'module': 'platform.gameboy',
        #    'class': 'GameBoy',
        #    'desc': 'Nintendo GameBoy System'
        #}
    }

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def parse_args(self, args=[]):
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

            platform_class = self.PLATFORM[platform]['class']
            platform_module = 'hlakit.' + self.PLATFORM[platform]['module']
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

            cpu_class = self.CPU[cpu]['class']
            cpu_module = 'hlakit.' + self.CPU[cpu]['module']
            module_symbols = __import__(cpu_module, fromlist=[cpu_class])
            cpu_ctor = getattr(module_symbols, cpu_class)
            self._target = cpu_ctor()

    def get_include_dirs(self):
        options = getattr(self, '_options', None)
        if options:
            return options.include
        return []

    def add_include_dir(self, path):
        """ this is only used by the #usepath preprocessor directive that is
        deprecated and will be gone in version 1.0 """
        options = getattr(self, '_optons', None)
        if options:
            options.include.append(path)
        else:
            self._options = DummyOptions()
            setattr(self._options, 'include', [ path ])

    def get_args(self):
        return getattr(self, '_args', [])

    def get_file_dir(self, f):

        # calculate the correct path to the file 
        if f[0] == '/':
            # if it starts with a '/' then it is an absolute path
            return os.path.dirname(f)
  
        # add in the current file dir
        pp = self.preprocessor()
        state = pp.state_stack_top()
        if state and state.get_file_path():
            search_paths.append(os.path.dirname(state.get_file_path()))

        # add in cwd as last option
        search_paths.append(os.getcwd())

        # add in the included directories
        if len(self.get_include_dirs()) > 0:
            search_paths.extend(self.get_include_dirs())

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

    def get_file_path(self, f):
        search_paths = []

        # calculate the correct path to the file 
        if f[0] == '/':
            # if it starts with a '/' then it is an absolute path
            return f
      
        # add in the current file dir
        pp = self.preprocessor()
        state = pp.state_stack_top()
        if state and state.get_file_path():
            search_paths.append(os.path.dirname(state.get_file_path()))

        # add in cwd as last option
        search_paths.append(os.getcwd())

        # add in the included directories
        if len(self.get_include_dirs()) > 0:
            search_paths.extend(self.get_include_dirs())

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
        target = getattr(self, '_target', None)
        if target:
            return target.preprocessor()
        return None

    def compiler(self):
        target = getattr(self, '_target', None)
        if target:
            return target.compiler()
        return None

    def linker(self):
        target = getattr(self, '_target', None)
        if target:
            return target.linker()
        return None

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

            # parse the file
            inf = open(fpath, 'r')
            pp.parse(inf)
            inf.close()

            pp_tokens = pp.get_output()
            #for t in pp_tokens:
            #    print "%s: %s" % (type(t), t)

            # compile the tokenstream
            cc_tokens = cc.compile(pp_tokens)

            # link the compiled tokens into a binary
            #ll.link(cc_tokens)

            # dump the tokens
            #print "TOKEN STREAM:"
            #for t in cc_tokens:
            #    print "%s: %s" % (type(t), t)

            #TypeRegistry.instance().dump()
            #SymbolTable.instance().dump()

