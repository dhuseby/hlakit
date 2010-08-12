"""
HLAKit
Copyright (c) 2010 David Huseby. All rights reserved.

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

from pyparsing import *
from session import Session
from symboltable import SymbolTable
from name import Name
from functioncall import FunctionCall
from numericvalue import NumericValue
from immediate import Immediate

class Conditional(object):
    """
    This encapsulates a conditional statement
    """

    IF, ELSE, WHILE, DO, FOREVER, SWITCH, CASE, DEFAULT = range(8)

    @classmethod
    def exprs(klass):
        cond = klass._get_conditions()
        regs = klass._get_switch_registers()
        if_ = Group(Suppress('if') + \
                        Suppress('(') + \
                        cond.setResultsName('cond') + \
                        Suppress(')')).setResultsName('if_')
        else_ = Group(Suppress('else')).setResultsName('else_')
        while_ = Group(Suppress('while') + \
                           Suppress('(') + \
                           cond + \
                           Suppress(')')).setResultsName('while_')
        do_ = Group(Suppress('do')).setResultsName('do_')
        forever_ = Group(Suppress('forever')).setResultsName('forever_')
        switch_ = Group(Suppress('switch') + \
                            Suppress('(') + \
                            regs + \
                            Suppress(')')).setResultsName('switch_')
        case_ = Group(Suppress('case') + \
                          Suppress('#') + \
                          Immediate.exprs()).setResultsName('case_')
        default_ = Group(Suppress('default')).setResultsName('default_')

        expr = Or([if_, else_, while_, do_, forever_, switch_, case_, default_])
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, mode, cond=None):
        self._mode = mode
        self._cond = cond

    def get_mode(self):
        return self._mode

    output = { IF: 'if',
               ELSE: 'else',
               WHILE: 'while',
               DO: 'do',
               FOREVER: 'forever',
               SWITCH: 'switch',
               CASE: 'case',
               DEFAULT: 'default' }

    def __str__(self):
        s = self.output[self.get_mode()]
        if self.get_mode() in (IF, WHILE, SWITCH):
            s += '(' + str(self.get_cond()) + ')'
        return s

    __repr__ = __str__
