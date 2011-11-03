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

        nes = Session().get_target()
        block = None

        if nes.has_block_started() and nes.get_block()['start'] is None:
            nes.set_block_start(len(p[1][1]) - 1)

        if nes.has_block_ended():
            nes.set_block_end(len(p[1][1]))
            block = nes.clear_block()
        
        if len(p) == 2:
            if p[1] is None:
                p[0] = ('program', [], [])
            else:
                if isinstance(p[1], list):
                    p[0] = ('program', p[1], [])
                else:
                    p[0] = ('program', [ p[1] ], [])
        elif len(p) == 3:
            if p[2] is None:
                p[0] = ('program', p[1][1], p[1][2])
            else:
                if isinstance(p[2], list):
                    p[0] = ('program', p[1][1] + p[2], p[1][2])
                else:
                    p[0] = ('program', p[1][1] + [ p[2] ], p[1][2])

        if block != None:
            p[0][2].append(block)

    def p_platform_statement(self, p):
        '''platform_statement : cpu_statement
                              | nes_pp_statement'''
        if self.is_enabled() and p[1] != None:
            p[0] = p[1]

    def p_nes_pp_statement(self, p):
        '''nes_pp_statement : HASH nes_pp_mem_statement
                            | HASH nes_pp_ines_statement'''
        pass
        #if self.is_enabled():
        #    p[0] = p[2]

    def p_nes_pp_value(self, p):
        '''nes_pp_value : id
                        | number
                        | STRING'''
        p[0] = p[1]

    def _clean_value(self, val):
        if val[0] == '"' and val[-1] == '"':
            return val[1:-1]
        return val

    def p_nes_pp_mem_statement(self, p):
        '''nes_pp_mem_statement : PP_RAM '.' PP_END NL
                                | PP_RAM '.' PP_ORG nes_pp_value NL
                                | PP_RAM '.' PP_ORG nes_pp_value ',' nes_pp_value NL
                                | PP_ROM '.' PP_END NL
                                | PP_ROM '.' PP_ORG nes_pp_value NL
                                | PP_ROM '.' PP_BANKSIZE nes_pp_value NL
                                | PP_ROM '.' PP_BANK nes_pp_value NL
                                | PP_ROM '.' PP_BANK nes_pp_value ',' nes_pp_value NL
                                | PP_ROM '.' PP_ORG nes_pp_value ',' nes_pp_value NL
                                | PP_CHR '.' PP_END NL
                                | PP_CHR '.' PP_BANKSIZE nes_pp_value NL
                                | PP_CHR '.' PP_LINK filename NL
                                | PP_CHR '.' PP_LINK filename ',' nes_pp_value NL
                                | PP_CHR '.' PP_BANK nes_pp_value NL
                                | PP_CHR '.' PP_BANK nes_pp_value ',' nes_pp_value NL
                                | PP_SETPAD nes_pp_value NL
                                | PP_ALIGN nes_pp_value NL'''

        nes = Session().get_target()
        if p[1] in ('ram', 'rom', 'chr'):
            if p[3] in ('org', 'bank'):
                if nes.has_block_started():
                    t = nes.get_block()['type']
                    if t != None and t != p[1]:
                        raise Exception('WARNING: unclosed %s block at file: %s, line: %s, included from: %s' % (t, Session().get_cur_file(), p.lexer.lineno, Session()._cur_file))
                else:
                    nes.start_block(p[1])
                if nes.get_block()['type'] is None:
                    nes.set_block_type(p[1])

            if p[3] == 'org':
                nes.set_block_org(p[4])
                if len(p) == 8:
                    nes.set_block_maxsize(p[6])
            elif p[3] == 'bank':
                nes.set_block_bank(p[4])
                if len(p) == 8:
                    nes.set_banksize(p[6])
            elif p[3] == 'banksize':
                nes.set_banksize(p[1], p[4])
            elif p[3] == 'link':
                nes.set_block_link(p[4])
            elif p[3] == 'end':
                nes.end_block()
        elif p[1] == 'setpad':
            nes.set_padding(self._clean_value(p[2]))
        elif p[1] == 'align':
            nes.set_alignment(self._clean_value(p[2]))

        if len(p) == 4:
            p[0] = ('nes_pp_mem_statement', p[1], p[2])
        elif len(p) == 5:
            p[0] = ('nes_pp_mem_statement', p[1], p[3])
        elif len(p) == 6:
            p[0] = ('nes_pp_mem_statement', p[1], p[3], p[4])
        elif len(p) == 8:
            p[0] = ('nes_pp_mem_statement', p[1], p[3], p[4], p[6])

    def p_nes_pp_ines_statement(self, p):
        '''nes_pp_ines_statement : PP_INES '.' PP_OFF NL
                                 | PP_INES '.' PP_MAPPER nes_pp_value NL
                                 | PP_INES '.' PP_MIRRORING nes_pp_value NL
                                 | PP_INES '.' PP_FOURSCREEN nes_pp_value NL
                                 | PP_INES '.' PP_BATTERY nes_pp_value NL
                                 | PP_INES '.' PP_TRAINER nes_pp_value NL
                                 | PP_INES '.' PP_PRGREPEAT nes_pp_value NL
                                 | PP_INES '.' PP_CHRREPEAT nes_pp_value NL'''
        value = None
        if p[1] == 'off':
            value = True
        else:
            # strip quotes off if they exist
            value = p[4]
            if value[0] == '"':
                value = value[1:-1]

        # store the ines setting in the target
        Session().get_target()[p[3]] = value

        p[0] = ('nes_pp_ines_statement', p[3], value)

    # must have a p_error rule
    def p_error(self, p):
        print "Syntax error in input! File: %s, Line: %s" % (Session().get_cur_file(), p.lineno)
        import pdb; pdb.set_trace()

