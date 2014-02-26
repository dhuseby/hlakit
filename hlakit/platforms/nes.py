"""
Copyright (c) 2010-2014 David Huseby. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDERS AND CONTRIBUTORS OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of copyright holders and contributors.
"""

from ..platform import Platform
#from session import CommandLineError, Session
#from lexer import Lexer
#from parser import Parser
#import copy

PLATFORM_CLASS = 'NES'
CPUS = ['ricoh2a0x']

class NES(Platform):
    
    def __init__(self, cpu=None):
        super(NES, self).__init__()
"""

        self._cpu = cpu

        # compiler lexer and parser
        self._lexer = NESLexer()
        self._parser = NESParser(tokens=self._lexer.tokens)

        # initialize the current block member
        self._alignment = None
        self._padding = '0xFF'
        self._banksize = { 'rom': '16K', 'ram': '16K', 'chr': '16K' }
        self._blocks = {}

        # initially turn #ines.off to False
        self.__setitem__('off', False)

        # start the initial block
        self._init_block()

    def lexer(self):
        return self._lexer

    def parser(self):
        return self._parser

    def pp_lexer(self):
        return self._pp_lexer

    def pp_parser(self):
        return self._pp_parser


    ''' functions for building and saving the ram/rom/chr block data '''

    def _init_block(self):
        self._block = { 'type': None,
                        'started': False,
                        'ended': False,
                        'start': None,
                        'end': None,
                        'alignment': self._alignment,
                        'padding': self._padding,
                        'banksize': '16K' }

    def has_block_ended(self):
        return self._block['ended']

    def has_block_started(self):
        return self._block['started']

    def start_block(self, type_=None):
        self._block['type'] = type_ 
        self._block['started'] = True
        self._block['banksize'] = self._banksize[type_]
        self._block['source'] = copy.copy(Session()._cur_file)

    def end_block(self):
        self._block['ended'] = True

    def get_cur_block(self):
        return self._block

    def get_blocks(self):
        return self._blocks

    def reset_block(self):
        root_file = Session().get_root_file()
        if root_file not in self._blocks:
            self._blocks[root_file] = []

        self._blocks[root_file].append(self._block)
        self._init_block()

    def set_block_org(self, org):
        self._block['org'] = org

    def set_block_maxsize(self, maxsize):
        self._block['maxsize'] = maxsize

    def set_block_bank(self, bank):
        self._block['bank'] = bank

    def set_block_link(self, link):
        self._block['link'] = link

    def set_block_type(self, type_):
        self._block['type'] = type_

    def set_block_start(self, start):
        self._block['start'] = start

    def set_block_end(self, end):
        self._block['end'] = end

    def set_alignment(self, align):
        self._alignment = align
        self._block['alignment'] = align

    def set_padding(self, padding):
        self._padding = padding
        self._block['padding'] = padding

    def set_banksize(self, type_, banksize):
        self._banksize[type_] = banksize
        if self._block['type'] == type_:
            self._block['banksize'] = banksize


class NESLexer(Lexer):

    '''NOTE: that the handling of RAM/ROM/CHR preprocessor statements is done
       at the compiler level so we need to be able to parse them from the input
       stream of text.  However, the #ines preprocessor statements were handled
       during the preprocess stage and don't need to be handled here.'''

    # NES tokens list
    tokens = [ 'PPRAMORG',
               'PPRAMEND',
               'PPROMORG',
               'PPROMBANK',
               'PPROMBANKSIZE',
               'PPROMEND',
               'PPCHRBANK',
               'PPCHRBANKSIZE',
               'PPCHRLINK',
               'PPCHREND',
               'PPSETPAD',
               'PPALIGN' ]

    # NES compile time pre-processor directives
    t_PPRAMORG          = r'\#(?i)[\t ]*ram\.org'
    t_PPRAMEND          = r'\#(?i)[\t ]*ram\.end'

    t_PPROMORG          = r'\#(?i)[\t ]*rom\.org'
    t_PPROMBANK         = r'\#(?i)[\t ]*rom\.bank'
    t_PPROMBANKSIZE     = r'\#(?i)[\t ]*rom\.banksize'
    t_PPROMEND          = r'\#(?i)[\t ]*rom\.end'

    t_PPCHRBANK         = r'\#(?i)[\t ]*chr\.bank'
    t_PPCHRBANKSIZE     = r'\#(?i)[\t ]*chr\.banksize'
    t_PPCHRLINK         = r'\#(?i)[\t ]*chr\.link'
    t_PPCHREND          = r'\#(?i)[\t ]*chr\.end'

    t_PPSETPAD          = r'\#(?i)[\t ]*setpad'
    t_PPALIGN           = r'\#(?i)[\t ]*align'

    def __init__(self):
        super(NESLexer, self).__init__()


class NESParser(Parser):

    def __init__(self, tokens=[]):
        super(NESParser, self).__init__(tokens)

    def p_program(self, p):
        '''program : empty
                   | platform_statement
                   | program platform_statement'''

        '''
        nes = Session().get_target()

        if nes.has_block_started() and nes.get_cur_block()['start'] is None:
            nes.set_block_start(len(p[1][1]) - 1)

        if nes.has_block_ended():
            nes.set_block_end(len(p[1][1]))
            nes.reset_block()
        '''

        # call base class implementation
        super(Parser, self).p_program(p)

    def p_platform_statement(self, p):
        '''platform_statement : common_statement
                              | nes_pp_statement'''
        if p[1] != None:
            p[0] = p[1]

    # no id necessary because macros have been expanded already
    def p_nes_pp_value(self, p):
        '''nes_pp_value : number
                        | filename
                        | number ',' number
                        | filename ',' number'''
        if len(p) == 2:
            p[0] = [ p[1], None ]
        else:
            p[0] = [ p[1], p[3] ]

    def _clean_value(self, val):
        v = val

        # macro replacements cause values to be lists of tokens
        if isinstance(v, list):
            tmp = ''
            for i in v:
                tmp += '%s ' % i
            v = tmp

        # strip whitespace and brackets
        v = v.strip("\n\t\r '\"><")

        return v

    def p_nes_pp_statement(self, p):
        '''nes_pp_statement : PPRAMORG nes_pp_value
                            | PPRAMEND
                            | PPROMORG nes_pp_value
                            | PPROMBANK nes_pp_value
                            | PPROMBANKSIZE nes_pp_value
                            | PPROMEND
                            | PPCHRBANK nes_pp_value
                            | PPCHRBANKSIZE nes_pp_value
                            | PPCHRLINK nes_pp_value
                            | PPCHREND
                            | PPSETPAD nes_pp_value
                            | PPALIGN nes_pp_value'''
       
        '''
        nes = Session().get_target()
        if p[1] in ('ram', 'rom', 'chr'):
            if p[3] in ('org', 'bank'):
                if nes.has_block_started():
                    t = nes.get_cur_block()['type']
                    if t != None and t != p[1]:
                        raise Exception('WARNING: unclosed %s block at file: %s, line: %s, included from: %s' % (t, Session().get_cur_file(), p.lexer.lineno, Session()._cur_file))
                else:
                    nes.start_block(p[1])
                if nes.get_cur_block()['type'] is None:
                    nes.set_block_type(p[1])

            if p[3] == 'org':
                nes.set_block_org(self._clean_value(p[4]))
                if len(p) == 8:
                    nes.set_block_maxsize(self._clean_value([6]))
            elif p[3] == 'bank':
                nes.set_block_bank(self._clean_value(p[4]))
                if len(p) == 8:
                    nes.set_banksize(self._clean_value(p[6]))
            elif p[3] == 'banksize':
                nes.set_banksize(self._clean_value(p[1]), self._clean_value(p[4]))
            elif p[3] == 'link':
                nes.set_block_link(p[4])
            elif p[3] == 'end':
                nes.end_block()
        elif p[1] == 'setpad':
            nes.set_padding(self._clean_value(p[2]))
        elif p[1] == 'align':
            nes.set_alignment(self._clean_value(p[2]))
        '''

        if len(p) == 3:
            p[0] = ('nes_pp_statement', p[1], p[2])
        else:
            p[0] = ('nes_pp_statement', p[1], [])

    # must have a p_error rule
    def p_error(self, p):
        if p != None:
            print "Syntax error in input! File: %s, Line: %s" % (Session().get_cur_file(), p.lineno)
        import pdb; pdb.set_trace()
"""
