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

from session import Session
from symboltable import SymbolTable
from ppmacro import PPMacro
from buffer import Buffer

class PPParser(object):

    def __init__(self, tokens=[]):
        self.tokens = tokens
        self._enabled = [ True ]
        self._depth = 0

    def is_enabled(self):
        return self._enabled[-1]

    def p_program(self, p):
        '''program : common_statement
                   | program common_statement'''
        if len(p) == 2:
            if p[1] is None:
                p[0] = ('program', [])
            else:
                if isinstance(p[1], list):
                    p[0] = ('program', p[1])
                else:
                    p[0] = ('program', [ p[1] ])
        elif len(p) == 3:
            if p[2] is None:
                p[0] = ('program', p[1][1])
            else:
                if isinstance(p[2], list):
                    p[0] = ('program', p[1][1] + p[2])
                else:
                    p[0] = ('program', p[1][1] + [ p[2] ])

    def p_common_statement(self, p):
        '''common_statement : pp_block_statement
                            | pp_statement
                            | base_statement
                            | empty_statement'''
        if self.is_enabled() and p[1] != None:
            p[0] = p[1]

    def p_empty_statement(self, p):
        '''empty_statement : NL
                           | empty_statement NL'''
        pass

    def p_pp_block_statement(self, p):
        '''pp_block_statement : pp_block_start pp_block_body pp_block_else pp_block_body pp_block_end
                              | pp_block_start pp_block_body pp_block_end'''
        if len(p) == 4:
            if p[2] is None:
                return
            p[0] = p[2]
        elif len(p) == 6:
            if p[2] is None:
                p[0] = p[4]
            else:
                p[0] = p[2]

    def p_pp_block_start(self, p):
        '''pp_block_start : PPIFDEF ID NL
                          | PPIFNDEF ID NL '''

        # only execute the logic if we're enabled
        if self.is_enabled():
            # check to see if the symbol is defined
            defined = (SymbolTable().lookup_symbol(p[2]) != None)

            # execute the ifdef/ifndef logic
            if ((defined == False) and (p[1] == '#ifdef')) or (defined and (p[1] == '#ifndef')):
                self._enabled.append(False)
            else:
                self._enabled.append(True)
        else:
            # we're disabled so push a False to track depth while keeping disabled state
            self._enabled.append(False)

        p[0] = ('pp_block_start', p[1], p[2])

    def p_pp_block_else(self, p):
        '''pp_block_else : PPELSE NL '''

        if len(self._enabled) == 1:
            print "ERROR: unmatched #else"
            return

        # remove the top item in the list
        old_state = self._enabled.pop()

        # only execute the logic if this is a top level else
        if self.is_enabled():
            # flip the enabled state
            self._enabled.append(not old_state)
        else:
            # we're disabled so push a False to track depth while keeping disabled state
            self._enabled.append(False)

        p[0] = ('pp_block_else', p[1])

    def p_pp_block_end(self, p):
        '''pp_block_end : PPENDIF NL '''

        if len(self._enabled) == 1:
            print "ERROR: unmatched #endif"
            return

        # pop the current state off of the stack
        self._enabled.pop()

        p[0] = ('pp_block_end', p[1])

    def p_pp_block_body(self, p):
        '''pp_block_body : common_statement
                         | pp_block_body common_statement'''

        if self.is_enabled():
            if len(p) == 2:
                if p[1] is None:
                    p[0] = []
                    return
                if isinstance(p[1], list):
                    p[0] = p[1]
                else:
                    p[0] = [ p[1] ]
            elif len(p) == 3:
                if p[2] is None:
                    p[0] = p[1]
                    return
                if isinstance(p[2], list):
                    p[0] = p[1] + p[2]
                else:
                    p[0] = p[1] + [ p[2] ]

    def p_pp_statement(self, p):
        '''pp_statement : pp_include NL
                        | pp_incbin NL
                        | pp_define NL
                        | pp_undef NL
                        | pp_msg NL'''
        p[0] = p[1]

    def p_pp_define(self, p):
        '''pp_define : PPDEFINE ID empty
                     | PPDEFINE ID pp_define_body
                     | PPDEFINE ID '(' pp_define_params ')' pp_define_body'''

        name = p[2]
        value = []
        params = None

        if len(p) == 4:
            value = p[3]
        elif len(p) == 7:
            value = p[6]
            params = p[4]

        SymbolTable().new_symbol( name, PPMacro(name, value, params) )

    def p_pp_define_params(self, p):
        '''pp_define_params : ID
                            | pp_define_params ',' ID'''

        if len(p) == 2:
            if p[1] is None:
                p[0] = []
                return
            if isinstance(p[1], list):
                p[0] = p[1]
            else:
                p[0] = [ p[1] ]
        elif len(p) == 4:
            if p[3] is None:
                p[0] = p[1]
                return
            if isinstance(p[3], list):
                p = p[1] + p[3]
            else:
                p[0] = p[1] + [ p[3] ]

    def p_pp_define_body(self, p):
        '''pp_define_body : pp_block_statement
                          | pp_statement
                          | pp_define_body_statement '''
        p[0] = p[1]

    def p_pp_define_body_statement(self, p):
        ''' pp_define_body_statement : pp_define_body_token
                                     | pp_define_body pp_define_body_token'''
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
                return
            if isinstance(p[1], list):
                p[0] = p[1]
            else:
                p[0] = [ p[1] ]
        elif len(p) == 3:
            if p[2] is None:
                p[0] = p[1]
                return
            if isinstance(p[2], list):
                p[0] = p[1] + p[2]
            else:
                p[0] = p[1] + [ p[2] ]

    def p_pp_define_body_token(self, p):
        '''pp_define_body_token : number
                                | ID
                                | STRING
                                | HASH
                                | '.'
                                | '+'
                                | '-'
                                | '*'
                                | '/'
                                | '~'
                                | '!'
                                | '%'
                                | '>'
                                | '<'
                                | '='
                                | '&'
                                | '^'
                                | '|'
                                | '{'
                                | '}'
                                | '('
                                | ')'
                                | '['
                                | ']'
                                | ':'
                                | ',' '''
        p[0] = p[1]

    def p_pp_undef(self, p):
        '''pp_undef : PPUNDEF ID'''
        SymbolTable().del_symbol(p[2])

    def p_pp_include(self, p):
        '''pp_include : PPINCLUDE filename'''

        # resolve the file name path
        #print "Including %s from: %s, line: %s" % (p[2][1:-1], Session().get_cur_file(), p.lexer.lineno)
        fpath = Session().get_file_path(p[2][1:-1], (p[2][0] == '<'))

        if fpath is None:
            import pdb; pdb.set_trace()

        # get the program ast for the included file
        prg = Session().preprocess_file(fpath)
 
        if p is None or prg is None:
            import pdb; pdb.set_trace()

        p[0] = prg[1]

    def p_pp_msg(self, p):
        '''pp_msg : PPTODO STRING
                  | PPWARNING STRING
                  | PPERROR STRING
                  | PPFATAL STRING'''
        msg = '%s: %s' % (p[1].upper(), p[2])
        print msg

    def p_pp_incbin(self, p):
        '''pp_incbin : PPINCBIN filename'''

        # resolve the file name path
        fpath = Session().get_file_path(p[2][1:-1], (p[2][0] == '<'))
        #print 'INCLUDING BINARY: %s' % fpath

        p[0] = [ '#', 'incbin', '"' + fpath + '"', '\n' ]

    def p_base_statement(self, p):
        '''base_statement : base_token
                          | base_statement base_token'''
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
                return
            if isinstance(p[1], list):
                p[0] = p[1]
            else:
                p[0] = [ p[1] ]
        elif len(p) == 3:
            if p[2] is None:
                p[0] = p[1]
                return
            if isinstance(p[2], list):
                p[0] = p[1] + p[2]
            else:
                p[0] = p[1] + [ p[2] ]

    def p_number(self, p):
        '''number : DECIMAL
                  | KILO
                  | HEXC
                  | HEXS
                  | BINARY'''
        p[0] = p[1]

    def p_filename(self, p):
        '''filename : STRING
                    | BSTRING'''
        p[0] = p[1]

    def p_base_token(self, p):
        '''base_token     : number
                          | id
                          | STRING
                          | NL
                          | HASH
                          | '.'
                          | '+'
                          | '-'
                          | '*'
                          | '/'
                          | '~'
                          | '!'
                          | '%'
                          | '>'
                          | '<'
                          | '='
                          | '&'
                          | '^'
                          | '|'
                          | '{'
                          | '}'
                          | '('
                          | ')'
                          | '['
                          | ']'
                          | ':'
                          | ',' '''
        p[0] = p[1]

    def p_id(self, p):
        '''id : ID'''
        macro = SymbolTable().lookup_symbol(p[1])
        if macro:
            print "Replacing %s with %s" % (p[1], macro.value)
            p[0] = macro.value
            return

        p[0] = p[1]

    def p_empty(self, p):
        '''empty : '''
        pass

    # must have a p_error rule
    def p_error(self, p):
        print "Syntax error in input! File: %s, Line: %s" % (Session().get_cur_file(), p.lineno)
        import pdb; pdb.set_trace()

