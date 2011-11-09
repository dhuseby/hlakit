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
from hlakit.cpu.ricoh2A0X.parser import Parser as Ricoh2A0XParser

class Parser(Ricoh2A0XParser):

    def __init__(self, tokens=[]):
        super(Parser, self).__init__(tokens)

    def p_program(self, p):
        '''program : platform_statement
                   | program platform_statement'''

        nes = Session().get_target()

        if nes.has_block_started() and nes.get_cur_block()['start'] is None:
            nes.set_block_start(len(p[1][1]) - 1)

        if nes.has_block_ended():
            nes.set_block_end(len(p[1][1]))
            nes.reset_block()

        # call base class implementation
        super(Parser, self).p_program(p)

    def p_platform_statement(self, p):
        '''platform_statement : cpu_statement
                              | nes_pp_statement'''
        if p[1] != None:
            p[0] = p[1]

    def p_nes_pp_statement(self, p):
        '''nes_pp_statement : HASH nes_pp_mem_statement'''
        if p[2] != None:
            if isinstance(p[2], list):
                p[0] = [ p[1] ] + p[2]
            else:
                p[0] = p[1:]

    # no id necessary because macros have been expanded already
    def p_nes_pp_value(self, p):
        '''nes_pp_value : number
                        | STRING'''
        p[0] = p[1]

    def _clean_value(self, val):
        v = val

        # macro replacements cause values to be lists of tokens
        if isinstance(v, list):
            tmp = ''
            for i in v:
                tmp += '%s ' % i
            v = tmp

        # strip whitespace and brackets
        v = v.strip("\n\t\r '\"><")

        return v

    def p_nes_pp_mem_statement(self, p):
        '''nes_pp_mem_statement : PP_RAM '.' PP_END
                                | PP_RAM '.' PP_ORG nes_pp_value
                                | PP_RAM '.' PP_ORG nes_pp_value ',' nes_pp_value
                                | PP_ROM '.' PP_END
                                | PP_ROM '.' PP_ORG nes_pp_value
                                | PP_ROM '.' PP_BANKSIZE nes_pp_value
                                | PP_ROM '.' PP_BANK nes_pp_value
                                | PP_ROM '.' PP_BANK nes_pp_value ',' nes_pp_value
                                | PP_ROM '.' PP_ORG nes_pp_value ',' nes_pp_value
                                | PP_CHR '.' PP_END
                                | PP_CHR '.' PP_BANKSIZE nes_pp_value
                                | PP_CHR '.' PP_LINK filename
                                | PP_CHR '.' PP_LINK filename ',' nes_pp_value
                                | PP_CHR '.' PP_BANK nes_pp_value
                                | PP_CHR '.' PP_BANK nes_pp_value ',' nes_pp_value
                                | PP_SETPAD nes_pp_value
                                | PP_ALIGN nes_pp_value'''
        
        nes = Session().get_target()
        if p[1] in ('ram', 'rom', 'chr'):
            if p[3] in ('org', 'bank'):
                if nes.has_block_started():
                    t = nes.get_cur_block()['type']
                    if t != None and t != p[1]:
                        raise Exception('WARNING: unclosed %s block at file: %s, line: %s, included from: %s' % (t, Session().get_cur_file(), p.lexer.lineno, Session()._cur_file))
                else:
                    nes.start_block(p[1])
                if nes.get_cur_block()['type'] is None:
                    nes.set_block_type(p[1])

            if p[3] == 'org':
                nes.set_block_org(self._clean_value(p[4]))
                if len(p) == 8:
                    nes.set_block_maxsize(self._clean_value([6]))
            elif p[3] == 'bank':
                nes.set_block_bank(self._clean_value(p[4]))
                if len(p) == 8:
                    nes.set_banksize(self._clean_value(p[6]))
            elif p[3] == 'banksize':
                nes.set_banksize(self._clean_value(p[1]), self._clean_value(p[4]))
            elif p[3] == 'link':
                nes.set_block_link(p[4])
            elif p[3] == 'end':
                nes.end_block()
        elif p[1] == 'setpad':
            nes.set_padding(self._clean_value(p[2]))
        elif p[1] == 'align':
            nes.set_alignment(self._clean_value(p[2]))

        if len(p) == 3:
            p[0] = ('nes_pp_mem_statement', p[1], p[2])
        elif len(p) == 4:
            p[0] = ('nes_pp_mem_statement', p[1], p[3])
        elif len(p) == 5:
            p[0] = ('nes_pp_mem_statement', p[1], p[3], p[4])
        elif len(p) == 7:
            p[0] = ('nes_pp_mem_statement', p[1], p[3], p[4], p[6])

    # must have a p_error rule
    def p_error(self, p):
        if p != None:
            print "Syntax error in input! File: %s, Line: %s" % (Session().get_cur_file(), p.lineno)
        import pdb; pdb.set_trace()

