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

from hlakit.common.buffer import Buffer

class RomFileBank(object):

    def __init__(self, number, maxsize=0, type_=None, padding=None):
        self._blocks = {}
        self._cur_block = None
        self._number = number
        self._max_size = maxsize
        self._type = type_
        self._padding = padding

    def save(self, outf):
        raise ParseFatalException("no CPU/Platform specific rom bank save function defined")

    def load(self, inf):
        raise ParseFatalException("no CPU/Platform specific rom bank load function defined")

    def _check_block(self):
        if self._cur_block is None:
            raise ParseFatalException("no current block defined in rom bank")
        if not self._blocks.has(self._cur_block):
            raise ParseFatalException("invalid current block addr: %d" % self._cur_block)

    def get_current_block_addr(self):
        return self._cur_block

    def get_current_block(self):
        self._check_block()
        return self._blocks[self._cur_block]

    def get_offset(self):
        self._check_block()
        return self.get_current_block().get_cur_offset()

    def get_size(self):
        self._check_block()
        total = 0
        for block in self._blocks.itervalues():
            total += block.get_cur_offset()
        return total

    def get_free(self):
        self._check_block()
        if self._max_size == 0:
            raise ParseFatalException("#tell.bankfree on bank with no max size")

        return (self._max_size - self.get_bank_size())

    def get_type(self):
        # overload in CPU/Platform versions to make this mean something
        return self._type

    def get_maxsize(self):
        return self._max_size

    def set_maxsize(self, maxsize):
        self._max_size = maxsize

    def get_number(self):
        return self._number

    def _block_overlap(self, baseaddr, maxsize):
        self._check_block()
        for (k, v) in self._blocks.iteritems():
            if v.get_maxsize() > 0:
                if (baseaddr > k) and (baseaddr <= (k + v.get_maxsize())):
                    return True
            if maxsize > 0:
                if (k > baseaddr) and (k <= (baseaddr + maxsize)):
                    return True
        return False

    def create_rom_block(self, baseaddr, maxsize=0):
        if self._block_overlap(baseaddr, maxsize):
            raise ParseFatalException("conflicting #rom.org, overlaps with existing rom block in bank %d" % self.get_number())

        if self._blocks.has(baseaddr):
            raise ParseFatalException("conflicting #rom.org, rom block already exists in bank %d" % self.get_number())

        # create the new block
        self._blocks[baseaddr] = Buffer(baseaddr, maxsize, self._padding)

        # set the current block addr
        self._cur_block = baseaddr

