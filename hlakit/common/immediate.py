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
from name import Name
from numericvalue import NumericValue
from arrayvalue import ArrayValue

# turn on faster operatorPrecedence parsing
ParserElement.enablePackrat()

class bind1(object):

    def __init__(self, fn, type):
        self._fn = fn
        self._type = type

    def get_type(self):
        return self._type

    def __call__(self, pstring, location, tokens):
        return self._fn(pstring, location, tokens, self._type)


def get_args(tokens):
    args_ = None
    if 'numeric_terminal' in tokens.keys():
        args_ = tokens.numeric_terminal
    elif 'variable_terminal' in tokens.keys():
        # return the variable name
        args_ = Name('.'.join([str(v) for v in tokens.variable_terminal]))
    return args_


class Immediate(object):
    """
    This encapsulates an immediate value in the language
    """

    SIGN, SIZEOF, LO, HI, NYLO, NYHI, NEG, NOT, MULT, ADD, SHIFT, CMP, EQ, \
    AND, EXOR, OR, TERMINAL = range(17)

    TYPE = [ 'SIGN', 'SIZEOF', 'LO', 'HI', 'NYLO', 'NYHI', 'NEG', 'NOT',
             'MULT', 'ADD', 'SHIFT', 'CMP', 'EQ', 'AND', 'EXOR', 'OR',
             'TERMINAL' ]

    @classmethod
    def parse(klass, pstring, location, tokens, type_):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        # handle terminals
        if type_ == klass.TERMINAL:
            args_ = get_args(tokens)
            if args_ is None:
                if len(tokens) != 1:
                    raise ParseFatalException('invalid number of terminal arguments')
                if isinstance(tokens[0], Immediate):
                    return tokens[0]
            return klass(type_, args_)

        # handle single-argument, right-associative operators 
        elif type_ in (klass.SIGN, klass.SIZEOF, \
                       klass.LO,   klass.HI, \
                       klass.NYLO, klass.NYHI, \
                       klass.NEG,  klass.NOT):
            args_ = get_args(tokens[0])
            if args_ is None:
                if len(tokens[0]) != 2:
                    raise ParseFatalException('invalid number of op args')
                if isinstance(tokens[0][1], Immediate):
                    args_ = tokens[0][1]
            return klass(type_, args_)

        # handle double-argument, left-associative operators
        elif type_ in (klass.MULT,  klass.ADD, \
                       klass.SHIFT, klass.CMP, \
                       klass.EQ,    klass.AND, \
                       klass.EXOR,  klass.OR):
            # tokens[0][0] == left sub-expression
            # tokens[0][1] == operator string
            # tokens[0][2] == right sub-expression
            return klass(type_, tokens[0][0], tokens[0][2])

        raise ParseFatalException('invalid immediate expression')

    @classmethod
    def exprs(klass):
        signop = oneOf('+ -')
        sizeof_ = Literal('sizeof')
        lo_ = Literal('lo')
        hi_ = Literal('hi')
        nylo_ = Literal('nylo')
        nyhi_ = Literal('nyhi')
        negop = Literal('!')
        notop = Literal('~')
        multop = oneOf('* / %')
        plusop = oneOf('+ -')
        shiftop = oneOf('<< >>')
        cmpeqop = oneOf('< > <= >=')
        eqop = oneOf('!= ==')
        andop = Literal('&')
        exorop = Literal('^')
        orop = Literal('|')

        variable_ref = Group(delimitedList(Name.exprs(), delim='.'))
        imm = Or([NumericValue.exprs().setResultsName('numeric_terminal'),
                  variable_ref.setResultsName('variable_terminal')])

        expr = operatorPrecedence( imm,
                [ 
                  (signop,  1, opAssoc.RIGHT, bind1(klass.parse, klass.SIGN)),
                  (sizeof_, 1, opAssoc.RIGHT, bind1(klass.parse, klass.SIZEOF)),
                  (lo_,     1, opAssoc.RIGHT, bind1(klass.parse, klass.LO)),
                  (hi_,     1, opAssoc.RIGHT, bind1(klass.parse, klass.HI)),
                  (nylo_,   1, opAssoc.RIGHT, bind1(klass.parse, klass.NYLO)),
                  (nyhi_,   1, opAssoc.RIGHT, bind1(klass.parse, klass.NYHI)),
                  (negop,   1, opAssoc.RIGHT, bind1(klass.parse, klass.NEG)),
                  (notop,   1, opAssoc.RIGHT, bind1(klass.parse, klass.NOT)),
                  (multop,  2, opAssoc.LEFT, bind1(klass.parse, klass.MULT)),
                  (plusop,  2, opAssoc.LEFT, bind1(klass.parse, klass.ADD)),
                  (shiftop, 2, opAssoc.LEFT, bind1(klass.parse, klass.SHIFT)),
                  (cmpeqop, 2, opAssoc.LEFT, bind1(klass.parse, klass.CMP)),
                  (eqop,    2, opAssoc.LEFT, bind1(klass.parse, klass.EQ)),
                  (andop,   2, opAssoc.LEFT, bind1(klass.parse, klass.AND)),
                  (exorop,  2, opAssoc.LEFT, bind1(klass.parse, klass.EXOR)),
                  (orop,    2, opAssoc.LEFT, bind1(klass.parse, klass.OR)) 
                ])

        expr.setParseAction(bind1(klass.parse, klass.TERMINAL))
        return expr

    def __init__(self, type_, *args_):
        self._type = type_
        self._args = args_

    def get_type(self):
        return self._type

    def get_args(self):
        return self._args

    def __str__(self):
        s = ''
        s += self.TYPE[self._type] + ' ( '
        for a in self._args:
            s += str(a) + ' '
        s += ')'
        return s

    __repr__ = __str__

