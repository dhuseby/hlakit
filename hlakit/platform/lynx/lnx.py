"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

from struct import pack, unpack
from binascii import crc32
from ctypes import c_uint32
from pyparsing import *
from hlakit.common.session import Session
from hlakit.common.numericvalue import NumericValue

class Lnx(object):
    """
    This class encapsulates the .lnx header that will be written with
    the ROM image.
    
    here's how version 1 headers are defined in the make_lnx code:

    typedef struct
    {
      UBYTE   magic[4];
      UWORD   page_size_bank0;
      UWORD   page_size_bank1;
      UWORD   version;
      char    cartname[32];
      char    manufname[16];
      UBYTE   rotation;
      UBYTE   spare[5];
    }LYNX_HEADER_NEW;

    here's how the proposed version 2 headers are defined:

    typedef struct
    {
      UBYTE   magic[4];
      UBYTE   num_banks;
      UBYTE   use_cart_strobe;
      UWORD   save_game_size;
      UWORD   version;
      char    cartname[32];
      char    manufname[16];
      UBYTE   rotation;
      UBYTE   spare[5];
    }LYNX_HEADER_NEW;

    """

    ROTATE_NONE, ROTATE_LEFT, ROTATE_RIGHT = range(3)
    ROTATIONS = ( 'None', 'Left', 'Right' )

    def __init__(self, inf=None):
        # version 1 specific
        self._page_size_bank0 = None
        self._page_size_bank1 = None

        # version 2 specific
        self._num_banks = None
        self._use_cart_strobe = None
        self._save_game_size = None

        # common
        self._version = None
        self._cart_name = ''
        self._manufacturer_name = ''
        self._rotation = self.ROTATE_NONE

        # the banks of data
        self._banks = []

        # the save game data
        self._save_game_data = None

        if inf:
            self._unpack_header(inf)
            self._unpack_banks(inf)

    def save(self, outf):
        self._pack_header(outf)
        self._pack_banks(outf)

    def _unpack_header(self, inf):

        # read in the magic characters
        magic = inf.read(4)
        magic = unpack('cccc', magic)
        if (magic[0] != 'L') or \
           (magic[1] != 'Y') or \
           (magic[2] != 'N') or \
           (magic[3] != 'X'):
               raise SyntaxError(inf.name, 0, 0, 'invalid magic value in .lnx file')

        # read in sizes, but we unpack it differently based on version
        sizes = inf.read(4)

        # read in the file version
        version = inf.read(2)
        self._version = unpack('<H', version)[0]

        if self._version == 1:
            self._page_size_bank0, self._page_size_bank1 = unpack('<HH', sizes)
        elif self._version == 2:
            self._num_banks, self._use_cart_strobe, self._save_game_size = unpack('<BBH')
        else:
            raise SyntaxError(inf.name, 0, 8, 'invalid .lnx file version')

        # read in the cart name
        cartname = inf.read(32)
        self._cart_name = unpack('32s', cartname)[0]

        # read in the manufacturer name
        manufname = inf.read(16)
        self._manufacturer_name = unpack('16s', manufname)[0]

        # read in the rotation
        rotation = inf.read(1)
        self._rotation = unpack('B', rotation)[0]
        if (self._rotation != self.ROTATE_NONE) and \
           (self._rotation != self.ROTATE_LEFT) and \
           (self._rotation != self.ROTATE_RIGHT):
               raise SyntaxError(inf.name, 0, 58, 'invalid rotation in .lnx file')

        # read in the spare bytes to put the file pointer at the first byte in
        # the rom bank. 
        spare = inf.read(5)

    def _unpack_banks(self, inf):
        if self._version == 1:
            # load bank 0
            self._banks.append(inf.read(256 * self._page_size_bank0))

            # load bank 1 if needed
            if self._page_size_bank1 > 0:
                self._banks.append(inf.read(256 * self._page_size_bank1))

        elif self._version == 2:
            # load the bank 0 banks
            for i in range(0, self._num_banks):
                self._banks.append(inf.read(256 * 2048))

            # load the bank 1 banks if needed
            if self._use_cart_strobe:
                for i in range(0, self._num_banks):
                    self._banks.append(inf.read(256 * 2048))

            # load the save game data if needed
            if self._save_game_size > 0:
                self._save_game_data = inf.read(256 * self._save_game_size)

        else:
            raise SyntaxError(inf.name, 0, 64, 'cannot load banks, invalid .lnx version')

    def _pack_header(self, outf):
        pass

    def _pack_banks(self, outf):
        pass

    def __str__(self):
        s = 'Atari Lynx ROM\n'
        s += '\tVersion: %d\n' % self._version
        if self._version == 1:
            s += '\tBank 0 Page Size: %d\n' % self._page_size_bank0
            s += '\tBank 1 Page Size: %d\n' % self._page_size_bank1
        elif self._version == 2:
            s += '\tNumber of Banks: %d\n' % self._num_banks
            s += '\tUse Cart Strobe: %s\n' % ('False', 'True')[self._use_cart_strobe]
            s += '\tSave Game Size: %d\n' % self._save_game_size
        s += '\tCart Name: %s\n' % self._cart_name
        s += '\tManufacturer Name: %s\n' % self._manufacturer_name
        s += '\tRotation: %s\n' % self.ROTATIONS[self._rotation]
        if self._version == 1:
            s += '\tBank 0 Checksum: %s\n' % str(hex(c_uint32(crc32(self._banks[0])).value))[:-1]
            if self._page_size_bank1 > 0:
                s += '\tBank 1 Checksum: %s\n' % str(hex(c_uint32(crc32(self._banks[1])).value))[:-1]
        elif self._version == 2:
            crc = crc32(self._banks[0])
            for i in range(1, self._num_banks):
                crc = crc32(self._banks[i], crc)
            s += '\tBank 0 Checksum: %s\n' % str(hex(c_uint32(crc).value))[:-1]

            if self._use_cart_strobe:
                crc = crc32(self._banks[self._num_banks])
                for i in range(self._num_banks + 1, self._num_banks + self._num_banks):
                    crc = crc32(self._banks[i], crc)
                s += '\tBank 1 Checksum: %s\n' % str(hex(c_uint32(crc).value))[:-1]

            if self._save_game_size > 0:
                s += '\tSave Game Checksum: %s\n' % str(hex(c_uint32(crc).value))[:-1]

        return s

class LnxOff(object):
    """
    This defines the rules for parsing a #lnx.off line 
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        return klass()

    @classmethod
    def exprs(klass):
        kw = Keyword('#lnx.off')

        expr = Suppress(kw) + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __str__(self):
        return 'LnxOff'

    __repr__ = __str__


