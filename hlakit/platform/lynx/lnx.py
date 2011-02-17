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

from struct import pack, unpack
from binascii import crc32
from ctypes import c_uint32
from hlakit.common.numericvalue import NumericValue
from hlakit.common.arrayvalue import StringValue
from hlakit.common.buffer import Buffer
from hlakit.cpu.mos6502.romfile import MOS6502RomFile
from hlakit.platform.lynx.romfilebank import RomFileBank as LnxRomFileBank
from hlakit.platform.lynx.cursors import RamCursor

class ListingLine(object):

    def __init__(self, bank, segment, counter, addr):
        self._bank = bank
        self._segment = segment
        self._counter = counter
        self._addr = addr
        self._label = None
        self._code = None
        self._fn = None
        self._bytes = []

    def set_org(self, addr):
        self._code = '.org $' + hex(addr)[2:].zfill(4).upper()

    def set_end(self):
        self._code = '.end'

    def set_code(self, code):
        self._code = str(code)

    def set_fn(self, fn):
        self._fn = str(fn)

    def set_bytes(self, bytes):
        self._bytes = bytes

    def set_label(self, label):
        self._label = label

    def __str__(self):
        s = hex(self._bank)[2:].zfill(2).upper() + ' '
        s += hex(self._segment)[2:].zfill(2).upper() + ' '
        s += hex(self._counter)[2:].zfill(3).upper() + ' '
        s += hex(self._addr)[2:].zfill(4).upper() + '    '
        if self._label != None:
            s += (' ' * (16 - len(str(self._label)))) + str(self._label) + ':    '
        else:
            s += ' ' * 21

        if len(self._bytes) == 0:
            s += ' ' * 12
        elif len(self._bytes) == 1:
            s += hex(self._bytes[0])[2:].zfill(2).upper() + (' ' * 10)
        elif len(self._bytes) == 2:
            s += hex(self._bytes[0])[2:].zfill(2).upper() + ' '
            s += hex(self._bytes[1])[2:].zfill(2).upper() + (' ' * 7)
        elif len(self._bytes) == 3:
            s += hex(self._bytes[0])[2:].zfill(2).upper() + ' '
            s += hex(self._bytes[1])[2:].zfill(2).upper() + ' '
            s += hex(self._bytes[2])[2:].zfill(2).upper() + '    '

        if self._code != None:
            s += self._code + (' ' * (16 - len(self._code)))
        else:
            s += ' ' * 16
        
        if self._fn != None:
            s += self._fn
        
        return s

    __repr__ = __str__


class Lnx(MOS6502RomFile):
    """
    This class encapsulates the .lnx header that will be written with
    the ROM image.
    
    here's how version 1 headers are defined in the make_lnx code:

    typedef struct {
      UBYTE   magic[4];
      UWORD   page_size_bank0;
      UWORD   page_size_bank1;
      UWORD   version;
      char    cartname[32];
      char    manufname[16];
      UBYTE   rotation;
      UBYTE   spare[5];
    } LYNX_HEADER_NEW;

    here's how the proposed version 2 headers are defined:

    typedef struct {
      UBYTE   magic[4];
      UBYTE   num_banks;
      UBYTE   use_cart_strobe;
      UWORD   save_game_size;
      UWORD   version;
      char    cartname[32];
      char    manufname[16];
      UBYTE   rotation;
      UBYTE   spare[5];
    } LYNX_HEADER_NEW;

    """

    ROTATE_NONE, ROTATE_LEFT, ROTATE_RIGHT = range(3)
    ROTATIONS = ( 'none', 'left', 'right' )
    ROTATION_BY_NAME = { 'none': ROTATE_NONE,
                         'left': ROTATE_LEFT,
                         'right': ROTATE_RIGHT }
    VERSION_2_SEGMENT_SIZE = 2048

    def __init__(self, inf=None):
        # no header flag
        self._no_header = False

        # version 1 specific
        self._segment_size_bank0 = None
        self._segment_size_bank1 = None

        # version 2 specific
        self._num_banks = None
        self._use_cart_strobe = None
        self._save_game_size = None

        # common
        self._version = 1
        self._cart_name = ''
        self._manufacturer_name = ''
        self._rotation = self.ROTATE_NONE

        self._spare = '\x00' * 5

        # the save game data
        self._save_game_data = None

        # label locations used for resolving relative jumps
        self._labels = {}
        self._cur_label = None

        # RAM cursor for tracking RAM location for locating
        self._cursor = None

        # listing lines
        self._listing = []

        # the loader function name
        self._loader_fn = None

        # variable location pointer
        self._next_variable_slot = 0

        if inf:
            self._unpack_header(inf)
            self._unpack_banks(inf)

        super(Lnx, self).__init__()

    # Lynx specific overloads

    def save(self, outf):
        if not self._no_header:
            self._pack_header(outf)
        self._pack_banks(outf)

    def load(self, inf):
        self._unpack_header(inf)
        self._unpack_banks(inf)

    def load_header(self, inf):
        self._unpack_header(inf)

    def save_header(self, outf):
        self._pack_header(outf)

    def _get_segment_size(self, bank):
        if self._version == 1:
            if bank == 0:
                return self._segment_size_bank0;
            elif bank == 1:
                return self._segment_size_bank1;
            else:
                raise ValueError("invalide bank number: %d for version 1 Lnx rom")
        elif self._version == 2:
            return VERSION_2_SEGMENT_SIZE

        raise RuntimeError("invalid Lnx rom version")
         
    def _get_new_rom_bank(self, bank, maxsize, type, padding):
        return LnxRomFileBank(bank, maxsize, type, padding, self._get_segment_size(bank))

    def _check_bank(self):
        if self._cur_bank is None:
            raise RuntimeError("no current bank defined")

    def set_rom_org(self, segment, counter=None, maxsize=None):
        if self._cur_bank is None:
            raise RuntimeError("#rom.org before a #rom.bank declaration")

        if counter is None:
            counter = 0
        if maxsize is None:
            maxsize = 0

        self.get_current_bank().set_rom_org(segment, counter, maxsize)

    def set_rom_end(self):
        if self._cur_bank is None:
            raise RuntimeError("#rom.end before a #rom.org declaration")
        
        self.get_current_bank().set_rom_end()
       
    def _get_page_from_address(self, address):
        return (((address & 0xFF00) >> 8) & 0xFF)

    def _get_offset_from_address(self, address):
        return (address & 0xFF)

    def set_ram_org(self, address, maxsize=0):
        if self._cursor != None:
            raise RuntimeError("#ram.org inside of unclosed #ram.org block")

        self._cursor = RamCursor(self._get_page_from_address(address),
                                 self._get_offset_from_address(address),
                                 maxsize)

        # create a listing line, addr is zero because we're setting up
        # a new ram ord and by definition it is 0
        lline = ListingLine(self.get_current_bank_number(), 
                            self.get_current_bank().get_segment(),
                            self.get_current_bank().get_counter(),
                            0)
        lline.set_org(self._cursor.get_cur_address())

        # add it to the listing
        self._listing.append(lline)

    def set_ram_end(self):
        if self._cursor is None:
            raise RuntimeError("#ram.end without a matching #ram.org")

        lline = ListingLine(self.get_current_bank_number(),
                            self.get_current_bank().get_segment(),
                            self.get_current_bank().get_counter(),
                            self._cursor.get_cur_address())
        lline.set_end()

        # add it to the listing
        self._listing.append(lline)

        # remove the cursor
        self._cursor = None

    def get_cur_ram_page(self):
        if self._cursor is None:
            raise RuntimeError("No #ram.org currently defined")

        return self._cursor.get_page()

    def get_cur_ram_offset(self):
        if self._cursor is None:
            raise RuntimeError("No #ram.org currently defined")

        return self._cursor.get_offset()

    def get_cur_ram_addr(self):
        if self._cursor is None:
            raise RuntimeError("No #ram.org currently defined")

        return self._cursor.get_cur_address()

    def get_address_for_var(self, var):
        """
        if a variable has a parent function set, then it is a local variable 
        inside of a function and only takes up a temporary spot in the zero 
        page.  if it doesn't have a parent function then it is a global 
        variable that needs to be located permanently in the zero page. so
        how do we manage temporary variables in the zero page?  simple, by
        using their scoping information.  when we see a local variable, we
        will grab the first piece of zero page memory that is large enough and
        it is either unallocated, or it is allocated to a local variable that
        is not in the scope stack of the variable being allocated and it is 
        not in any of the scopes of the functions that call the parent function
        of the variable being located.  this seems complicated, but it isn't
        really.
        """

        # the first version just locates all variables inline, in main ram at
        # the current ram cursor location
        if var.get_address() != None:
            return

        # by the time we get here, all variables know their size and initial value
        size = var.get_size()
        var.set_address(self.get_cur_ram_addr())
        self._cursor.inc_ptr(size)

    def set_current_label(self, lbl):
        self._cur_label = str(lbl)

    def write_bytes(self, bytes, line, fn=None):
        if not isinstance(bytes, list):
            raise ValueError("bytes parameter must be an array of bytes")

        if self._cursor is None:
            raise RuntimeError("No #ram.org currently defined")

        # add the debug listing line
        lline = ListingLine(self.get_current_bank_number(),
                            self.get_current_bank().get_segment(),
                            self.get_current_bank().get_counter(),
                            self._cursor.get_cur_address())

        # add the label if there is one
        if self._cur_label != None:
            lline.set_label(self._cur_label)
            self._cur_label = None

        # add the bytes
        if len(bytes) <= 3:
            lline.set_bytes(bytes)

        # add the line
        lline.set_code(line)

        # add the fn
        lline.set_fn(fn)

        # add it to the listing
        self._listing.append(lline)

        # write the bytes to the ROM
        self.get_current_bank().write_bytes(bytes)

        # move the RAM cursor
        self._cursor += len(bytes)

    # Lynx specific romfile settings

    def set_no_header(self):
        self._no_header = True

    def get_no_header(self):
        return self._no_header


    def set_version(self, version):
        version = int(version)
        if (version < 0) or (version > 2):
            raise ValueError('valid .LNX version is 1 or 2')
        self._version = version

    def get_version(self):
        return self._version


    # NOTE: the cart strobe is how Lynx carts switch "banks", it can
    # be used as an additional address line
    def set_use_cart_strobe(self, use_strobe):
        if self._version != 2:
            raise RuntimeError('use cart strobe is only valid in version 2 headers')
        self._use_cart_strobe = use_strobe

    def get_use_cart_strobe(self):
        return self._use_cart_strobe


    def set_save_game_size(self, save_size):
        if self._version != 2:
            raise RuntimeError('save game size is only valid in version 2 headers')
        self._save_game_size = save_size

    def get_save_game_size(self):
        return self._save_game_size


    def set_segment_size_bank0(self, size):
        if self._version != 1:
            raise RuntimeError('bank0 page size is only valid in version 1 headers')
        self._segment_size_bank0 = int(size)

    def get_segment_size_bank0(self):
        return self._segment_size_bank0


    def set_segment_size_bank1(self, size):
        if self._version != 1:
            raise RuntimeError('bank1 page size is only valid in version 1 headers')
        self._segment_size_bank1 = int(size)

    def get_segment_size_bank1(self):
        return self._segment_size_bank1


    def set_cart_name(self, name):
        self._cart_name = str(name)

    def get_cart_name(self):
        return self._cart_name


    def set_manufacturer_name(self, name):
        self._manufacturer_name = str(name)

    def get_manufacturer_name(self):
        return self._manufacturer_name


    def set_rotation(self, rotation):
        if isinstance(rotation, StringValue):
            rotation = str(rotation)
        if isinstance(rotation, NumericValue):
            rotation = int(rotation)
        if isinstance(rotation, str):
            if rotation.lower() not in self.ROTATION_BY_NAME.keys():
                raise ValueError('rotation must be: none, left, or right')
            self._rotation = self.ROTATION_BY_NAME[rotation]
        elif isinstance(rotation, int):
            if rotation not in range(3):
                raise ValueError('rotation must be 0 (none), 1 (left), or 2 (right)')
            self._rotation = rotation
        else:
            raise TypeError('rotation value type must be int or str')

    def get_rotation(self):
        return self._rotation

    def set_loader(self, loader):
        print "setting loader to: %s" % str(loader)
        self._loader_fn = str(loader)

    def get_loader(self):
        return self._loader_fn


    # LOAD/SAVE HELPERS

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
            self._segment_size_bank0, self._segment_size_bank1 = unpack('<HH', sizes)
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
        # the rom bank. save these for later...
        self._spare = inf.read(5)

    def _unpack_banks(self, inf):
        if self._version == 1:
            # load bank 0
            b = LnxRomFileBank(0, segment_size=self._segment_size_bank0)
            b.load(inf)
            self._banks[0] = b

            # load bank 1 if needed
            if self._segment_size_bank1 > 0:
                b = LnxRomFileBank(1, segment_size=self._segment_size_bank1)
                b.load(inf)
                self._banks[1] = b

        elif self._version == 2:
            # load the bank 0 banks
            for i in range(0, self._num_banks):
                b = LnxRomFileBank(i, segment_size=VERSION_2_SEGMENT_SIZE)
                b.load(inf)
                self._banks[i] = b

            # load the bank 1 banks if needed
            if self._use_cart_strobe:
                for i in range(0, self._num_banks):
                    b = LnxRomFileBank(i, segment_size=VERSION_2_SEGMENT_SIZE)
                    b.load(inf)
                    self._banks[self._num_banks + i] = b

            # load the save game data if needed
            if self._save_game_size > 0:
                savesize = 256 * self._save_game_size
                b = Buffer(0, savesize)
                b.load(inf, savesize)
                self._save_game_data = b

        else:
            raise SyntaxError(inf.name, 0, 64, 'cannot load banks, invalid .lnx version')

    def _pack_header(self, outf):

        # write the magic characters
        outf.write(pack('cccc', 'L', 'Y', 'N', 'X'))

        # write out the sizes
        if self._version == 1:
            outf.write(pack('<HH', self._segment_size_bank0, self._segment_size_bank1))
        elif self._version == 2:
            outf.write(pack('<BBH', self._num_banks, self._use_cart_strobe, self._save_game_size))
        else:
            raise SyntaxError(outf.name, 0, 8, 'invalid .lnx file version')

        # write out the version
        outf.write(pack('<H', self._version))

        # write out the cart name
        outf.write(pack('32s', self._cart_name))

        # write out the manufacturer name
        outf.write(pack('16s', self._manufacturer_name))

        # write out the rotation
        outf.write(pack('B', self._rotation))

        # write out the spare bytes
        outf.write(self._spare)

    def _pack_banks(self, outf):
        if self._version == 1:
            # write out bank 0
            self._banks[0].save(outf)

            # write out bank 1
            if self._segment_size_bank1 > 0:
                self._banks[1].save(outf)

        elif self._version == 2:
            # write out all of the banks
            for b in self._banks.itervalues():
                b.save(outf)

            # write out the save game data if any
            if self._save_game_size > 0:
                self._save_game_data.save(outf)

        else:
            raise SyntaxError(outf.name, 0, 64, 'cannot save banks, invalid .lnx version')

    def __str__(self):
        s = 'Atari Lynx ROM\n'
        s += '\tVersion: %d\n' % self._version
        if self._version == 1:
            s += '\tBank 0 Page Size: %d\n' % self._segment_size_bank0
            s += '\tBank 1 Page Size: %d\n' % self._segment_size_bank1
        elif self._version == 2:
            s += '\tNumber of Banks: %d\n' % self._num_banks
            s += '\tUse Cart Strobe: %s\n' % ('False', 'True')[self._use_cart_strobe]
            s += '\tSave Game Size: %d\n' % self._save_game_size
        s += '\tCart Name: %s\n' % self._cart_name
        s += '\tManufacturer Name: %s\n' % self._manufacturer_name
        s += '\tRotation: %s\n' % self.ROTATIONS[self._rotation]
        if self._version == 1:
            s += '\tBank 0 Checksum: %s\n' % str(hex(c_uint32(crc32(self._banks[0])).value))[:-1]
            if self._segment_size_bank1 > 0:
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


    def get_debug_listing(self):
        s = '\nBA SG CNT ADDR               LABELS    00 00 00    CODE            FN\n'
        for l in self._listing:
            s += str(l) + '\n'
        return s

    def get_debug_str(self):
        s = ''
        for (k,v) in self._banks.iteritems():
            s += "Bank %s\n" % k
            s += v.get_debug_str()
        if self._cursor != None:
            s += "Ram Cusor:\n"
            s += self._cursor.get_debug_str()
        return s



