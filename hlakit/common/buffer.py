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

import sys
from struct import *
from math import floor, ceil, log

class Buffer(object):
    """
    This class is the base class for any/all binary data buffers.  This can be
    used for building blocks of ROM data and the overall ROM image.
    """

    BYTE_ORDER = ''

    def __init__(self, org, maxsize=None):
        self._buffer = []
        self._org = org
        self._maxsize = maxsize
        self._current_size = None
        self._current_write = None
        self._current_read = None
        self._padding_value = None
        self._alignment = None
        self._buffer = []

    def _pad_with_value(self, start, length, value):
        if (not isinstance(value, list)) and (not isinstance(value, str)):
            raise TypeError('_pad_with_list given incorrect padding value type')

        # figure out where in the padding value the start index lands
        j = start % len(value)

        # padd the buffer with the values
        for i in range(0, length):
            self._buffer[start + i] = value[j]
            j = (j + 1) % len(value)

    def _get_int_padding(self, value):
        padding_list = []

        # calculate the number of bytes needed to store the padding value
        if value == 0:
            num_bytes = 1
        else:
            num_bytes = int(ceil((floor(log(value, 2)) + 1) / 8))
        
        if num_bytes > 8:
            raise TypeError('numeric padding value too large')

        # pack the value into a binary string
        packed = ''
        if (num_bytes > 4) and (num_bytes <= 8):
            packed = pack(self.BYTE_ORDER + 'Q', value)
        elif (num_bytes > 2) and (num_bytes <= 4):
            # NOTE: use 'I' instead of 'L' because 'L' is 8 bytes long on
            # 64-bit systems.
            packed = pack(self.BYTE_ORDER + 'I', value)
        elif num_bytes == 2:
            packed = pack(self.BYTE_ORDER + 'H', value)
        elif num_bytes == 1:
            packed = pack(self.BYTE_ORDER + 'B', value)
        
        return packed 

    def _get_str_padding(self, value):
        return value

    def _pad_buffer(self, start, len):
        if isinstance(self._padding_value, str):
            padding_list = self._get_str_padding(self._padding_value)
        else:
            padding_list = self._get_int_padding(self._padding_value)
        self._pad_with_value(start, len, padding_list)

    def _check_buffer_size(self):
        if self._current_write < len(self._buffer):
            return

        self.reserve(self._current_write)

    def save(self, outf):
        for b in self._buffer:
            outf.write(b)

    def set_padding_value(self, value):
        if isinstance(value, str) or isinstance(value, int):
            self._padding_value = value
            return

        raise TypeError('invalid padding value type, must be a string or int')

    def reserve(self, size):
        # make sure we're not overrunning a buffer
        if (self._maxsize != None) and (size >= self._maxsize):
            raise IndexError('writing past buffer maxsize') 

        # remember where to start filling with padding bytes
        pad_start = len(self._buffer)

        # figure out how much we need to extend the buffer
        ext = size - len(self._buffer) 

        # extend the buffer
        self._buffer.extend([None] * ext)

        # fill with padding value
        self._pad_buffer(pad_start, ext)

    def write_byte(self, value):
        # make sure the buffer is large enough
        self._check_buffer_size()

        # pack the value into the buffer array
        self._buffer[self._current_write] = pack('B', value)

        # move the write location to the next byte
        self._current_write += 1

    def __str__(self):
        return 'Buffer'

    __repr__ = __str__

