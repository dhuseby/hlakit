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
import ply.lex as lex

from ..target import Target
from ..preprocessor import Preprocessor
from ..lexer import Lexer
from ..symboltable import SymbolTable
from ..paths import Paths
#from ..families.atari import Atari
#from ..platforms.lynx import Lynx
#from ..cpus.mos65sc02 import MOS65SC02

TARGET_CLASS = 'AtariLynxMOS65SC02'

class AtariLynxMOS65SC02(Target):

    def __init__(self):
        super(AtariLynxMOS65SC02, self).__init__()
        self._lexer = Lexer()
        self._preprocessor = Preprocessor()
        self._lexer.register_callbacks( self._preprocessor )

    def scan(self, f):
        """ feed the file through the lexer and return the tokens """
        self._lexer.push_lex_context_file(f)
        tokens = self._lexer.scan()
        SymbolTable().dump()
        Paths().dump()
        return tokens


