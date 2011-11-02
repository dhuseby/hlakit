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
from hlakit.common.session import CommandLineError
from pplexer import PPLexer
from ppparser import PPParser
import pprint
import cStringIO

class PPBlock(object):

    def __init__(self, type_=None, align=None, padding='0xFF', banksize=None):
        self.type = type_
        self.org = None
        self.maxsize = None
        self.bank = None
        self.banksize = banksize
        self.padding = padding
        self.alignment = align
        self.link = None
        self.ended = False
        self.lines = []

    def __str__(self):
        out = cStringIO.StringIO()
        s = '('
        if self.type:
            s = '%s ' % self.type.upper()
        if self.org:
            s += 'Org: %s ' % self.org
        if self.maxsize:
            s += 'Maxsize: %s ' % self.maxsize
        if self.bank:
            s += 'Bank: %s ' % self.bank
        if self.banksize:
            s += 'Banksize: %s ' % self.banksize
        if self.padding:
            s += 'Padding: %s ' % self.padding
        if self.alignment:
            s += 'Alignment: %s ' % self.alignment
        if self.link:
            s += 'Link: %s ' % self.link
        s += '\n'
        out.write(s)
        pprint.pprint(self.lines, out)
        out.write(')')
        val = out.getvalue()
        out.close()
        return val


class NES(Target):
    
    def __init__(self, cpu=None):

        super(NES, self).__init__()

        self._cpu = cpu

        # preprocessor lexer and parser
        self._pp_lexer = PPLexer()
        self._pp_parser = PPParser(tokens=self._pp_lexer.tokens)

        # initialize the current block member
        self._block = None
        self._alignment = None
        self._padding = None
        self._banksize = { 'rom': '16K', 'ram': '16K', 'chr': '16K' }

        # initially turn #ines.off to False
        self.__setitem__('off', False)

        # start the initial block
        self.start_block()

    def lexer(self):
        return None

    def parser(self):
        return None

    def pp_lexer(self):
        return self._pp_lexer

    def pp_parser(self):
        return self._pp_parser

    def has_ended_block(self):
        if self._block is None:
            return False
        return self._block.ended

    def append_to_block(self, p):
        if self._block is None:
            raise Exception('no block defined')

        if isinstance(p, list):
            self._block.lines += p
        else:
            self._block.lines.append(p)

    def start_block(self, type_=None):
        if self._block != None:
            raise Exception('starting a new block before closing previous block')

        self._block = PPBlock(type_, self._alignment, self._padding, self._banksize)

    def end_block(self):
        if self._block is None:
            raise Exception('trying to end a block before starting one')
        self._block.ended = True

    def get_block(self):
        return self._block

    def clear_block(self):
        if self._block != None and self._block.ended == False:
            raise Exception('clearing a non-ended block')
        block = self._block
        self._block = None
        return block

    def set_block_org(self, org):
        if self._block is None:
            raise Exception('no block defined')
        self._block.org = org

    def set_block_maxsize(self, maxsize):
        if self._block is None:
            raise Exception('no block defined')
        self._block.maxsize = maxsize

    def set_block_bank(self, bank):
        if self._block is None:
            raise Exception('no block defined')
        self._block.bank = bank

    def set_block_link(self, link):
        if self._block is None:
            raise Exception('no block defined')
        self._block.link = link

    def set_block_type(self, type_):
        if self._block is None:
            raise Exception('no block defined')
        self._block.type = type_

    def set_alignment(self, align):
        self._alignment = align
        if self._block != None:
            self._block.alignment = align

    def set_padding(self, padding):
        self._padding = padding
        if self._block != None:
            self._block.padding = padding

    def set_banksize(self, type_, banksize):
        self._banksize[type_] = banksize
        
