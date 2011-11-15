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

    def p_program(self, p):
        '''program : common_statement
                   | program common_statement'''
        # call base class implementation
        super(PPParser, self).p_program(p)

    def p_common_statement(self, p):
        '''common_statement : pp_block_statement
                            | pp_statement
                            | base_statement
                            | mos6502_pp_statement
                            | nes_pp_statement
                            | empty_statement'''
        if self.is_enabled() and p[1] != None:
            p[0] = p[1]


    def p_nes_pp_statement(self, p):
        '''nes_pp_statement : nes_pp_mem_statement
                            | nes_pp_ines_statement'''
        if self.is_enabled() and p[2] != None:
            if isinstance(p[2], list):
                p[0] = [ p[1] ] + p[2]
            else:
                p[0] = p[1:]

    def p_nes_pp_value(self, p):
        '''nes_pp_value : id
                        | number
                        | STRING'''
        p[0] = p[1]

    def p_nes_pp_mem_statement(self, p):
        '''nes_pp_mem_statement : PPRAMEND NL
                                | PPRAMORG nes_pp_value NL
                                | PPRAMORG nes_pp_value ',' nes_pp_value NL
                                | PPROMEND NL
                                | PPROMORG nes_pp_value NL
                                | PPROMBANKSIZE nes_pp_value NL
                                | PPROMBANK nes_pp_value NL
                                | PPROMBANK nes_pp_value ',' nes_pp_value NL
                                | PPROMORG nes_pp_value ',' nes_pp_value NL
                                | PPCHREND NL
                                | PPCHRBANKSIZE nes_pp_value NL
                                | PPCHRLINK filename NL
                                | PPCHRLINK filename ',' nes_pp_value NL
                                | PPCHRBANK nes_pp_value NL
                                | PPCHRBANK nes_pp_value ',' nes_pp_value NL
                                | PPSETPAD nes_pp_value NL
                                | PPALIGN nes_pp_value NL'''
        output = []
        for i in xrange(1, len(p)):
            if isinstance(p[i], list):
                output += p[i]
            else:
                output.append(p[i])
        p[0] = output

    def p_nes_pp_ines_statement(self, p):
        '''nes_pp_ines_statement : PPINESOFF NL
                                 | PPINESMAPPER nes_pp_value NL
                                 | PPINESMIRRORING nes_pp_value NL
                                 | PPINESFOURSCREEN nes_pp_value NL
                                 | PPINESBATTERY nes_pp_value NL
                                 | PPINESTRAINER nes_pp_value NL
                                 | PPINESPRGREPEAT nes_pp_value NL
                                 | PPINESCHRREPEAT nes_pp_value NL'''
        value = None
        if len(p) == 3:
            value = True
        else:
            # strip quotes off if they exist
            value = self._clean_value(p[2])

        # store the ines setting in the target
        Session().get_target()[p[1]] = value

    # must have a p_error rule
    def p_error(self, p):
        print "Syntax error in input! File: %s, Line: %s" % (Session().get_cur_file(), p.lineno)
        import pdb; pdb.set_trace()


