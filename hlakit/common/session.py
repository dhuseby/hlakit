"""
HLAKit
Copyright (c) 2010-2011 David Huseby. All rights reserved.

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
import ply.lex as lex
import ply.yacc as yacc

HLAKIT_VERSION = "0.8"

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
        'generic': {
            'module': 'platform.generic',
            'class': 'Generic',
            'cpu': None,
            'desc': 'Generic platform, turns off platform-specific features'
        },
        'nes': {
            'module': 'platform.nes',
            'class': 'NES',
            'cpu': '6502',
            'desc': 'Nintendo Entertainment System'
        },
        'lynx': {
            'module': 'platform.lynx',
            'class': 'Lynx',
            'cpu': '6502',
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

    def _build_parser(self):
        self._parser = None

        # parse the command line options
        usage = "usage: %prog [options] file1 file2"
        parser = optparse.OptionParser(usage=usage, version = "%prog " + HLAKIT_VERSION)
        parser.add_option('--cpu', default='', dest='cpu',
            help='specifying the cpu activates the assembly opcodes for the given cpu.\n'
                'you probably want to specify a platform instead if you are coding for\n'
                'a specific platform (e.g. NES).  if you want to just create a generic\n'
                'binary for a given cpu, then this is the option for you.')
        parser.add_option('--platform', default='generic', dest='platform',
            help='specifying the platform activates platform specific preprocessor\n'
                 'directives and implies the cpu so you don\'t have to specify the cpu.')
        parser.add_option('-I', '--include', action="append", default=[], dest='include',
            help='specify directories to search for include files')
        parser.add_option('--pp', action='store_true', dest='output_pp', default=False,
            help='outputs the preprocessed input to stdout')
        parser.add_option('--cc', action='store_true', dest='output_cc', default=False,
            help='outputs the compiled token names to stdout')
        parser.add_option('-d', '--debug', action='store_true', dest='debug', default=False,
            help='outputs some debug output')
        parser.add_option('-o', dest='output_file', default=None,
            help='specify the name of the output file')

        self._opts_parser = parser


    def _initialize_target(self, args):
        self._options = None
        self._args = None
        self._target = None

        # actually parse the args
        (self._options, self._args) = self.get_opts_parser().parse_args(args)

        # make sure that if the platform is 'generic' that they specified a cpu
        if (self._options.platform == 'generic') and (self._options.cpu == ''):
            raise CommandLineError('With the generic platform you must specify ' \
                                   'a CPU with the --cpu switch.\n\n' \
                                   'The supported CPUs are:\n' \
                                   '\t%s\n' % '\n\t'.join(self.CPU))

        # if they specified a platform, then look up the module
        # and class name and instantiate an instance of the target
        platform = self._options.platform.lower()

        if not self.PLATFORM.has_key(platform):
            raise CommandLineError('You specified an unknown platform name.\n\n' \
                                   'The supported platforms are:\n' \
                                   '\t%s\n' % '\n\t'.join(self.PLATFORM))

        # get the platform data
        platform_class = self.PLATFORM[platform]['class']
        platform_module = 'hlakit.' + self.PLATFORM[platform]['module']
        module_symbols = __import__(platform_module, fromlist=[platform_class])
        platform_ctor = getattr(module_symbols, platform_class)

        # initialize the target
        self._target = platform_ctor(self._options.cpu.lower())

    def parse_args(self, args=[]):
        try:
            self._build_parser()
            self._initialize_target(args)
        except CommandLineError, e:
            print >> sys.stderr, 'ERROR: %s' % e
            p = self.get_parser()
            if p:
                p.print_help()
            raise e
        
    def get_cpu_spec(self, cpu):
        cpus = getattr(self, 'CPU', None)
        if cpus and cpus.has_key(cpu):
            return cpus[cpu]
        return None

    def get_args(self):
        return getattr(self, '_args', [])

    def get_opts_parser(self):
        if not hasattr(self, '_opts_parser'):
            self._build_parser()
        return getattr(self, '_opts_parser', None)

    def is_debug(self):
        options = getattr(self, '_options', None)
        if options:
            return options.debug

    def get_include_dirs(self):
        options = getattr(self, '_options', None)
        if options:
            return options.include
        return []

    def lexer(self):
        target = getattr(self, '_target', None)
        if target:
            return lex.lex(module=target.lexer(), debug=self.is_debug())
        return None

    def pp_lexer(self):
        target = getattr(self, '_target', None)
        if target:
            return lex.lex(module=target.pp_lexer(), debug=self.is_debug())
        return None

    def parser(self):
        target = getattr(self, '_target', None)
        if target:
            return yacc.yacc(module=target.parser(), debug=self.is_debug())
        return None

    def pp_parser(self):
        target = getattr(self, '_target', None)
        if target:
            return yacc.yacc(module=target.pp_parser(), debug=self.is_debug())
        return None

    def _preprocess(self):
        pp_lexer = self.pp_lexer()
        pp_parser = self.pp_parser()

        # this will contain a tuple for each file containing the file name, the 
        # preprocessed output, and an object that maps line,col positions in the
        # preprocessed output to the original file line,col for error reporting
        output = []

        files = self.get_args()
        if len(files) == 0:
            raise CommandLineError('No files to compile\n')

        for f in self.get_args():

            # read the file
            fin = open(f)
            inf = fin.read()
            fin.close()

            #lexer.add_path(os.path.dirname(f))
            #lexer.parse(inf, f)
            result = pp_parser.parse(inf, lexer=pp_lexer)
            print result

    def _build(self):
        lexer = self.lexer()
        parser = self.parser()

        files = self.get_args()
        if len(files) == 0:
            raise CommandLineError('No files to compile\n')

        for f in self.get_args():

            # read the file
            fin = open(f)
            inf = fin.read()
            fin.close()

            #lexer.add_path(os.path.dirname(f))
            #lexer.parse(inf, f)
            result = parser.parse(inf, lexer=lexer)
            print result

    def build(self):
        try:
            self._preprocess()
            #self._build()
        except CommandLineError, e:
            print >> sys.stderr, 'ERROR: %s' % e
            p = self.get_parser()
            if p:
                p.print_help()
            raise e


