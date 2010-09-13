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

    def _process_token(self, token):

        # handle generic token
        if isinstance(token, Variable):
            pass
        elif isinstance(token, Function):
            pass
        elif isinstance(token, TellBank):
            pass
        elif isinstance(token, TellBankOffset):
            pass
        elif isinstance(token, TellBankSize):
            pass
        elif isinstance(token, TellBankFree):
            pass
        elif isinstance(token, TellBankType):
            pass
        elif isinstance(token, Incbin):
            pass
        elif isinstance(token, RomOrg):
            pass
        elif isinstance(token, RomEnd):
            pass
        elif isinstance(token, RomBanksize):
            pass
        elif isinstance(token, RomBank):
            pass
        elif isinstance(token, RamOrg):
            pass
        elif isinstance(token, RamEnd):
            pass
        elif isinstance(token, SetPad):
            pass
        elif isinstance(token, Align):
            pass
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
