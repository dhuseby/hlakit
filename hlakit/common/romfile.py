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

from hlakit.common.romfilebank import RomFileBank

class RomFile(object):

    def __init__(self):
        self._ram_pos = None
        self._ram_maxsize = None
        self._banks = {}
        self._cur_bank = None
        self._padding = 0
        self._banksize = 0

    def save(self, outf):
        raise ParseFatalException("no CPU/Platform specific romfile save function defined")

    def load(self, inf):
        raise ParseFatalException("no CPU/Platform specific romfile load function defined")

    def get_current_bank_number(self):
        return self._cur_bank

    def set_current_bank_number(self, bank):
        self._cur_bank = int(bank)

    def _check_bank(self):
        if self._cur_bank is None:
            raise ParseFatalException("no current bank defined")
        if not self._banks.has(self._cur_bank):
            raise ParseFatalException("invalid current bank number: %d" % self._cur_bank)

    def get_current_bank(self):
        self._check_bank()
        return self._banks[self._cur_bank]

    def incbin(self, data):
        self.write_bytes(data)

    def set_rom_banksize(self, banksize):
        for v in self._banks.itervalues():
            v.set_maxsize(banksize)

    def _get_new_rom_bank(self, bank, maxsize, type, padding):
        return RomFileBank(bank, maxsize, type, padding)

    def set_rom_bank(self, bank, maxsize=None, type_=None):
        bank = int(bank)
        if maxsize is None:
            maxsize = self._banksize

        # if the bank doesn't exist, create it
        if bank not in self._banks.keys():
            self._banks[bank] = self._get_new_rom_bank(bank, int(maxsize), type_, self._padding)

        # set the current bank index
        self._cur_bank = bank


    """
    def set_rom_org(self, addr, maxsize=None):
        self._rom_pos = int(addr)
        self._rom_maxsize = maxsize

    def set_rom_end(self):
        self._rom_pos = 0
        self._rom_maxsize = None

    def get_rom_pos(self):
        return self._rom_pos

    def increment_rom_pos(self, amt = 1):
        self._rom_pos += amt
        if self._rom_maxsize and (self._rom_pos >= self._rom_maxsize):
            return False
        return True
    """


    def get_ram_pos(self):
        return self._ram_pos

    def set_ram_org(self, addr, maxsize=None):
        self._ram_pos = int(addr)
        self._ram_maxsize = maxsize

    def set_ram_end(self):
        self._ram_pos = 0
        self._ram_maxsize = None

    def increment_ram_pos(self, amt = 1):
        self._ram_pos += amt
        if self._ram_maxsize and (self._ram_pos >= self._ram_maxsize):
            raise ParseFatalException("writing past ram maxsize")

    def set_padding(self, padding):
        self._padding = padding

    def get_padding(self):
        return self._padding

    def set_align(self, align):
        pass

    def write_bytes(self, bytes=[]):
        pass


