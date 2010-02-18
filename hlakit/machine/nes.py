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
from ines import iNES

class NES(Machine):

    CPU = 'mos6502'
    def __init__(self, options = None, logger = None):

        # init the base class 
        super(NES, self).__init__()

        # store the options object
        self._options = options

        # store the logger
        self._logger = logger

        # initialize the preprocessor expressions list
        self._preprocessor_exprs = []

        # initialize the compiler expressions list
        self._compiler_exprs = []

        # create our iNES header
        self._ines = iNES()

        # iNES meta values
        self._prg_repeat = 0        # specified how many times to repeat prg block
        self._chr_repeat = 0        # specifies how many times to repeat chr block
        self._ines_off = False      # disables iNES header generation

        # build the expressions
        self._init_preprocessor_exprs()
        
    def get_cpu(self):
        return NES.CPU

    def get_preprocessor_exprs(self):
        return self._preprocessor_exprs

    def get_compiler_exprs(self):
        return self._compiler_exprs

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
        mapper = Keyword('#ines.mapper')
        mirroring = Keyword('#ines.mirroring')
        fourscreen = Keyword('#ines.fourscreen')
        battery = Keyword('#ines.battery')
        trainer = Keyword('#ines.trainer')
        prgrepeat = Keyword('#ines.prgrepeat')
        chrrepeat = Keyword('#ines.chrrepeat')
        off = Keyword('#ines.off')

        # unif (.rom) header preprocessor keywords

        # NES ram/rom/chr specific preprocessor keywords
        """
        ram_org = Keyword('#ram.org')
        ram_end = Keyword('#ram.end')
        rom_org = Keyword('#rom.org')
        rom_end = Keyword('#rom.end')
        rom_banksize = Keyword('#rom.banksize')
        rom_bank = Keyword('#rom.bank')
        chr_banksize = Keyword('#chr.banksize')
        chr_bank = Keyword('#chr.bank')
        chr_link = Keyword('#chr.link')
        """

        # NES specific tell preprocessor keywords
        """
        tell_bank = Keyword('#tell.bank')
        tell_bankoffset = Keyword('#tell.bankoffset')
        tell_banksize = Keyword('#tell.banksize')
        tell_bankfree = Keyword('#tell.bankfree')
        tell_banktype = Keyword('#tell.banktype')
        """
        
        # define value
        value = OneOrMore(~LineEnd() + Word(printables)).setResultsName('value')

        # mapper line
        mapper_line = Suppress(mapper) + \
                      value + \
                      Suppress(LineEnd())
        mapper_line.setParseAction(self._mapper_line)

        # mirroring line
        mirroring_line = Suppress(mirroring) + \
                         value + \
                         Suppress(LineEnd())
        mirroring_line.setParseAction(self._mirroring_line)

        # fourscreen line
        fourscreen_line = Suppress(fourscreen) + \
                          value + \
                          Suppress(LineEnd())
        fourscreen_line.setParseAction(self._fourscreen_line)

        # battery line
        battery_line = Suppress(battery) + \
                       value + \
                       Suppress(LineEnd())
        battery_line.setParseAction(self._battery_line)

        # trainer line
        trainer_line = Suppress(trainer) + \
                       value + \
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

    def _convert_bool_argument(self, token):
        # try to convert the token to int, otherwise
        # it is a string...
        try:
            value = int(token)
            if value == 0:
                value = False
            elif value == 1:
                value = True
        except:
            # unquote and convert to upper case 
            value = token.strip('"\'').upper()
            if value == 'Y' or value == 'YES':
                value = True
            elif value == 'N' or value == 'NO':
                value = False
            else:
                raise ParseFatalException ('argument must be "yes", "no", 0, or 1')

        return value
 

    #
    # Parse Action Callbacks
    #

    def _mapper_line(self, pstring, location, tokens):
        if len(tokens.value) != 1:
            raise ParseFatalException ('#ines.mapper must have exactly 1 argument')

        # try to convert the mapper value to int, otherwise
        # it is a string...
        try:
            value = int(tokens.value[0])
        except:
            value = tokens.value[0].strip('"\'')

        # store the mapper value
        self._ines.set_mapper(value)
        
        return []

    def _mirroring_line(self, pstring, location, tokens):
        if len(tokens.value) != 1:
            raise ParseFatalException ('#ines.mirroring must have exactly 1 argument')

        # try to convert the mirroring value to int, otherwise
        # it is a string...
        try:
            value = int(tokens.value[0])
        except:
            value = tokens.value[0].strip('"\'').upper()
            if value == "V":
                value = "VERTICAL"
            elif value == "H":
                value = "HORIZONTAL"

        # store the mirroring
        self._ines.set_mirroring(value)

        return []

    def _fourscreen_line(self, pstring, location, tokens):
        if len(tokens.value) != 1:
            raise ParseFatalException ('#ines.fourscreen must have exactly 1 argument')

        # convert the argument
        value = self._convert_bool_argument(tokens.value[0])

        # store the four screen
        self._ines.set_four_screen(value)

        return []

    def _battery_line(self, pstring, location, tokens):
        if len(tokens.value) != 1:
            raise ParseFatalException ('#ines.battery must have exactly 1 argument')

        # convert the argument
        value = self._convert_bool_argument(tokens.value[0])

        # store the battery/sram
        self._ines.set_sram(value)

        return []

    def _trainer_line(self, pstring, location, tokens):
        if len(tokens.value) != 1:
            raise ParseFatalException ('#ines.trainer must have exactly 1 argument')

        # convert the argument
        value = self._convert_bool_argument(tokens.value[0])

        # store the battery/sram
        self._ines.set_trainer(value)

        return []

    def _prgrepeat_line(self, pstring, location, tokens):
        if len(tokens.value) != 1:
            raise ParseFatalException ('#ines.prgrepeat must have exactly 1 argument')

        try:
            value = int(tokens.value[0])
        except:
            raise ParseFatalException('#ines.prgrepeat must have integer argument')

        # store the prg repeat
        self._prg_repeat = value

        return []

    def _chrrepeat_line(self, pstring, location, tokens):
        if len(tokens.value) != 1:
            raise ParseFatalException ('#ines.chrrepeat must have exactly 1 argument')

        try:
            value = int(tokens.value[0])
        except:
            raise ParseFatalException('#ines.chrrepeat must have integer argument')

        # store the chr repeat
        self._chr_repeat = value

        return []

    def _off_line(self, pstring, location, tokens):
        
        # store the ines off
        self._ines_off = True

        return []


