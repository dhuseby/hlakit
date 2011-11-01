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

from hlakit.common.session import Session
from hlakit.cpu.ricoh2A0X.ppparser import PPParser as Ricoh2A0XPPParser

class PPParser(Ricoh2A0XPPParser):

    def __init__(self, tokens=[]):
        super(PPParser, self).__init__(tokens)

    def p_program(self, p):
        '''program : platform_statement
                   | program platform_statement'''
        if len(p) == 2:
            p[0] = ('program', [ p[1] ])
        elif len(p) == 3:
            p[0] = ('program', p[1][1] + [ p[2] ])

    def p_platform_statement(self, p):
        '''platform_statement : cpu_statement
                              | nes_pp_statement'''
        if self.is_enabled():
            p[0] = p[1]

    def p_nes_pp_statement(self, p):
        '''nes_pp_statement : HASH nes_pp_mem_statement
                            | HASH nes_pp_ines_statement'''
        if self.is_enabled():
            p[1] = p[1]

    def p_nes_pp_mem_statement(self, p):
        '''nes_pp_mem_statement : PP_RAM '.' PP_END NL
                                | PP_RAM '.' PP_ORG number NL
                                | PP_RAM '.' PP_ORG number ',' number NL
                                | PP_ROM '.' PP_END NL
                                | PP_ROM '.' PP_ORG number NL
                                | PP_ROM '.' PP_BANKSIZE number NL
                                | PP_ROM '.' PP_BANK number NL
                                | PP_ROM '.' PP_BANK number ',' number NL
                                | PP_ROM '.' PP_ORG number ',' number NL
                                | PP_CHR '.' PP_END NL
                                | PP_CHR '.' PP_BANKSIZE number NL
                                | PP_CHR '.' PP_LINK filename NL
                                | PP_CHR '.' PP_LINK filename ',' number NL
                                | PP_CHR '.' PP_BANK number NL
                                | PP_CHR '.' PP_BANK number ',' number NL
                                | PP_SETPAD STRING NL
                                | PP_SETPAD number NL
                                | PP_ALIGN number NL'''
        if len(p) == 4:
            p[0] = ('nes_pp_mem_statement', p[1], p[2])
        elif len(p) == 5:
            p[0] = ('nes_pp_mem_statement', p[1], p[3])
        elif len(p) == 6:
            p[0] = ('nes_pp_mem_statement', p[1], p[3], p[4])
        elif len(p) == 8:
            p[0] = ('nes_pp_mem_statement', p[1], p[3], p[4], p[6])

    def p_nes_pp_ines_statement(self, p):
        '''nes_pp_ines_statement : PP_INES '.' PP_MAPPER STRING NL
                                 | PP_INES '.' PP_MAPPER number NL
                                 | PP_INES '.' PP_MIRRORING STRING NL
                                 | PP_INES '.' PP_MIRRORING number NL
                                 | PP_INES '.' PP_FOURSCREEN STRING NL
                                 | PP_INES '.' PP_FOURSCREEN number NL
                                 | PP_INES '.' PP_BATTERY STRING NL
                                 | PP_INES '.' PP_BATTERY number NL
                                 | PP_INES '.' PP_TRAINER STRING NL
                                 | PP_INES '.' PP_TRAINER number NL
                                 | PP_INES '.' PP_PRGREPEAT number NL
                                 | PP_INES '.' PP_CHRREPEAT number NL'''
        p[0] = ('nes_pp_ines_statement', p[3], p[4])

    # must have a p_error rule
    def p_error(self, p):
        print "Syntax error in input! File: %s, Line: %s" % (Session().get_cur_file(), p.lineno)
        import pdb; pdb.set_trace()

