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

THIS SOFTWARE IS PROVIDED BY DAVID HUSEBY `AS IS'' AND ANY EXPRESS OR IMPLIED
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

from hlakit.cpu.mos6502.generator import Generator as MOS6502Generator
from ines import iNES, iNESMapper, iNESMirroring, iNESFourscreen, iNESBattery, iNESTrainer, iNESPrgRepeat, iNESChrRepeat, iNESOff
from chr import ChrBanksize, ChrBank, ChrLink, ChrEnd

class Generator(MOS6502Generator):

    def _resolve_value(self, name, type_):
        pass

    def _process_token(self, token):

        # get the rom file
        romfile = self.romfile()

        # handle NES specific token
        if isinstance(token, iNES):
            pass
        elif isinstance(token, iNESMapper):
            pass
        elif isinstance(token, iNESMirroring):
            pass
        elif isinstance(token, iNESFourscreen):
            pass
        elif isinstance(token, iNESBattery):
            pass
        elif isinstance(token, iNESTrainer):
            pass
        elif isinstance(token, iNESPrgRepeat):
            pass
        elif isinstance(token, iNESChrRepeat):
            pass
        elif isinstance(token, iNESOff):
            pass
        elif isinstance(token, ChrBanksize):
            pass
        elif isinstance(token, ChrBank):
            pass
        elif isinstance(token, ChrLink):
            pass
        elif isinstance(token, ChrEnd):
            pass
        else:
            # pass the token along to the CPU generator
            super(Generator, self)._process_token(token)

    def _initialize_rom(self):
        """ This function returns the RomFile to be used for this session """
        return None

    def _finalize_rom(self):
        pass

    def build_rom(self, tokens):
        pass

