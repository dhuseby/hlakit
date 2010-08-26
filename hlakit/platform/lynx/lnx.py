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

class Lnx(object):
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
        # the rom bank. save these for later...
        self._spare = inf.read(5)

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
        s = '#lnx.%s' % self.TYPE[self._type]
        if self._size:
            s += ' %s' % self._size
        elif self._version:
            s += ' %s' % self._version
        elif self._name:
            s += ' %s' % self._name
        elif self._rotation: 
            s += ' %s' % self._rotation
        return s

    __repr__ = __str__



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


