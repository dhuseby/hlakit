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

from hlakit.common.target import Target
from hlakit.common.session import CommandLineError, Session
from pplexer import PPLexer
from ppparser import PPParser
from lexer import Lexer
from parser import Parser
import copy

class NES(Target):
    
    def __init__(self, cpu=None):

        super(NES, self).__init__()

        self._cpu = cpu

        # preprocessor lexer and parser
        self._pp_lexer = PPLexer()
        self._pp_parser = PPParser(tokens=self._pp_lexer.tokens)

        # compiler lexer and parser
        self._lexer = Lexer()
        self._parser = Parser(tokens=self._lexer.tokens)

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

