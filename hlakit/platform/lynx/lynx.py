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
from hlakit.cpu.mos6502 import MOS6502, MOS6502Preprocessor, MOS6502Compiler
from loader import LynxLoader
from lnx import Lnx, LnxSetting
from rom import LynxRomOrg, LynxRomEnd, LynxRomBank, LynxRomPadding

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
        return None



