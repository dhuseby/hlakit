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

class RomFile(object):

    def __init__(self):
        self._cur_bank = 0

    def save(self, outf):
        pass

    def get_current_bank(self):
        return self._cur_bank

    def set_current_bank(self, bank):
        self._cur_bank = int(bank)

    def get_current_offset(self):
        # TODO: get the current write position in the current buffer
        return 0

    def get_current_banksize(self):
        # TODO: get current bank size from cumulation of buffer sizes
        return 0

    def get_current_bankfree(self):
        # TODO: get current bank free
        return 0

    def get_current_banktype(self):
        # TODO: track the current bank type
        return 'ROM'

    def incbin(self, data):
        # TODO: create a new buffer to contain the binary data
        pass

    def set_rom_org(self, addr, maxsize=None):
        pass

    def set_rom_end(self):
        pass

    def set_rom_banksize(self, banksize):
        pass

    def set_rom_bank(self, bank, maxsize=None):
        pass

    def set_ram_org(self, addr, maxsize=None):
        pass

    def set_ram_end(self):
        pass

    def set_padding(self, padding):
        pass

    def set_align(self, align):
        pass

