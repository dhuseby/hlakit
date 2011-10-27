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

from hlakit.common.ppparser import PPParser as CommonPPParser

class PPParser(CommonPPParser):

    def __init__(self, tokens=[]):
        super(PPParser, self).__init__(tokens)

    def p_program(self, p):
        '''program : cpu_statement
                   | program cpu_statement'''
        if len(p) == 2:
            p[0] = ('program', [ p[1] ])
        elif len(p) == 3:
            p[0] = ('program', p[1][1] + [ p[2] ])


    def p_cpu_statement(self, p):
        '''cpu_statement : common_statement
                         | mos6502_pp_statement'''
        if self.is_enabled():
            p[0] = p[1]

    def p_mos6502_pp_statement(self, p):
        '''mos6502_pp_statement : HASH LP_INTERRUPT '.' LP_START ID NL
                                | HASH LP_INTERRUPT '.' LP_NMI ID NL
                                | HASH LP_INTERRUPT '.' LP_IRQ ID NL'''
        p[0] = ('mos6502_pp_statement', p[4], p[5])

    def p_pp_block_body(self, p):
        '''pp_block_body : cpu_statement
                         | pp_block_body cpu_statement'''
        if self.is_enabled():
            if len(p) == 2:
                p[0] = [ p[1] ]
            elif len(p) == 3:
                p[0] = p[1] + [ p[2] ]

    def p_pp_define_body(self, p):
        '''pp_define_body : cpu_statement
                          | pp_define_body BS NL cpu_statement'''
        if len(p) == 2:
            p[0] = [ p[1] ]
        elif len(p) == 5:
            p[0] = p[1] + [ p[4] ]

    # must have a p_error rule
    def p_error(self, p):
        import pdb; pdb.set_trace()
        print "Syntax error in input!"

