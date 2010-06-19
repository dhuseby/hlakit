"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

from pyparsing import *
from hlakit.common.session import Session
from hlakit.common.numericvalue import NumericValue

class iNES(object):
    """
    This class encapsulates the iNES header that will be written with
    the ROM image.
    """

    # mirroring
    MIRRORING = { 
        'HORIZONTAL': 0,
        'VERTICAL': 1
    }

    # ROM type
    ROM_TYPE = {
        'NES': 0,
        'VS_UNISYSTEM': 1,
        'PLAYCHOICE': 2
    }

    # Options
    OPTIONS = {
        'NTSC': 0,
        'PAL': 1,
        'EXTRA_RAM': 4,         # extra RAM at $6000-$7FFF
        'NO_BUS_CONFLICTS': 5   # ??
    }

    # all known NES mappers
    MAPPERS = {
        'none':                                             0,
        'NONE':                                             0,
        'ROM':                                              0,
        'NES-NROM':                                         0,
        'MMC1':                                             1,
        'S*ROM':                                            1,
        'SAROM':                                            1,
        'SBROM':                                            1,
        'SCROM':                                            1,
        'SEROM':                                            1,
        'SGROM':                                            1,
        'SKROM':                                            1,
        'SLROM':                                            1,
        'SL1ROM':                                           1,
        'SNROM':                                            1,
        'SOROM':                                            1,
        'NES-MMC1':                                         1,
        'NES-S*ROM':                                        1,
        'NES-SAROM':                                        1,
        'NES-SBROM':                                        1,
        'NES-SCROM':                                        1,
        'NES-SEROM':                                        1,
        'NES-SGROM':                                        1,
        'NES-SKROM':                                        1,
        'NES-SLROM':                                        1,
        'NES-SL1ROM':                                       1,
        'NES-SNROM':                                        1,
        'NES-SOROM':                                        1,
        'U*ROM':                                            2,
        'UNROM':                                            2,
        'UOROM':                                            2,
        'NES-U*ROM':                                        2,
        'NES-UNROM':                                        2,
        'NES-UOROM':                                        2,
        'CNROM':                                            3,
        'NES-CNROM':                                        3,
        'MMC3':                                             4,
        'MMC6':                                             4,
        'T*ROM':                                            4,
        'TFROM':                                            4,
        'TGROM':                                            4,
        'TKROM':                                            4,
        'TLROM':                                            4,
        'TR1ROM':                                           4,
        'TSROM':                                            4,
        'NES-B4':                                           4,
        'H*ROM':                                            4,
        'HKROM':                                            4,
        'NES-MMC3':                                         4,
        'NES-MMC6':                                         4,
        'NES-T*ROM':                                        4,
        'NES-TFROM':                                        4,
        'NES-TGROM':                                        4,
        'NES-TKROM':                                        4,
        'NES-TLROM':                                        4,
        'NES-TR1ROM':                                       4,
        'NES-TSROM':                                        4,
        'NES-NES-B4':                                       4,
        'NES-H*ROM':                                        4,
        'NES-HKROM':                                        4,
        'MMC5':                                             5,
        'E*ROM':                                            5,
        'EKROM':                                            5,
        'ELROM':                                            5,
        'ETROM':                                            5,
        'EWROM':                                            5,
        'NES-MMC5':                                         5,
        'NES-E*ROM':                                        5,
        'NES-EKROM':                                        5,
        'NES-ELROM':                                        5,
        'NES-ETROM':                                        5,
        'NES-EWROM':                                        5,
        'FFE F4':                                           6,
        'A*ROM':                                            7,
        'AMROM':                                            7,
        'ANROM':                                            7,
        'AOROM':                                            7,
        'NES-A*ROM':                                        7,
        'NES-AMROM':                                        7,
        'NES-ANROM':                                        7,
        'NES-AOROM':                                        7,
        'FFE F3':                                           8,
        'MMC2':                                             9,
        'P*ROM':                                            9,
        'PNROM':                                            9,
        'PEEOROM':                                          9,
        'NES-MMC2':                                         9,
        'NES-P*ROM':                                        9,
        'NES-PNROM':                                        9,
        'NES-PEEOROM':                                      9,
        'MMC4':                                             10,
        'NES-MMC4':                                         10,
        'Color Dreams':                                     11,
        'CPROM':                                            13,
        '100-in-1 Contra Function 16':                      15,
        'Bandai':                                           16,
        'FFE F8':                                           17,
        'Jaleco SS8806':                                    18,
        'Namcot 106':                                       19,
        'Konami VRC4':                                      21,
        'VRC4':                                             21,
        'Konami VRC2 Type A':                               22,
        'Konami VRC2 A':                                    22,
        'VRC2 A':                                           22,
        'Konami VRC2 Type B':                               23,
        'Konami VRC2 B':                                    23,
        'VRC2 B':                                           23,
        'Konami VRC6 A1/A0':                                24,
        'VRC6 A1/A0':                                       24,
        'Konami VRC4 Type Y':                               25,
        'Konami VRC4 Y':                                    25,
        'VRC4 Y':                                           25,
        'Irem G-101':                                       32,
        'Taito TC0190':                                     33,
        'TC0190':                                           33,
        'BNROM':                                            34,
        'NES-BNROM':                                        34,
        'Nina-01':                                          34,
        'SMB2j Pirate':                                     40,
        'Caltron 6-in-1':                                   41,
        'Mario Baby':                                       42,
        'SMB2j (LF36)':                                     43,
        'Super HiK 7 in 1 (MMC3)':                          44,
        'Super 1,000,000 in 1 (MMC3)':                      45,
        'GameStation/RumbleStation':                        46,
        'Super Spike & Nintendo World Cup Soccer (MMC3)':   47,
        'Super Spike/World Cup':                            47,
        '1993 Super HiK 4-in-1 (MMC3)':                     49,
        'SMB2j rev. A':                                     50,
        '11 in 1 Ball Games':                               51,
        'Mario 7 in 1 (MMC3)':                              52,
        'SMB3 Pirate':                                      56,
        'Study & Game 32 in 1':                             58,
        'T3H53':                                            59,
        'T3H53':                                            59,
        '20-in-1':                                          61,
        '700-in-1':                                         62,
        'Hello Kitty 255 in 1':                             63,
        'Tengen RAMBO-1':                                   64,
        'RAMBO-1':                                          64,
        'Irem H-3001':                                      65,
        'GNROM':                                            66,
        'NES-GNROM':                                        66,
        'Sunsoft Mapper  #3':                               67,
        'Sunsoft 3':                                        67,
        'Sunsoft Mapper #4':                                68,
        'Sunsoft 4':                                        68,
        'Sunsoft FME-07':                                   69,
        'FME-07':                                           69,
        'Camerica (partial)':                               71,
        'Konami VRC3':                                      73,
        'VRC3':                                             73,
        'Konami VRC1':                                      75,
        'VRC1':                                             75,
        'Irem 74161/32':                                    78,
        'NINA-03':                                          79,
        'NINA-06':                                          79,
        'Cony':                                             83,
        'Konami VRC7':                                      85,
        'VRC7':                                             85,
        'Copyright':                                        90,
        'Mapper 90':                                        90,
        'Super Mario World':                                90,
        'PC-HK-SF3':                                        91,
        'Dragon Buster (MMC3 variant)':                     95,
        'Dragon Buster':                                    95,
        'Kid Niki (J)':                                     97,
        'VS Unisystem':                                     99,
        'Nintendo VS Unisystem':                            99,
        'Debugging Mapper':                                 100,
        'Nintendo World Championship':                      105,
        'HES-Mapper #113':                                  113,
        'TKSROM':                                           118,
        'TLSROM':                                           118,
        'NES-TKSROM':                                       118,
        'NES-TLSROM':                                       118,
        'TQROM':                                            119,
        'NES-TQROM':                                        119,
        'Sachen Mapper 141':                                141,
        'SMB2j Pirate (KS 202)':                            142,
        'KS 202':                                           142,
        'Sachen Copy Protection':                           143,
        'AGCI':                                             144,
        'Extended VS Unisystem':                            151,
        'Nintendo VS Unisystem (Extended)':                 151,
        'Super Donkey Kong':                                182,
        '72-in-1':                                          225,
        '76-in-1':                                          226,
        '1200-in-1':                                        227,
        'Action 52':                                        228,
        '31-in-1':                                          229,
        'Camerica 9096':                                    232,
        'Maxi 15':                                          234,
        'Golden Game 150-in-1':                             235,
        'Sachen 74LS374N':                                  243
    }

    def __init__(self):
        self._extended_format = False       # extended format?
        self._magic = "\x4E\x45\x53\x1A"    # NES + char break
        self._prg = 0                       # 16K PRG-ROM page count
        self._chr = 0                       # 8K CHR-ROM page count
        self._mirroring = iNES.MIRRORING['HORIZONTAL'] # mirroring value
        self._sram = False                  # SRAM enabled
        self._trainer = False               # 512-byte trainer present
        self._four_screen = False           # Four-screen VRAM layout
        self._mapper = 0                    # mapper number
        self._rom_type = iNES.ROM_TYPE['NES'] # ROM type
        self._options = iNES.OPTIONS['NTSC']# Options

    def __str__(self):
        """
        +--------+------+------------------------------------------+
        | byte   | size | description                              |
        +--------+------+------------------------------------------+
        |   0    |  3   | 'NES'                                    |
        |   3    |  1   | $1A                                      |
        |   4    |  1   | 16K PRG-ROM page count                   |
        |   5    |  1   | 8K CHR-ROM page count                    |
        |   6    |  1   | ROM Control Byte #1                      |
        |        |      |   %####vTsM                              |
        |        |      |    |  ||||+- 0=Horizontal Mirroring      |
        |        |      |    |  ||||   1=Vertical Mirroring        |
        |        |      |    |  |||+-- 1=SRAM enabled              |
        |        |      |    |  ||+--- 1=512-byte trainer present  |
        |        |      |    |  |+---- 1=Four-screen VRAM layout   |
        |        |      |    |  |                                  |
        |        |      |    +--+----- Mapper # (lower 4-bits)     |
        |   7    |  1   | ROM Control Byte #2                      |
        |        |      |   %####0000                              |
        |        |      |    |  |                                  |
        |        |      |    +--+----- Mapper # (upper 4-bits)     |
        |  7     |  1   | 01=00-> nes rom                          |
        |  7     |  1   | 01=01-> vs unisystem rom                 |
        |  7     |  1   | 01=02-> playchoice rom                   |
        |  8     |  1   | $00                                      |
        |  9     |  1   | $00                                      |
        |  10    |  1   | 0=0->"100% compatible with NTSC console" |
        |  10    |  1   | 1=0->"Not necessarily 100% compatible    |
        |        |      |       with PAL console""                 |
        |  10    |  1   | 4=0->"extra ram at $6000-$7fff           |
        |  10    |  1   | 5=0->"don't have bus conflicts           |
        |  11    |  6   | $00                                      |
        +--------+------+------------------------------------------+
        """

        # TODO: output the binary string representing the header
        pass

    def set_prg_count(self, prg):
        self._prg = prg

    def set_chr_count(self, chr):
        self._chr = chr

    def set_mirroring(self, mirroring):
        if type(mirroring) == str:
            if iNES.MIRRORING.has_key(mirroring):
                self._mirroring = iNES.MIRRORING[mirroring]
        elif type(mirroring) == int:
            if mirroring in iNES.MIRRORING.values():
                self._mirroring = mirroring

    def set_sram(self, sram):
        self._sram = sram

    def set_trainer(self, trainer):
        self._trainer = trainer

    def set_four_screen(self, four_screen):
        self._four_screen = four_screen

    def set_mapper(self, mapper):
        if type(mapper) == str:
            if iNES.MAPPERS.has_key(mapper):
                self._mapper = iNES.MAPPERS[mapper]
        elif type(mapper) == int:
            if mapper in iNES.MAPPERS.values():
                self._mapper = mapper

    def set_rom_type(self, rom_type):
        if iNES.ROM_TYPE.has_key(rom_type):
            self._rom_type = iNES.ROM_TYPE[rom_type]

    def set_option(self, option):
        if iNES.OPTIONS.has_key(option):
            self._options = iNES.OPTIONS[option]


class iNESMapper(object):
    """
    This defines the rules for parsing a #ines.mapper "name"|number line 
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        mapper = getattr(tokens, 'name', None)
        if not mapper:
            mapper = getattr(tokens, 'number', None)
        if not mapper:
            raise ParseFatalException('#ines.mapper missing parameter')

        return klass(mapper)

    @classmethod
    def exprs(klass):
        kw = Keyword('#ines.mapper')
        name = quotedString(OneOrMore(Word(printables)))
        name.setParseAction(removeQuotes)
        name = name.setResultsName('name')
        number = NumericValue.exprs().setResultsName('number')

        expr = Suppress(kw) + \
               Or([name, number]) + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, mapper):
        self._mapper = mapper

    def get_mapper(self):
        return self._mapper

    def __str__(self):
        return 'iNESMapper %s' % self._mapper

    __repr__ = __str__


class iNESMirroring(object):
    """
    This defines the rules for parsing a #ines.mirroring "vertical"|"horizontal" line 
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'mirroring' not in tokens.keys():
            raise ParseFatalException('#ines.mirroring missing parameter')

        if tokens.mirroring == 'vertical' or \
           tokens.mirroring == 'horizontal':
            return klass(tokens.mirroring)

        raise ParseFatalException('#ines.mirroring invalid parameter')

    @classmethod
    def exprs(klass):
        kw = Keyword('#ines.mirroring')
        mirroring = quotedString(Or([Keyword('vertical'), Keyword('horizontal')]))
        mirroring.setParseAction(removeQuotes)
        mirroring = mirroring.setResultsName('mirroring')

        expr = Suppress(kw) + \
               mirroring + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, mirroring):
        self._mirroring = mirroring

    def get_mirroring(self):
        return self._mirroring

    def __str__(self):
        return 'iNESMirroring %s' % self._mirroring

    __repr__ = __str__


class iNESFourscreen(object):
    """
    This defines the rules for parsing a #ines.fourscreen "yes"|"no" line 
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'value' not in tokens.keys():
            raise ParseFatalException('#ines.fourscreen missing parameter')

        if tokens.value == 'yes' or \
           tokens.value == 'no':
            return klass(tokens.value)

        raise ParseFatalException('#ines.fourscreen invalid parameter')

    @classmethod
    def exprs(klass):
        kw = Keyword('#ines.fourscreen')
        value = quotedString(Or([Keyword('yes'), Keyword('no')]))
        value.setParseAction(removeQuotes)
        value = value.setResultsName('value')

        expr = Suppress(kw) + \
               value + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, value):
        self._value = value

    def get_fourscreen(self):
        return self._value

    def __str__(self):
        return 'iNESFourscreen %s' % self._value

    __repr__ = __str__


class iNESBattery(object):
    """
    This defines the rules for parsing a #ines.battery "yes"|"no" line 
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'value' not in tokens.keys():
            raise ParseFatalException('#ines.battery missing parameter')

        if tokens.value == 'yes' or \
           tokens.value == 'no':
            return klass(tokens.value)

        raise ParseFatalException('#ines.battery invalid parameter')

    @classmethod
    def exprs(klass):
        kw = Keyword('#ines.battery')
        value = quotedString(Or([Keyword('yes'), Keyword('no')]))
        value.setParseAction(removeQuotes)
        value = value.setResultsName('value')

        expr = Suppress(kw) + \
               value + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, value):
        self._value = value

    def get_battery(self):
        return self._value

    def __str__(self):
        return 'iNESBattery %s' % self._value

    __repr__ = __str__


class iNESTrainer(object):
    """
    This defines the rules for parsing a #ines.trainer "yes"|"no" line 
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'value' not in tokens.keys():
            raise ParseFatalException('#ines.trainer missing parameter')

        if tokens.value == 'yes' or \
           tokens.value == 'no':
            return klass(tokens.value)

        raise ParseFatalException('#ines.trainer invalid parameter')

    @classmethod
    def exprs(klass):
        kw = Keyword('#ines.trainer')
        value = quotedString(Or([Keyword('yes'), Keyword('no')]))
        value.setParseAction(removeQuotes)
        value = value.setResultsName('value')

        expr = Suppress(kw) + \
               value + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, value):
        self._value = value

    def get_trainer(self):
        return self._value

    def __str__(self):
        return 'iNESTrainer %s' % self._value

    __repr__ = __str__


class iNESPrgRepeat(object):
    """
    This defines the rules for parsing a #ines.prgrepeat <number> line 
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'repeat' not in tokens.keys():
            raise ParseFatalException('#ines.prgrepeat missing parameter')

        return klass(tokens.repeat)

    @classmethod
    def exprs(klass):
        kw = Keyword('#ines.prgrepeat')
        repeat = NumericValue.exprs().setResultsName('repeat')

        expr = Suppress(kw) + \
               repeat + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, repeat):
        self._repeat = repeat

    def get_repeat(self):
        return self._repeat

    def __str__(self):
        return 'iNESPrgRepeat %s' % self._repeat

    __repr__ = __str__


class iNESChrRepeat(object):
    """
    This defines the rules for parsing a #ines.chrrepeat <number> line 
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'repeat' not in tokens.keys():
            raise ParseFatalException('#ines.chrrepeat missing parameter')

        return klass(tokens.repeat)

    @classmethod
    def exprs(klass):
        kw = Keyword('#ines.chrrepeat')
        repeat = NumericValue.exprs().setResultsName('repeat')

        expr = Suppress(kw) + \
               repeat + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, repeat):
        self._repeat = repeat

    def get_repeat(self):
        return self._repeat

    def __str__(self):
        return 'iNESChrRepeat %s' % self._repeat

    __repr__ = __str__


class iNESOff(object):
    """
    This defines the rules for parsing a #ines.off line 
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        return klass()

    @classmethod
    def exprs(klass):
        kw = Keyword('#ines.off')

        expr = Suppress(kw) + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __str__(self):
        return 'iNESOff'

    __repr__ = __str__


