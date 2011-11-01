"""
HLAKit
Copyright (c) 2010-2011 David Huseby. All rights reserved.

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

from hlakit.cpu.ricoh2A0X.pplexer import PPLexer as Ricoh2A0XPPLexer

class PPLexer(Ricoh2A0XPPLexer):

    # NES specific preprocessors
    nes_preprocessor = {
        'ram': 'PP_RAM',
        'rom': 'PP_ROM',
        'org': 'PP_ORG',
        'end': 'PP_END',
        'banksize': 'PP_BANKSIZE',
        'bank': 'PP_BANK',
        'setpad': 'PP_SETPAD',
        'align': 'PP_ALIGN',
        'ines': 'PP_INES',
        'mapper': 'PP_MAPPER',
        'mirroring': 'PP_MIRRORING',
        'fourscreen': 'PP_FOURSCREEN',
        'battery': 'PP_BATTERY',
        'trainer': 'PP_TRAINER',
        'prgrepeat': 'PP_PRGREPEAT',
        'chrrepeat': 'PP_CHRREPEAT',
        'chr': 'PP_CHR',
        'link': 'PP_LINK',
    }

    # NES tokens list
    tokens = Ricoh2A0XPPLexer.tokens \
             + list(set(nes_preprocessor.values()))

    # identifier
    def t_ID(self, t):
        r'[a-zA-Z_][\w]*'

        value = t.value.lower()

        t.type = self.nes_preprocessor.get(value, None) # check for preprocessor words
        if t.type != None:
            t.value = value
            return t

        return super(PPLexer, self).t_ID(t)

    def __init__(self):
        super(PPLexer, self).__init__()


