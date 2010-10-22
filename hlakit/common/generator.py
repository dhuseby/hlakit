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

from pyparsing import *
from romfile import RomFile
from incbin import Incbin
from tell import TellBank, TellBankOffset, TellBankSize, TellBankFree, TellBankType
from rompp import RomOrg, RomEnd, RomBanksize, RomBank
from rampp import RamOrg, RamEnd
from setpad import SetPad
from align import Align
from variable import Variable
from function import Function
from label import Label

class Generator(object):
    """ This encapsulates the linker and code generator """

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def __init__(self):
        if not hasattr(self, '_romfile'):
            self._romfile = self._initialize_rom()

    def _process_variable(self, var):
        pass

    def _process_token(self, token):

        romfile = self.romfile()

        # handle generic token
        if isinstance(token, Variable):
            self._process_variable(token)
        
        elif isinstance(token, Label):
            # locate the label at the current addr
            token.set_address(romfile.get_current_pos())
            romfile.set_current_label(token)

        elif isinstance(token, TellBank):
            print 'MESSAGE: Current bank is %d' % romfile.get_current_bank()
        
        elif isinstance(token, TellBankOffset):
            print 'MESSAGE: Current offset is 0x%0.4x' % romfile.get_current_offset()
        
        elif isinstance(token, TellBankSize):
            print 'MESSAGE: Current bank size is 0x%0.4x' % romfile.get_current_banksize()
        
        elif isinstance(token, TellBankFree):
            print 'MESSAGE: Current bank free is 0x%0.4x' % romfile.get_current_bankfree()
        
        elif isinstance(token, TellBankType):
            print 'MESSAGE: Current bank type is %s' % romfile.get_current_banktype()
        
        elif isinstance(token, Incbin):
            romfile.incbin(token.get_data())
        
        elif isinstance(token, RomOrg):
            romfile.set_rom_org(token.get_address(), token.get_maxsize())
        
        elif isinstance(token, RomEnd):
            romfile.set_rom_end()
        
        elif isinstance(token, RomBanksize):
            romfile.set_rom_banksize(token.get_size())
        
        elif isinstance(token, RomBank):
            romfile.set_rom_bank(token.get_number(), token.get_maxsize())
        
        elif isinstance(token, RamOrg):
            romfile.set_ram_org(token.get_address(), token.get_maxsize())
        
        elif isinstance(token, RamEnd):
            romfile.set_ram_end()
        
        elif isinstance(token, SetPad):
            romfile.set_padding(token.get_value())
        
        elif isinstance(token, Align):
            romfile.set_align(token.get_value())
        
        else:
            raise ParseFatalException('Unknown token type: %s' % type(token))

    def _initialize_rom(self):
        return RomFile()

    def _finalize_rom(self):
        pass

    def romfile(self):
        return self._romfile

    def build_rom(self, tokens):

        # process each of the tokens
        for t in tokens:
            self._process_token(t)

        # finalize the rom output pass
        self._finalize_rom()
