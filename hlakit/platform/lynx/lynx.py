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

import os
from pyparsing import *
from hlakit.cpu.mos6502 import MOS6502, MOS6502Preprocessor, MOS6502Compiler, MOS6502Generator
from loader import LynxLoader
from lnx import Lnx, LnxSetting
from rompp import LynxRomOrg, LynxRomEnd, LynxRomBank, LynxRomPadding

class LynxPreprocessor(MOS6502Preprocessor):

    @classmethod
    def first_exprs(klass):
        e = []

        # start with the first base preprocessor rules 
        e.extend(MOS6502Preprocessor.first_exprs())

        # add in Lynx specific preprocessor parse rules
        e.append(('lynxloader', LynxLoader.exprs()))
        e.append(('lnxsetting', LnxSetting.exprs()))
        e.append(('lynxromorg', LynxRomOrg.exprs()))
        e.append(('lynxromend', LynxRomEnd.exprs()))
        e.append(('lynxrombank', LynxRomBank.exprs()))
        e.append(('lynxrompadding', LynxRomPadding.exprs()))
        
        return e


class LynxCompiler(MOS6502Compiler):

    @classmethod
    def first_exprs(klass):
        e = []

        # start with the first, base compiler rules
        e.extend(MOS6502Compiler.first_exprs())

        # add in the Lynx specific compiler parse rules

        return e

class LynxGenerator(MOS6502Generator):

    def _resolve_value(self, name, type_):
        pass

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
            romfile.set_lnx_rom_org(token.get_segment(), 
                                token.get_counter(), 
                                token.get_maxsize())
        elif isinstance(token, LynxRomEnd):
            romfile.set_rom_end()
        elif isinstance(token, LynxRomBank):
            romfile.set_rom_bank(token.get_number())
        elif isinstance(token, LynxRomPadding):
            romfile.set_rom_padding(token.get_value())
        else:
            # pass the token along to the CPU generator
            super(LynxGenerator, self)._process_token(token)

    def _initialize_rom(self):
        """ This function returns the RomFile to be used for this session """
        return Lnx()

    def _finalize_rom(self):
        # look up the loader function, encrypt it and put it at the front of
        # the rom list

        # output all blocks in the rom list to the rom
        romfile = self.romfile()
        bufs = romfile.get_buffers()
        print "Buffers:"
        for b in bufs:
            print '%s' % b

    def build_rom(self, tokens):

        # initialize the rom output pass
        self._initialize_rom()

        # process each of the tokens
        for t in tokens:
            self._process_token(t)

        # finalize the rom output pass
        self._finalize_rom()


class Lynx(MOS6502):

    CPU = 'mos6502'

    def __init__(self):

        # init the base class 
        super(Lynx, self).__init__()

    def preprocessor(self):
        return LynxPreprocessor()

    def compiler(self):
        return LynxCompiler()

    def generator(self):
        return LynxGenerator()



