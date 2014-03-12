"""
Copyright (c) 2010-2014 David Huseby. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDERS AND CONTRIBUTORS OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of copyright holders and contributors.
"""

from ..platform import Platform
from ..lexer import Lexer, LexerError

PLATFORM_CLASS = 'Lynx'
CPUS = ['mos65sc02']

class Lynx(Platform):

    def __init__(self):
        super(Lynx, self).__init__()

class LynxLexer(Lexer):

    # this class needs to register these as #<keyword> callbacks
    # with the lexer object that is passed into the regiser function
    # these will use register_preprocessor call to hook up the callbacks
    reserved = {
        'align'         : 'ALIGN',
        'rom'           : 'ROM',
        'ram'           : 'RAM',
        'loader'        : 'LOADER',
        'bank'          : 'BANK',
        'org'           : 'ORG',
        'end'           : 'END',
        'blockof'       : 'BLOCKOF',
        'lnx'           : 'LNX',
        'version'       : 'VERSION',
        'name'          : 'NAME',
        'manufacturer'  : 'MANUFACTURER',
        'rotation'      : 'ROTATION',
        'banks'         : 'BANKS',
        'block_count'   : 'BLOCKS',
        'block_size'    : 'BLOCKSIZE',
        'off'           : 'OFF'
    }

    tokens = [
        'NL',
        'ID',
        'WS',
        'STRING',
        'NUMBER',
        'IMMEDIATE'
    ] + list(reserved.values())

    def __init__(self):
        super(Lexer, self).__init__()
        self._lnx_header = {}
        self._blocks = {}

    def t_NL(self, t):
        r'\n'
        t.lexer.lineno += 1
        return t

    def t_WS(self, t):
        r'\s+'
        # eat whitespace

    def t_define_ID(self, t):
        r'[a-zA-Z_][\w]*'
        # check for a reserved word
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_HASH(self, t):
        r'\#'

