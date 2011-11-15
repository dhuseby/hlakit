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

from hlakit.cpu.ricoh2A0X.lexer import Lexer as Ricoh2A0XLexer

class Lexer(Ricoh2A0XLexer):

    '''NOTE: that the handling of RAM/ROM/CHR preprocessor statements is done
       at the compiler level so we need to be able to parse them from the input
       stream of text.  However, the #ines preprocessor statements were handled
       during the preprocess stage and don't need to be handled here.'''

    # NES tokens list
    tokens = Ricoh2A0XLexer.tokens \
           + [ 'PPRAMORG',
               'PPRAMEND',
               'PPROMORG',
               'PPROMBANK',
               'PPROMBANKSIZE',
               'PPROMEND',
               'PPCHRBANK',
               'PPCHRBANKSIZE',
               'PPCHRLINK',
               'PPCHREND',
               'PPSETPAD',
               'PPALIGN' ]

    # NES compile time pre-processor directives
    t_PPRAMORG          = r'\#(?i)[\t ]*ram\.org'
    t_PPRAMEND          = r'\#(?i)[\t ]*ram\.end'

    t_PPROMORG          = r'\#(?i)[\t ]*rom\.org'
    t_PPROMBANK         = r'\#(?i)[\t ]*rom\.bank'
    t_PPROMBANKSIZE     = r'\#(?i)[\t ]*rom\.banksize'
    t_PPROMEND          = r'\#(?i)[\t ]*rom\.end'

    t_PPCHRBANK         = r'\#(?i)[\t ]*chr\.bank'
    t_PPCHRBANKSIZE     = r'\#(?i)[\t ]*chr\.banksize'
    t_PPCHRLINK         = r'\#(?i)[\t ]*chr\.link'
    t_PPCHREND          = r'\#(?i)[\t ]*chr\.end'

    t_PPSETPAD          = r'\#(?i)[\t ]*setpad'
    t_PPALIGN           = r'\#(?i)[\t ]*align'

    def __init__(self):
        super(Lexer, self).__init__()

