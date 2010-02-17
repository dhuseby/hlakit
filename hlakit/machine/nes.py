"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

import os
from pyparsing import *
from machine import Machine

class NES(Machine):

    CPU = 'mos6502'
    MAPPERS = {
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

    def __init__(self, options = None, logger = None):

        # init the base class 
        super(NES, self).__init__()

        # store the options object
        self._options = options

        # store the logger
        self._logger = logger

        # initialize the expressions lists
        self._preprocessor_exprs = []

        # build the expressions
        self._init_preprocessor_exprs()
        
    def get_cpu(self):
        return NES.CPU

    def get_preprocessor_exprs(self):
        return self._preprocessor_exprs

    def get_compiler_exprs(self):
        return None

    def get_file_writer(self):
        # the file writer is the platform specific binary
        # creator.  for the NES, it writes out a NES ROM
        # in either iNES (.nes) or UNIF (.rom) format depending
        # on the preprocessor directives.  The default is to
        # output an iNES file.
        return None

    def _init_preprocessor_exprs(self):
        # define the NES specific preprocessor keywords

        # ines (.nes) header preprocessor keywords
        mapper = Keyword('#nes.ines.mapper')
        mirroring = Keyword('#nes.ines.mirroring')
        fourscreen = Keyword('#nes.ines.fourscreen')
        battery = Keyword('#nes.ines.battery')
        trainer = Keyword('#nes.ines.trainer')
        prgrepeat = Keyword('#nes.ines.prgrepeat')
        chrrepeat = Keyword('#nes.ines.chrrepeat')
        off = Keyword('#nes.ines.off')

        # unif (.rom) header preprocessor keywords

        # NES ram/rom/chr specific preprocessor keywords
        """
        ram_org = Keyword('#nes.ram.org')
        ram_end = Keyword('#nes.ram.end')
        rom_org = Keyword('#nes.rom.org')
        rom_end = Keyword('#nes.rom.end')
        rom_banksize = Keyword('#nes.rom.banksize')
        rom_bank = Keyword('#nes.rom.bank')
        chr_banksize = Keyword('#nes.chr.banksize')
        chr_bank = Keyword('#nes.chr.bank')
        chr_link = Keyword('#nes.chr.link')
        """

        # NES specific tell preprocessor keywords
        """
        tell_bank = Keyword('#nes.tell.bank')
        tell_bankoffset = Keyword('#nes.tell.bankoffset')
        tell_banksize = Keyword('#nes.tell.banksize')
        tell_bankfree = Keyword('#nes.tell.bankfree')
        tell_banktype = Keyword('#nes.tell.banktype')
        """
        
        # define value
        value = OneOrMore(~LineEnd() + Word(printables)).setResultsName('value')

        # define yesno
        yesno = Or(Keyword('yes'), Keyword('no')).setResultsName('value')

        # define horzvert
        horzvert = Or(Keyword('horizontal'), Keyword('vertical')).setResultsName('value')

        # mapper line
        mapper_line = Suppress(mapper) + \
                      value + \
                      Suppress(LineEnd())
        mapper_line.setParseAction(self._mapper_line)

        # mirroring line
        mirroring_line = Suppress(mirroring) + \
                         horzvert + \
                         Suppress(LineEnd())
        mirroring_line.setParseAction(self._mirroring_line)

        # fourscreen line
        fourscreen_line = Suppress(fourscreen) + \
                          yesno + \
                          Suppress(LineEnd())
        fourscreen_line.setParseAction(self._fourscreen_line)

        # battery line
        battery_line = Suppress(battery) + \
                       yesno + \
                       Suppress(LineEnd())
        battery_line.setParseAction(self._battery_line)

        # trainer line
        trainer_line = Suppress(trainer) + \
                       yesno + \
                       Suppress(LineEnd())
        trainer_line.setParseAction(self._trainer_line)

        # prgrepeat line
        prgrepeat_line = Suppress(prgrepeat) + \
                         Word(nums).setResultsName('value') + \
                         Suppress(LineEnd())
        prgrepeat_line.setParseAction(self._prgrepeat_line)

        # chrrepeat line
        chrrepeat_line = Suppress(chrrepeat) + \
                         Word(nums).setResultsName('value') + \
                         Suppress(LineEnd())
        chrrepeat_line.setParseAction(self._chrrepeat_line)

        # off line
        off_line = Suppress(off) + \
                   Suppress(LineEnd())
        off_line.setParseAction(self._off_line)

        # put the expressions in the top level map
        self._preprocessor_exprs.append(('mapper_line', mapper_line))
        self._preprocessor_exprs.append(('mirroring_line', mirroring_line))
        self._preprocessor_exprs.append(('fourscreen_line', fourscreen_line))
        self._preprocessor_exprs.append(('battery_line', battery_line))
        self._preprocessor_exprs.append(('trainer_line', trainer_line))
        self._preprocessor_exprs.append(('prgrepeat_line', prgrepeat_line))
        self._preprocessor_exprs.append(('chrrepeat_line', chrrepeat_line))
        self._preprocessor_exprs.append(('off_line', off_line))

    def _get_mapper_number(self, mapper_name):
        return NES.MAPPERS[mapper_name]

    #
    # Parse Action Callbacks
    #

    def _mapper_line(self, pstring, location, tokens):
        return []

    def _mirroring_line(self, pstring, location, tokens):
        return []

    def _fourscreen_line(self, pstring, location, tokens):
        return []

    def _battery_line(self, pstring, location, tokens):
        return []

    def _trainer_line(self, pstring, location, tokens):
        return []

    def _prgrepeat_line(self, pstring, location, tokens):
        return []

    def _chrrepeat_line(self, pstring, location, tokens):
        return []

    def _off_line(self, pstring, location, tokens):
        return []


