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

from hlakit.cpu.mos6502 import MOS6502

from pplexer import PPLexer
from ppparser import PPParser

class Ricoh2A0X(MOS6502):
    '''
    The 2A03 is a custom integrated circuit used as the heart of NES game 
    consoles and Family Computers. To avoid costly glue logic, Nintendo squeezed 
    alot of hardware (alot for the time, which was like 1982) inside this chip. 
    Here is a list of known integrated components found in the 2A03 (* prefix 
    indicates simple hardware discussed next).

    - stock NMOS 6502 microprocessor lacking decimal mode support
    - low frequency programmable timer
    - two nearly-identical rectangle wave function generators
    - triangle wave function generator
    - random wavelength function generator
    - audio sample playback unit (delta modulation channel)
    - one shot programmable DMA transfer unit
    - master dodecade clock divider
    - two 6502 address decoders for $4016R and $4017R
    - 3-bit register and address decoder for $4016W
    '''

    def __init__(self):

        # preprpocessor lexer and parser
        self._pp_lexer = PPLexer()
        self._pp_parser = PPParser(tokens=self._pp_lexer.tokens)

        # general lexer and parser
        self._lexer = None
        self._parser = None

    def lexer(self):
        return self._lexer

    def parser(self):
        return self._parser

    def pp_lexer(self):
        return self._pp_lexer

    def pp_parser(self):
        return self._pp_parser

