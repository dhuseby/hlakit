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

from hlakit.common.rompp import RomOrg
from hlakit.cpu.mos6502.generator import Generator as MOS6502Generator
from loader import LynxLoader
from lnx import Lnx
from lnxsetting import LnxSetting
from rompp import LynxRomOrg

class Generator(MOS6502Generator):

    def _process_token(self, token):

        # get the rom file
        romfile = self.romfile()

        # handle Lynx specific token
        if isinstance(token, LynxLoader):
            romfile.set_loader(token.get_fn())
        
        elif isinstance(token, LnxSetting):
            type_ = token.get_type()

            if type_ == LnxSetting.OFF:
                romfile.set_no_header()
            
            elif type_ == LnxSetting.PSB0:
                romfile.set_page_size_bank0(token.get_size())
            
            elif type_ == LnxSetting.PSB1:
                romfile.set_page_size_bank1(token.get_size())
            
            elif type_ == LnxSetting.VERSION:
                romfile.set_version(token.get_version())
            
            elif type_ == LnxSetting.CART_NAME:
                romfile.set_cart_name(token.get_name())
            
            elif type_ == LnxSetting.MANU_NAME:
                romfile.set_manufacturer_name(token.get_name())
            
            elif type_ == LnxSetting.ROTATION:
                romfile.set_rotation(token.get_rotation())
        
        elif isinstance(token, LynxRomOrg):
            # intercept LynxRomOrg tokens and set the rom addr
            romfile.set_rom_org(token.get_segment(), 
                                token.get_counter(), 
                                token.get_maxsize())
        
        elif isinstance(token, RomOrg):
            raise ParseFatalException('there should not be any RomOrg tokens in a Lynx compile')
        
        else:
            # pass the token along to the CPU generator
            super(Generator, self)._process_token(token)

    def _initialize_rom(self):
        """ This function returns the RomFile to be used for this session """
        return Lnx()


