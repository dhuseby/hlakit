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

class RomCursor(object):

    def __init__(self, segment, counter, maxsize, segment_size):
        self._base_segment = segment
        self._base_counter = counter
        self._segment_size = segment_size
        self._max_size = maxsize
        self._cur_segment = segment
        self._cur_counter = counter

    def get_segment(self):
        return self._cur_segment

    def get_counter(self):
        return self._cur_counter

    def get_maxsize(self):
        return self._max_size

    def get_size(self):
        return ((self._cur_segment - self._base_segment) * self._segment_size) + self._cur_counter

    def get_free(self):
        return self._max_size - self.get_size()

    def _calculate_address(self, segment, counter):
        return (segment * self._segment_size) + counter

    def get_base_address(self):
        return self._calculate_address(self._base_segment, self._base_counter)

    def get_cur_address(self):
        return self._calculate_address(self._cur_segment, self._cur_counter)

    def get_maxsize(self):
        return self._max_size

    def _check_bounds(self, segment, counter):
        if segment > 255:
            ParseFatalException("invalid Lnx banke segment: %d" % segment)

        if counter >= self._segment_size:
            ParseFatalException("invalid Lnx segment counter: %d" % counter)

        base_address = self._calculate_address(self._base_segment, self._base_counter)
        check_address = self._calculate_address(segment, counter)

        if (check_address - base_address) >= self._max_size:
            return ParseFatalException("overrunning bounds of current #rom.org (maxsize: %d)" % self._max_size)

    def inc_ptr(self, num_bytes):
        new_segment = self._cur_segment
        new_counter = self._cur_counter
        
        while (num_bytes > 0):
            if (new_counter + num_bytes) >= self._segment_size:
                new_segment += 1
                num_bytes -= (self._segment_size + new_counter)
                new_counter = 0
            else:
                new_counter += num_bytes
                num_bytes = 0

        # make sure the new location isn't beyond the maxsize
        self._check_bounds(new_segment, new_counter)

        # update cursor location
        self._cur_segment = new_segment
        self._cur_counter = new_counter


class RamCursor(object):

    PAGE_SIZE = 256

    def __init__(self, page, offset, maxsize):
        self._base_page = page
        self._base_offset = offset
        self._max_size = maxsize
        self._cur_page = page
        self._cur_offset = offset

    def get_page(self):
        return self._cur_page

    def get_offset(self):
        return self._cur_offset

    def get_maxsize(self):
        return self._max_size

    def get_size(self):
        return ((self._cur_page - self._base_page) * self.PAGE_SIZE) + self._cur_offset

    def get_free(self):
        return self._max_size - self.get_size()

    def _calculate_address(self, page, offset):
        return (page * self.PAGE_SIZE) + offset

    def get_base_address(self):
        return self._calculate_address(self._base_page, self._base_offset)

    def get_cur_address(self):
        return self._calculate_address(self._cur_page, self._cur_offset)

    def get_maxsize(self):
        return self._max_size

    def _check_bounds(self, page, offset):
        if page > 255:
            ParseFatalException("invalid Lynx page: %d" % page)

        if offset >= self.PAGE_SIZE:
            ParseFatalException("invalid Lynx offset: %d" % offset)

        base_address = self._calculate_address(self._base_page, self._base_offset)
        check_address = self._calculate_address(page, offset)

        if (check_address - base_address) >= self._max_size:
            return ParseFatalException("overrunning bounds of current #ram.org (maxsize: %d)" % self._max_size)

    def inc_ptr(self, num_bytes):
        new_page = self._cur_page
        new_offset = self._cur_offset
        
        while (num_bytes > 0):
            if (new_offset + num_bytes) >= self.PAGE_SIZE:
                new_page += 1
                num_bytes -= (self.PAGE_SIZE + new_offset)
                new_offset = 0
            else:
                new_offset += num_bytes
                num_bytes = 0

        # make sure the new location isn't beyond the maxsize
        self._check_bounds(new_page, new_offset)

        # update cursor location
        self._cur_page = new_page
        self._cur_offset = new_offset



