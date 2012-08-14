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
import cStringIO
import ply.lex as lex
import ply.yacc as yacc
from ppgraph import PPGraph
from hlakit.common.symboltable import SymbolTable

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
        },
        '2A03': {
            'module': 'cpu.ricoh2A0X',
            'class': 'Ricoh2A0X',
            'desc': 'NES NTSC CPU'
        },
        '2A07': {
            'module': 'cpu.ricoh2A0X',
            'class': 'Ricoh2A0X',
            'desc': 'NES PAL CPU'
        }
        #'5A22': {
        #    'module': 'cpu.ricoh5A22',
        #    'class': 'Ricoh5A22',
        #    'desc': 'SNES CPU'
        #},
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
            'cpu': [ '6502' ],
            'desc': 'Generic platform, turns off platform-specific features'
        },
        'nes': {
            'module': 'platform.nes',
            'class': 'NES',
            'cpu': [ '2A03', '2A07' ],
            'desc': 'Nintendo Entertainment System'
        },
        #'snes': {
        #    'module': 'platform.snes',
        #    'class': 'SNES',
        #    'cpu': [ '5A22' ],
        #    'desc': 'Super Nintendo Entertainment System'
        #},
        #'lynx': {
        #    'module': 'platform.lynx',
        #    'class': 'Lynx',
        #    'cpu': '6502',
        #    'desc': 'Atari Lynx Portable System'
        #},
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
        parser.add_option('-g', '--debug', action='store_true', dest='debug', default=False,
            help='outputs some debug output')
        parser.add_option('-d', '--graph', action='store_true', dest='graph', default=False,
            help='outputs a graph of the ast')
        parser.add_option('-o', dest='output_file', default=None,
            help='specify the name of the output file')

        self._opts_parser = parser

    def _parse_args( self, args ):
        self._options = None
        self._args = None
        self._target = None

        # actually parse the args
        (self._options, self._args) = self.get_opts_parser().parse_args(args)
       
        # get the platform name
        platform = self._options.platform.lower()

        # make sure the platform is valid
        if not self.PLATFORM.has_key(platform):
            raise CommandLineError('You specified an unknown platform name.\n\n' \
                                   'The supported platforms are:\n' \
                                   '\t%s\n' % '\n\t'.join(self.PLATFORM))

        # make sure that if the platform is 'generic' that they specified a cpu
        if platform == 'generic':
            if self._options.cpu == '':
                raise CommandLineError('With the generic platform you must specify ' \
                                       'a CPU with the --cpu switch.\n\n' \
                                       'The supported CPUs are:\n' \
                                       '\t%s\n' % '\n\t'.join(self.CPU))
            elif self._options.cpu not in self.PLATFORM[platform]['cpu']:
                raise CommandLineError('You specified the %s platform but chose the wrong CPU.\n' \
                                       'The supported cpu\'s for the %s platform are:\n' \
                                       '\t%s\n' % (platform, platform, '\n\t'.join(self.PLATFORM[platform]['cpu'])))

    def initialize_target(self):
        # if they specified a platform, then look up the module
        # and class name and instantiate an instance of the target
        platform = self._options.platform.lower()

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
            self._parse_args( args )

        except CommandLineError, e:
            print >> sys.stderr, 'ERROR: %s' % e
            p = self._opts_parser
            if p:
                p.print_help(file=sys.stderr)
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
        if getattr(self, '_options', None):
            return self._options.debug

    def is_graph(self):
        if getattr(self, '_options', None):
            return self._options.graph

    def get_target(self):
        if getattr(self, '_target', None) is None:
            return None
        return self._target

    def push_cur_dir(self, d):
        if getattr(self, '_cur_dir', None) is None:
            self._cur_dir = []
        self._cur_dir.append(d)

    def pop_cur_dir(self):
        if getattr(self, '_cur_dir', None):
            self._cur_dir.pop()

    def push_cur_file(self, f):
        if getattr(self, '_cur_file', None) is None:
            self._cur_file = []
        self._cur_file.append(f)

    def pop_cur_file(self):
        if getattr(self, '_cur_file', None):
            self._cur_file.pop()

    def get_cur_file(self):
        if getattr(self, '_cur_file', None):
            return self._cur_file[-1]
        return None

    def get_root_file(self):
        if getattr(self, '_cur_file', None):
            return self._cur_file[0]
        return None

    def get_cur_dir(self):
        cur_dir = getattr(self, '_cur_dir', None)
        if cur_dir:
            return cur_dir[-1]
        return None

    def get_include_dirs(self):
        options = getattr(self, '_options', None)
        if options:
            return options.include
        return []

    def get_file_path(self, f, inc_dirs=False):
        search_paths = []

        # calculate the correct path to the file 
        if f[0] == '/':
            # if it starts with a '/' then it is an absolute path
            return f
      
        # add in the current file dir
        search_paths.append(self.get_cur_dir())

        # add in cwd as last option
        search_paths.append(os.getcwd())

        # add in the included directories
        if inc_dirs and (len(self.get_include_dirs()) > 0):
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

    def lexer(self, debug=False):
        target = getattr(self, '_target', None)
        if target:
            return lex.lex(module=target.lexer(), debug=(self.is_debug() or debug))
        return None

    def parser(self, debug=False):
        target = getattr(self, '_target', None)
        if target:
            return yacc.yacc(module=target.parser(), debug=(self.is_debug() or debug))
        return None

    def pp_lexer(self, debug=False):
        target = getattr(self, '_target', None)
        if target:
            return lex.lex(module=target.pp_lexer(), debug=(self.is_debug() or debug))
        return None

    def pp_parser(self, debug=False):
        target = getattr(self, '_target', None)
        if target:
            return yacc.yacc(module=target.pp_parser(), debug=(self.is_debug() or debug))
        return None

    def _strip_pp(self, pp):
        line = []
        output = []
        inline = False

        for p in pp[1]:
            if inline:
                if len(p.strip()) > 0:
                    line.append(p)
                if p[0] == '\n':
                    output.append(' '.join(line))
                    inline = False
            else:
                if isinstance(p, tuple):
                    import pdb; pdb.set_trace()
                if len(p.strip()) > 0:
                    line = []
                    line.append(p)
                    inline = True
        return ('program', output)

    def go():
        pass

    """
    def preprocess_file(self, f, debug=False):
        pp_lexer = self.pp_lexer(debug)
        pp_parser = self.pp_parser(debug)

        # read the file
        fin = open(f)
        inf = fin.read()
        fin.close()

        print "Preprocessing %s..." % f
        self.push_cur_file(f)
        self.push_cur_dir(os.path.dirname(f))
        result = pp_parser.parse(inf, lexer=pp_lexer, debug=(self.is_debug() or debug))
        self.pop_cur_dir()
        self.pop_cur_file()
        if self.is_graph():
            graph = PPGraph(os.path.basename(f) + '.pdf', result)
            graph.save()

        return result

    def preprocess(self):
        output = []

        files = self.get_args()
        if len(files) == 0:
            raise CommandLineError('No files to compile\n')

        try:
            for f in files:
                pp = self.preprocess_file(f)
                clean = self._strip_pp(pp)
                sio = cStringIO.StringIO()
                sio.write('\n'.join(clean[1]))
                output.append( (f, pp, sio.getvalue() ) )
                sio.close()
        except CommandLineError, e:
            print >> sys.stderr, 'ERROR: %s' % e
            p = self._opts_parser
            if p:
                p.print_help()
            raise e

        return output

    def compile_file(self, cunit, debug=False):
        lexer = self.lexer(debug)
        parser = self.parser(debug)

        print "Compiling %s..." % cunit[0]
        self.push_cur_file(cunit[0])
        self.push_cur_dir(os.path.dirname(cunit[0]))
        result = parser.parse(cunit[2], lexer=lexer, debug=(self.is_debug() or debug))
        self.pop_cur_dir()
        self.pop_cur_file()

        return result
        
    def compile(self, cunits):
        '''
        cus is a list of tuples, each tuple contains the following:
         0: full path to compilation unit file
         1: the pre-processor tuple with AST ('program', [ ...tokens... ])
         2: the pre-processor output
        '''

        # reset the symbol table before beginning compilation
        SymbolTable().reset_state()

        output = []
        try:
            for cunit in cunits:
                cc = self.compile_file(cunit)
                output.append( (cunit[0], cunit[1], cunit[2], cc) )
        except RuntimeError, e:
            import pdb; pdb.set_trace()

        return output
    """


