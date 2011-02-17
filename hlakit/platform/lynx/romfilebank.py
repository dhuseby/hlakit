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
from hlakit.platform.lynx.cursors import RomCursor


class RomFileBank(object):

    def __init__(self, bank, maxsize=0, type_=None, padding=0, segment_size=0):
        #NOTE: maxsize is ignored

        self._bank = bank
        self._segments = []
        self._cursor = None
        self._type = type_
        self._padding = padding
        self._segment_size = segment_size

        if segment_size == 0:
            raise ValueError("initializing Lnx bank without segment size")

        # pre-allocate the blocks for the segments
        for i in range(0,256):
            self._segments.append(Buffer(self._get_base_addr(i), 
                                         self._segment_size, self._padding))

    def save(self, outf):
        for b in self._segments:
            b.save(outf)

    def load(self, inf):
        for b in self._segments:
            b.load(inf, self._segment_size)

    def _check_segment(self):
        if self._cursor is None:
            raise RuntimeError("no current #rom.org defined in rom bank")

    def get_current_block(self):
        self._check_segment()
        return self._segments[self._cursor.get_segment()]

    def get_bank(self):
        return self._bank

    def get_size(self):
        # NOTE: just adds up the amount of data written into each block
        total = 0
        for b in self._segments:
            total += b.get_write_pos()
        return total

    def get_current_addr(self):
        self._check_segment()
        return self._cursor.get_cur_address()

    def get_current_org(self):
        self._check_segment()
        return self._cursor.get_base_address()

    def get_current_maxsize(self):
        self._check_segment()
        return self._cursor.get_maxsize()

    def get_segment(self):
        self._check_segment()
        return self._cursor.get_segment()

    def get_counter(self):
        self._check_segment()
        return self._cursor.get_counter()
 
    def get_free(self):
        return (256 * self._segment_size) - self.get_size()

    def _get_base_addr(self, segment, counter=0):
        return (segment * self._segment_size) + counter

    def set_rom_org(self, segment, counter, maxsize):
        if counter > self._segment_size:
            raise ValueError("counter offset in segment is greater than segment size")

        if (segment < 0) or (segment > 255):
            raise ValueError("invalid segment number")

        if self._cursor is None:
            self._cursor = RomCursor(segment, counter, maxsize, self._segment_size)
        else:
            raise RuntimeError("#rom.org before #rom.end of previous #rom.org")

    def set_rom_end(self):
        if self._cursor is None:
            raise RuntimeError("#rom.end before #rom.org")

        # clean up the cursor
        self._cursor = None

    def write_bytes(self, bytes):
        if not isinstance(bytes, list):
            raise ValueError("bytes parameter must be an array of bytes")

        if self._cursor is None:
            raise RuntimeError("No #rom.org currently defined")

        # write the bytes over multiple segments if needed
        start = 0
        while True:
            # write the bytes
            written = self.get_current_block().write_bytes(bytes[start:])

            # move the rom cursor
            self._cursor += written

            # move start index
            start += written

            if start == len(bytes):
                break;

    def get_debug_str(self):
        s = "\tNum Segments: %d\n" % len(self._segments)
        s += "\tType: %s\n" % self._type
        s += "\tPadding: %s\n" % self._padding
        s += "\tSegment Size: %s\n" % self._segment_size
        if self._cursor != None:
            s += "\tCurrent Pos:\n"
            s += self._cursor.get_debug_str()
        return s
