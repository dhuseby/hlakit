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

import os
import sys
from struct import *
from exceptions import ValueError, MemoryError
from math import floor, ceil, log

class Buffer(object):

    def __init__(self, org=None, maxsize=None, padding=None):
        self._data = []
        self.org = org
        self.maxsize = maxsize
        self.padding = padding
        self.alignment = None

    def save(self, fout):
        # TODO: check alignment and pad out to alignment using correct endianess
        # TODO: check maxsize and raise error if exceeded
        pass
    
    def append_bytes(self, data):

        if self.maxsize and len(self._data) + len(data) > self.maxsize:
            raise MemoryError('buffer exceeds declared max size')

        for d in data:
            self._data.append(pack("B", d))

    def __str__(self):
        s = 'Buffer --'
        if self.org != None:
            s += ' Org: 0x%0.4x' % self.org
        else:
            s += ' Org: None'
        if self.maxsize != None:
            s += ', Max Size: 0x%0.4x' % self.maxsize
        else:
            s += ', Max Size: None'
        if isinstance(self.padding, int):
            s += ', Padding: 0x%0.4x' % self.padding
        else:
            s += ', Padding: "%s"' % self.padding
        if self.alignment != None:
            s += ', Alignment: 0x%0.4x' % self.alignment
        else:
            s += ', Alignment: None'
        s += ', Length: 0x%0.4x' % len(self._data)
        return s

    __repr__ = __str__
        

class Buffers(object):
    
    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    LITTLE_ENDIAN = '<'
    BIG_ENDIAN = '>'

    def _check_state(self):
        if getattr(self, '_buffers', None) is None:
            self._buffers = [ Buffer() ]
        if getattr(self, '_tags', None) is None:
            self._tags = {}
        if getattr(self, '_endianess', None) is None:
            self._endianess = None

    @property
    def buffer(self):
        self._check_state()
        return self._buffers[-1]

    # make buffer property read-only
    @buffer.setter
    def buffer(self, a):
        pass

    @property
    def endianess(self):
        self._check_state()
        return self._endianess

    @endianess.setter
    def endianess(self, e):
        if e not in ('<','>'):
            raise ValueError('endianess must be Buffers.LITTLE_ENDIAN or Buffers.BIG_ENDIAN')
        self._endianess = e

    def new_buffer(self):
        self._check_state()
        self._buffers.append( Buffer() )

    def add_tag(self, tag):
        self._check_state()
        # add a tag mapping to the current buffer
        self._tags[tag] = self.buffer

    def __len__(self):
        self._check_state()
        return len(self._buffers)

    def __getitem__(self, idx):
        self._check_state()
        if type(idx) == types.IntType:
            if idx >= 0 and idx < len(self._buffers):
                return self._buffers[idx]
        elif type(idx) in types.StringTypes:
            if self._tags.has_key(idx):
                return self._tags[idx]
        raise IndexError('invalid buffer index: %s' % idx)

    # make array access read-only
    def __setitem__(self, idx, value):
        pass


