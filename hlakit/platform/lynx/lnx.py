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
from pyparsing import *
from hlakit.common.session import Session
from hlakit.common.numericvalue import NumericValue
from hlakit.common.arrayvalue import StringValue
from hlakit.cpu.mos6502.romfile import MOS6502RomFile
from hlakit.common.buffer import Buffer

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

    def __init__(self, inf=None):
        # no header flag
        self._no_header = False

        # version 1 specific
        self._page_size_bank0 = None
        self._page_size_bank1 = None

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

        # the banks of data
        self._banks = []

        # the save game data
        self._save_game_data = None

        # the state of the ROM building
        self._buffers = []
        self._cur_bank = 0
        self._cur_buffer = None
        self._cur_segment = 0
        self._cur_counter = 0
        self._cur_maxsize = None
        self._cur_ram_addr = 0
        self._cur_padding = 0
        self._loader_fn = None
        self._cur_label = None
        self._rom_lines = []

        # label locations used for resolving relative jumps
        self._labels = {}

        if inf:
            self._unpack_header(inf)
            self._unpack_banks(inf)

        super(Lnx, self).__init__()

    def save(self, outf):
        o = open(outf, 'wb+')
        if not self._no_header:
            self.save_header(o)
        self.save_banks(o)
        o.close()

    def save_header(self, outf):
        self._pack_header(outf)

    def save_banks(self, outf):
        self._pack_banks(outf)

    def load_header(self, inf):
        self._unpack_header(inf)

    def load_banks(self, inf):
        self._unpack_banks(inf)

    def clear_banks(self):
        self._banks = []

    def append_bank(self, inf):
        self._banks.append(inf.read())

    def set_no_header(self):
        self._no_header = True

    def set_version(self, version):
        version = int(version)
        if (version < 0) or (version > 2):
            raise ValueError('valid .LNX version is 1 or 2')
        self._version = version

    def get_version(self):
        return self._version

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

    def set_page_size_bank0(self, size):
        if self._version != 1:
            raise RuntimeError('bank0 page size is only valid in version 1 headers')
        self._page_size_bank0 = int(size)

    def get_page_size_bank0(self):
        return self._page_size_bank0

    def set_page_size_bank1(self, size):
        if self._version != 1:
            raise RuntimeError('bank1 page size is only valid in version 1 headers')
        self._page_size_bank1 = int(size)

    def get_page_size_bank1(self):
        return self._page_size_bank1

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

    def _get_cur_bank_page_size(self):
        if self.get_version() == 1:
            if self._cur_bank == 0:
                if self._page_size_bank0 == None:
                    raise ParseFatalException('switching to a bank 0 without a defined page size')
                return self._page_size_bank0
            else:
                if self._page_size_bank1 == None:
                    raise ParseFatalException('switching to a bank 1 without a defined page size')
                return self._page_size_bank1
        else:
            # version 2 .lnx files have all banks set to maximum size
            return 2048

    def _get_cur_bank_maxsize(self):
        return 256 * self._get_cur_bank_page_size()

    def _get_cur_bank_byte_offset(self):
        return (self._cur_segment * self._get_cur_bank_page_size()) + self._cur_counter

    def set_loader(self, loader):
        self._loader_fn = str(loader)

    def get_loader(self):
        return self._loader_fn

    def set_rom_org(self, segment, counter=None, maxsize=None):
        if self._cur_buffer != None:
            raise ParseFatalException('cannot set rom org while in existing def')

        # initialize the segment, counter, and maxsize
        self._cur_segment = int(segment)
        if counter != None:
            self._cur_counter = int(counter)
        else:
            self._cur_counter = 0
        if maxsize != None:
            self._cur_maxsize = int(maxsize)

        # reset state
        self._in_rom_def = True
        self._rom_dirty = False

        # initialize the new buffer
        org = self._get_cur_bank_byte_offset()
        self._cur_buffer = Buffer(org, self._cur_maxsize, self._cur_padding)

    def set_rom_end(self):
        self._cur_maxsize = None
        self._in_rom_def = False
        self._rom_dirty = False
        # save off the current buffer
        self._buffers.append(self._cur_buffer)
        self._cur_buffer = None
        # TODO: if aligned in any way, move to the next alignment
        # TODO: if padded, make sure that the current ROM gets padded out to either next
        #       alignment or maxsize.

    def set_rom_bank(self, bank, banksize=None):
        bank = int(bank) 
        if self.get_version() == 1:
            if (bank < 0) or (bank > 1):
                raise ParseFatalException('invalid bank number for a version 1 .lnx rom')
        elif self.get_version() == 2:
            if (bank < 0) or (bank > 255):
                raise ParseFatalException('invalid bank number for a version 2 .lnx rom')

        # store the new bank index so that page sizes are correct
        self._cur_bank = int(bank)

        if self._cur_buffer != None:
            # if we're switching banks in a dirty rom, we'll force a rom end
            # and reset the rom state
            print 'WARNING: switching banks in the middle of building a ROM, resetting ROM state'
            self._set_rom_end()
            self._set_rom_org(0, 0)

        # if they specified a banksize, then set it
        if banksize != None:
            self.set_rom_banksize(banksize)
     
    def set_rom_padding(self, padding):
        self._cur_padding = padding
        if self._cur_buffer != None:
            self._cur_buffer.set_padding_value(padding)

    def set_rom_banksize(self, banksize):
        bs = int(banksize)
        if self.get_version() == 1:
            if bs not in (131072, 262144, 524288):
                raise ParseFatalException('invalid lynx bank size, must be 128K, 256K, or 512K')
            if self._cur_bank == 0:
                if self._page_size_bank0 == None:
                    self._page_size_bank0 = int(bs / 256)
                else:
                    if self._page_size_bank0 != int(bs / 256):
                        raise ParseFatalException('banksize mismatch on bank 0')
            else:
                if self._page_size_bank1 == None:
                    self._page_size_bank1 = int(bs / 256)
                else:
                    if self._page_size_bank1 != int(bs / 256):
                        raise ParseFatalException('banksize mismatch on bank 1')
        else:
            if bs != 524288:
                raise ParseFatalException('invalid lynx bank size for a version 2 rom')

    def get_buffers(self):
        return self._buffers

    def set_current_label(self, lbl):
        self._cur_label = str(lbl)

    def set_ram_org(self, addr, maxsize=None):
        # add a line to the debug listing
        self._rom_lines.append((self._cur_bank, self._cur_segment, 
                                self.get_rom_pos(), self.get_ram_pos(),
                                '', [], '.org $%04.0x' % addr))
        super(Lnx, self).set_ram_org(addr, maxsize)

    def get_relative_jmp(self, label):
        if label in self._labels:
            return self._labels[label] - (self._cur_buffer.get_write_pos() + 2)
        return None

    def emit(self, bytes=[], msg=None):
        # add a line to the debug listing
        self._rom_lines.append((self._cur_bank, self._cur_segment, 
                                self.get_rom_pos(), self.get_ram_pos(), 
                                self._cur_label, bytes, msg)) 

        if self._cur_label != None:
            # store the byte that the label refers to
            self._labels[self._cur_label] = self._cur_buffer.get_write_pos()

            # reset the label if there was one
            self._cur_label = None

        # write the bytes to the current buffer and increment the positions
        for b in bytes:
            self._cur_buffer.write_byte(b)
            self.increment_rom_pos()
            self.increment_ram_pos()

    def get_debug_listing(self):
        ll = 0
        for l in self._rom_lines:
            if l[4] != None and len(l[4]) > ll:
                ll = len(l[4])

        s = 'B SG CNT ADDR    LBL%s    00 00 00    CODE\n' % (' ' * (ll - 3))
        for l in self._rom_lines:
            if l[0] is None:
                b = ' '
            else:
                b = '%d' % l[0]
            if l[1] is None:
                sg = '  '
            else:
                sg = '%02.0x' % l[1]
            if l[2] is None:
                cnt = '   '
            else:
                cnt = '%03.0x' % l[2]
            if l[3] is None:
                addr = '    '
            else:
                addr = '%04.0x' % l[3]
            if l[4] is None:
                lbl = '%s' % (' ' * ll)
            else:
                lbl = '%s%s' % (' ' * (ll - len(l[4])), l[4][:ll])
            if len(l[5]) > 0:
                b0 = '%02.0x' % ord(l[5][0])
            else:
                b0 = '  '
            if len(l[5]) > 1:
                b1 = '%02.0x' % ord(l[5][1])
            else:
                b1 = '  '
            if len(l[5]) > 2:
                b2 = '%02.0x' % ord(l[5][2])
            else:
                b2 = '  '
            if l[6] is None:
                code = ''
            else:
                code = l[6]
            s += '%s %s %s %s    %s    %s %s %s    %s\n' % (b[:1], sg[:2], cnt[:3],
                                                   addr[:4], lbl[:ll], b0[:2],
                                                   b1[:2], b2[:2], code)
        return s

    def get_current_pos(self):
        return self._ram_pos

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
        # the rom bank. save these for later...
        self._spare = inf.read(5)

    def _unpack_banks(self, inf):
        if self._version == 1:
            # load bank 0
            banksize = 256 * self._page_size_bank0
            b = Buffer(0, banksize)
            b.load(inf, banksize)
            self._banks.append(b)

            # load bank 1 if needed
            if self._page_size_bank1 > 0:
                banksize = 256 * self._page_size_bank1
                b = Buffer(0, banksize)
                b.load(inf, banksize)
                self._banks.append(b)

        elif self._version == 2:
            # load the bank 0 banks
            for i in range(0, self._num_banks):
                banksize = 256 * 2048
                b = Buffer(0, banksize)
                b.load(inf, banksize)
                self._banks.append(b)

            # load the bank 1 banks if needed
            if self._use_cart_strobe:
                for i in range(0, self._num_banks):
                    banksize = 256 * 2048
                    b = Buffer(0, banksize)
                    b.load(inf, banksize)
                    self._banks.append(b)

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
            outf.write(pack('<HH', self._page_size_bank0, self._page_size_bank1))
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
            outf.write(self._banks[0])

            # write out bank 1
            if self._page_size_bank1 > 0:
                outf.write(self._banks[1])

        elif self._version == 2:
            # write out all of the banks
            for i in range(0, len(self._banks)):
                outf.write(self._banks[i])

            # write out the save game data if any
            if self._save_game_size > 0:
                outf.write(self._save_game_data)

        else:
            raise SyntaxError(outf.name, 0, 64, 'cannot save banks, invalid .lnx version')

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

class bind1(object):

    def __init__(self, fn, type):
        self._fn = fn
        self._type = type

    def get_type(self):
        return self._type

    def __call__(self, pstring, location, tokens):
        return self._fn(pstring, location, tokens, self._type)

class LnxSetting(object):
    """
    This defines the rules for parsing a #lnx.* preprocessor settings
    """

    OFF, PSB0, PSB1, VERSION, CART_NAME, MANU_NAME, ROTATION = range(7)
    TYPE = [ 'off', 'page_size_bank0', 'page_size_bank1', 'version',
             'cart_name', 'manufacturer_name', 'rotation' ]
    KEYNAMES = [ None, 'size', 'size', 'version', 'cname', 'mname', 'rotation' ]

    @classmethod
    def get_numeric_parameter(klass, tokens, keyname):
        pp = Session().preprocessor() 
        if keyname not in tokens.keys():
            raise ParseFatalException('#lnx.* missing %s' % keyname)

        value = getattr(tokens, keyname)
        if not isinstance(value, NumericValue):
            if not pp.has_symbol(value):
                raise ParseFatalException('unknown preprocessor symbol: %s' % value)
            value = pp.get_symbol(value)

        return value

    @classmethod
    def get_string_parameter(klass, tokens, keyname):
        pp = Session().preprocessor() 
        if keyname not in tokens.keys():
            raise ParseFatalException('#lnx.* missing %s' % keyname)

        value = getattr(tokens, keyname)
        if not isinstance(value, StringValue):
            if not pp.has_symbol(value):
                raise ParseFatalException('unknown preprocessor symbol: %s' % value)
            value = pp.get_symbol(value)

        return value

    @classmethod
    def parse(klass, pstring, location, tokens, type_):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if type_ == klass.OFF:
            return klass(type_)
        
        elif type_ in (klass.PSB0, klass.PSB1, klass.VERSION):
            return klass(type_, klass.get_numeric_parameter(tokens, klass.KEYNAMES[type_]))

        elif type_ in (klass.CART_NAME, klass.MANU_NAME, klass.ROTATION):
            return klass(type_, klass.get_string_parameter(tokens, klass.KEYNAMES[type_]))

        raise ParseFatalException('invalid #lnx expression')

    @classmethod
    def exprs(klass):
        label = Word(alphas + '_', alphanums + '_')

        #lnx.off
        off = Suppress(Keyword('#lnx.off'))
        off.setParseAction(bind1(klass.parse, klass.OFF))

        #lnx.page_size_bank0 <value>
        psb0 = Suppress(Keyword('#lnx.page_size_bank0')) + \
               Or([label, NumericValue.exprs()]).setResultsName('size')
        psb0.setParseAction(bind1(klass.parse, klass.PSB0))

        #lnx.page_size_bank1 <value>
        psb1 = Suppress(Keyword('#lnx.page_size_bank1')) + \
               Or([label, NumericValue.exprs()]).setResultsName('size')
        psb1.setParseAction(bind1(klass.parse, klass.PSB1))

        #lnx.version <value>
        ver = Suppress(Keyword('#lnx.version')) + \
               Or([label, NumericValue.exprs()]).setResultsName('version')
        ver.setParseAction(bind1(klass.parse, klass.VERSION))

        #lnx.cart_name <string value>
        cname = Suppress(Keyword('#lnx.cart_name')) + \
               Or([label, StringValue.exprs()]).setResultsName('cname')
        cname.setParseAction(bind1(klass.parse, klass.CART_NAME))

        #lnx.manufacturer_name <string value>
        mname = Suppress(Keyword('#lnx.manufacturer_name')) + \
               Or([label, StringValue.exprs()]).setResultsName('mname')
        mname.setParseAction(bind1(klass.parse, klass.MANU_NAME))

        #lnx.rotation <string value>
        rot = Suppress(Keyword('#lnx.rotation')) + \
               Or([label, StringValue.exprs()]).setResultsName('rotation')
        rot.setParseAction(bind1(klass.parse, klass.ROTATION))

        expr = MatchFirst([off, psb0, psb1, ver, cname, mname, rot])

        return expr


    def __init__(self, type_, *args_):
        self._type = type_

        self._size = None
        self._version = None
        self._name = None
        self._rotation = None

        if type_ in (self.PSB0, self.PSB1):
            self._size = args_[0]
        elif type_ == self.VERSION:
            self._version = args_[0]
        elif type_ in (self.CART_NAME, self.MANU_NAME):
            self._name = args_[0]
        elif type_ == self.ROTATION:
            self._rotation = args_[0]

    def get_type(self):
        return self._type

    def get_size(self):
        return self._size

    def get_version(self):
        return self._version

    def get_name(self):
        return self._name

    def get_rotation(self):
        return self._rotation

    def __str__(self):
        s_ = '#lnx.%s' % self.TYPE[self._type]
        if self._size:
            s_ += ' %s' % self._size
        elif self._version:
            s_ += ' %s' % str(self._version)
        elif self._name:
            s_ += ' "%s"' % self._name
        elif self._rotation: 
            s_ += ' %s' % self._rotation
        return s_

    __repr__ = __str__


