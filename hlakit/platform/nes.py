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
from platform import Platform
from ines import iNES
from hlakit.preprocessor import Preprocessor
from hlakit.number import Number
from tokens import *

class NES(Platform):

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

        # NES ram specific preprocessor keywords
        ram_org = Keyword('#ram.org')
        ram_end = Keyword('#ram.end')
        
        # NES rom specific preprocessor keywords
        rom_org = Keyword('#rom.org')
        rom_end = Keyword('#rom.end')
        rom_banksize = Keyword('#rom.banksize')
        rom_bank = Keyword('#rom.bank')

        # NES chr specific preprocessor keywords
        chr_banksize = Keyword('#chr.banksize')
        chr_bank = Keyword('#chr.bank')
        chr_link = Keyword('#chr.link')

        # NES specific tell preprocessor keywords
        tell_bank = Keyword('#tell.bank')
        tell_bankoffset = Keyword('#tell.bankoffset')
        tell_banksize = Keyword('#tell.banksize')
        tell_bankfree = Keyword('#tell.bankfree')
        tell_banktype = Keyword('#tell.banktype')
        
        # value
        label = Word(alphas + '_', alphanums + '_').setResultsName('label')
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

        # ram org line
        ram_org_line = Suppress(ram_org) + \
                       Number.exprs().setResultsName('value') + \
                       Suppress(LineEnd())
        ram_org_line.setParseAction(self._ram_org_line)
        ram_org_line_with_size = Suppress(ram_org) + \
                       Number.exprs().setResultsName('value') + \
                       Suppress(',') + \
                       Number.exprs().setResultsName('maxsize') + \
                       Suppress(LineEnd())
        ram_org_line_with_size.setParseAction(self._ram_org_line)

        # ram end line
        ram_end_line = Suppress(ram_end) + \
                       Suppress(LineEnd())
        ram_end_line.setParseAction(self._ram_end_line)

        # rom org line
        rom_org_line = Suppress(rom_org) + \
                       Number.exprs().setResultsName('value') + \
                       Suppress(LineEnd())
        rom_org_line.setParseAction(self._rom_org_line)
        rom_org_line_with_size = Suppress(rom_org) + \
                       Number.exprs().setResultsName('value') + \
                       Suppress(',') + \
                       Number.exprs().setResultsName('maxsize') + \
                       Suppress(LineEnd())
        rom_org_line_with_size.setParseAction(self._rom_org_line)

        # ram end line
        rom_end_line = Suppress(rom_end) + \
                       Suppress(LineEnd())
        rom_end_line.setParseAction(self._rom_end_line)

        # rom banksize line
        rom_banksize_line = Suppress(rom_banksize) + \
                            Number.exprs().setResultsName('size') + \
                            Suppress(LineEnd())
        rom_banksize_line.setParseAction(self._rom_banksize_line)

        # rom bank line
        rom_bank_line = Suppress(rom_bank) + \
                        Number.exprs().setResultsName('number') + \
                        Suppress(LineEnd())
        rom_bank_line.setParseAction(self._rom_bank_line)
        rom_bank_line_with_size = Suppress(rom_bank) + \
                                  Number.exprs().setResultsName('number') + \
                                  Suppress(',') + \
                                  Number.exprs().setResultsName('maxsize') + \
                                  Suppress(LineEnd())
        rom_bank_line_with_size.setParseAction(self._rom_bank_line)
        rom_bank_line_label = Suppress(rom_bank) + \
                        label + \
                        Suppress(LineEnd())
        rom_bank_line_label.setParseAction(self._rom_bank_line)
        rom_bank_line_label_with_size = Suppress(rom_bank) + \
                                  label + \
                                  Suppress(',') + \
                                  Number.exprs().setResultsName('maxsize') + \
                                  Suppress(LineEnd())
        rom_bank_line_label_with_size.setParseAction(self._rom_bank_line)

        # chr banksize line
        chr_banksize_line = Suppress(chr_banksize) + \
                            Number.exprs().setResultsName('size') + \
                            Suppress(LineEnd())
        chr_banksize_line.setParseAction(self._chr_banksize_line)

        # chr bank line
        chr_bank_line = Suppress(chr_bank) + \
                        Number.exprs().setResultsName('number') + \
                        Suppress(LineEnd())
        chr_bank_line.setParseAction(self._chr_bank_line)
        chr_bank_line_with_size = Suppress(chr_bank) + \
                                  Number.exprs().setResultsName('number') + \
                                  Suppress(',') + \
                                  Number.exprs().setResultsName('maxsize') + \
                                  Suppress(LineEnd())
        chr_bank_line_with_size.setParseAction(self._chr_bank_line)
        chr_bank_line_label = Suppress(chr_bank) + \
                        label + \
                        Suppress(LineEnd())
        chr_bank_line_label.setParseAction(self._chr_bank_line)
        chr_bank_line_label_with_size = Suppress(chr_bank) + \
                                  label + \
                                  Suppress(',') + \
                                  Number.exprs().setResultsName('maxsize') + \
                                  Suppress(LineEnd())
        chr_bank_line_label_with_size.setParseAction(self._chr_bank_line)

        # chr link line
        literal_file_path = quotedString(Word(Preprocessor.FILE_NAME_CHARS))
        literal_file_path.setParseAction(removeQuotes)
        literal_file_path = literal_file_path.setResultsName('file_path')
        chr_link_line = Suppress(chr_link) + \
                        literal_file_path + \
                        Suppress(LineEnd())
        chr_link_line.setParseAction(self._chr_link_line)
        chr_link_line_with_size = Suppress(chr_link) + \
                        literal_file_path + \
                        Suppress(',') + \
                        Number.exprs().setResultsName('size') + \
                        Suppress(LineEnd())
        chr_link_line_with_size.setParseAction(self._chr_link_line)

        # tell bank
        tell_bank_line = Suppress(tell_bank) + Suppress(LineEnd())
        tell_bank_line.setParseAction(self._tell_bank_line)

        # tell bank offset
        tell_bankoffset_line = Suppress(tell_bankoffset) + Suppress(LineEnd())
        tell_bankoffset_line.setParseAction(self._tell_bankoffset_line)

        # tell bank size
        tell_banksize_line = Suppress(tell_banksize) + Suppress(LineEnd())
        tell_banksize_line.setParseAction(self._tell_banksize_line)

        # tell bank free
        tell_bankfree_line = Suppress(tell_bankfree) + Suppress(LineEnd())
        tell_bankfree_line.setParseAction(self._tell_bankfree_line)

        # tell bank type
        tell_banktype_line = Suppress(tell_banktype) + Suppress(LineEnd())
        tell_banktype_line.setParseAction(self._tell_banktype_line)

        # put the expressions in the top level map
        self._preprocessor_exprs.append(('mapper_line', mapper_line))
        self._preprocessor_exprs.append(('mirroring_line', mirroring_line))
        self._preprocessor_exprs.append(('fourscreen_line', fourscreen_line))
        self._preprocessor_exprs.append(('battery_line', battery_line))
        self._preprocessor_exprs.append(('trainer_line', trainer_line))
        self._preprocessor_exprs.append(('prgrepeat_line', prgrepeat_line))
        self._preprocessor_exprs.append(('chrrepeat_line', chrrepeat_line))
        self._preprocessor_exprs.append(('off_line', off_line))
        self._preprocessor_exprs.append(('ram_org_line', ram_org_line))
        self._preprocessor_exprs.append(('ram_org_line_with_size', ram_org_line_with_size))
        self._preprocessor_exprs.append(('ram_end_line', ram_end_line))
        self._preprocessor_exprs.append(('rom_org_line', rom_org_line))
        self._preprocessor_exprs.append(('rom_org_line_with_size', rom_org_line_with_size))
        self._preprocessor_exprs.append(('rom_end_line', rom_end_line))
        self._preprocessor_exprs.append(('rom_banksize_line', rom_banksize_line))
        self._preprocessor_exprs.append(('rom_bank_line', rom_bank_line))
        self._preprocessor_exprs.append(('rom_bank_line_with_size', rom_bank_line_with_size))
        self._preprocessor_exprs.append(('rom_bank_line_label', rom_bank_line_label))
        self._preprocessor_exprs.append(('rom_bank_line_label_with_size', rom_bank_line_label_with_size))
        self._preprocessor_exprs.append(('chr_banksize_line', chr_banksize_line))
        self._preprocessor_exprs.append(('chr_bank_line', chr_bank_line))
        self._preprocessor_exprs.append(('chr_bank_line_with_size', chr_bank_line_with_size))
        self._preprocessor_exprs.append(('chr_bank_line_label', chr_bank_line_label))
        self._preprocessor_exprs.append(('chr_bank_line_label_with_size', chr_bank_line_label_with_size))
        self._preprocessor_exprs.append(('chr_link_line', chr_link_line))
        self._preprocessor_exprs.append(('chr_link_line_with_size', chr_link_line_with_size))
        self._preprocessor_exprs.append(('tell_bank_line', tell_bank_line))
        self._preprocessor_exprs.append(('tell_bankoffset_line', tell_bankoffset_line))
        self._preprocessor_exprs.append(('tell_banksize_line', tell_banksize_line))
        self._preprocessor_exprs.append(('tell_bankfree_line', tell_bankfree_line))
        self._preprocessor_exprs.append(('tell_banktype_line', tell_banktype_line))

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

    def _ram_org_line(self, pstring, location, tokens):

        if 'maxsize' in tokens.keys():
            return MemOrg(Memory.RAM, tokens.value, tokens.maxsize)

        return MemOrg(Memory.RAM, tokens.value)

    def _ram_end_line(self, pstring, location, tokens):
        return MemEnd(Memory.RAM)

    def _rom_org_line(self, pstring, location, tokens):

        if 'maxsize' in tokens.keys():
            return MemOrg(Memory.ROM, tokens.value, tokens.maxsize)

        return MemOrg(Memory.ROM, tokens.value)

    def _rom_end_line(self, pstring, location, tokens):
        return MemEnd(Memory.ROM)

    def _rom_banksize_line(self, pstring, location, tokens):
        return MemBankSize(Memory.ROM, tokens.size)

    def _rom_bank_line(self, pstring, location, tokens):

        if 'label' in tokens.keys():
            # we need to resolve the bank label
            bank_num = Preprocessor().get_symbol(tokens.label)
            if bank_num is None:
                raise ParseFatalException('unknown bank name: %s' % tokens.label)
            bank_num = int(bank_num)

        if 'number' in tokens.keys():
            bank_num = tokens.number

        max = None
        if 'maxsize' in tokens.keys():
            max = tokens.maxsize

        return MemBankNumber(Memory.ROM, bank_num, max)

    def _chr_banksize_line(self, pstring, location, tokens):
        return MemBankSize(Memory.CHR, tokens.size)

    def _chr_bank_line(self, pstring, location, tokens):

        if 'label' in tokens.keys():
            # we need to resolve the bank label
            bank_num = int(Preprocessor().get_symbol(tokens.label))
            if bank_num is None:
                raise ParseFatalException('unknown bank name: %s' % tokens.label)

        if 'number' in tokens.keys():
            bank_num = tokens.number

        max = None
        if 'maxsize' in tokens.keys():
            max = tokens.maxsize

        return MemBankNumber(Memory.CHR, bank_num, max)

    def _chr_link_line(self, pstring, location, tokens):

        size = None
        if 'size' in tokens.keys():
            size = tokens.size

        return MemBankLink(Memory.CHR, tokens.file_path, size)

    def _tell_bank_line(self, pstring, location, tokens):
        return Tell(Tell.NUMBER)

    def _tell_bankoffset_line(self, pstring, location, tokens):
        return Tell(Tell.OFFSET)

    def _tell_banksize_line(self, pstring, location, tokens):
        return Tell(Tell.SIZE)

    def _tell_bankfree_line(self, pstring, location, tokens):
        return Tell(Tell.FREE)

    def _tell_banktype_line(self, pstring, location, tokens):
        return Tell(Tell.TYPE)


