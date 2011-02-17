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

from math import ceil,log
from pyparsing import *
from session import Session

class NumericValue(object):
    """
    Encapsulates a numeric value. Numbers in HLAKit can
    be specified with in many different ways:

    decimal:
        100
        2K      <-- the K means "kilo" and multiplies the number by 1024

    hexidecimal:
        0x1A30
        $1A30

    binary:
        %11011011

    """

    @classmethod
    def parse(klass, pstring, location, token):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        # figure out which type of number we got
        if len(token.decimal):
            return klass(token.decimal, int(token.decimal, 10))
        elif len(token.decimal_with_k):
            value = int(token.decimal_with_k, 10) * 1024
            return klass(token.decimal_with_k + 'K', value)
        elif len(token.hex):
            return klass('0x' + token.hex, int(token.hex, 16))
        elif len(token.asmhex):
            return klass('$' + token.asmhex, int(token.asmhex, 16))
        elif len(token.binary):
            return klass('%' + token.binary, int(token.binary, 2))
        elif len(token.boolean):
            value = 0
            if token.boolean.lower() == 'true':
                value = 1
            return klass(token.boolean, value)
           
        raise ParseFatalException('number value with none of the expected attributes')

    @classmethod
    def exprs(klass):
        decimal_ = Word(nums).setResultsName('decimal')
        decimal_with_K_ = Combine(Word(nums) + Suppress(CaselessLiteral('K'))).setResultsName('decimal_with_k')
        hex_ = Combine(Suppress('0x') + Word(hexnums)).setResultsName('hex')
        asmhex_ = Combine(Suppress('$') + Word(hexnums)).setResultsName('asmhex')
        binary_ = Combine(Suppress('%') + Word('01')).setResultsName('binary')
        true_ = Keyword('true').setResultsName('boolean')
        TRUE_ = Keyword('TRUE').setResultsName('boolean')
        false_ = Keyword('false').setResultsName('boolean')
        FALSE_ = Keyword('FALSE').setResultsName('boolean')
        number_ = hex_ | asmhex_ | binary_ | decimal_with_K_ | \
                  decimal_ | true_ | TRUE_ | false_ | FALSE_
        number_.setParseAction(klass.parse)
        return number_

    def __init__(self, token, value=None):
        if token is None:
            raise ValueError('NumericValue parameter 1 cannot be None')

        self._token = token
        if value is None:
            # try to parse the value
            if token[0] == '$':
                value = int(token[1:], 16)
            elif token[0] == '%':
                value = int(token[1:], 2)
            elif token[0:2].lower() == '0x':
                value = int(token[2:], 16)
            elif token[-1].upper() == 'K':
                value = int(token[0:-1], 10) * 1024
            else:
                value = int(token, 10)

        self._value = value

    def resolve(self):
        return self

    def __len__(self):
        """ return the number of bytes needed to store this value """
        v = int(self._value)
        if v == 0:
            return 1
        return int(ceil(ceil(log(v) / log(2)) / 8))

    def __eq__(self, rhs):
        v = rhs
        if isinstance(rhs, NumericValue):
            v = rhs._value

        return (self._value == v)

    def __ne__(self, rhs):
        v = rhs
        if isinstance(rhs, NumericValue):
            v = rhs._value

        return (self._value != v)

    def __gt__(self, rhs):
        v = rhs
        if isinstance(rhs, NumericValue):
            v = rhs._value

        return (self._value > v)

    def __ge__(self, rhs):
        v = rhs
        if isinstance(rhs, NumericValue):
            v = rhs._value

        return (self._value >= v)

    def __lt__(self, rhs):
        v = rhs
        if isinstance(rhs, NumericValue):
            v = rhs._value

        return (self._value < v)

    def __le__(self, rhs):
        v = rhs
        if isinstance(rhs, NumericValue):
            v = rhs._value

        return (self._value <= v)

    def __cmp__(self, rhs):
        v = rhs
        if isinstance(rhs, NumericValue):
            v = rhs._value

        if self._value < v:
            return -1
        elif self._value == v:
            return 0
        else:
            return 1

    def __int__(self):
        return int(self._value)

    def __str__(self):
        return self._token

    def __nonzero__(self):
        return self.__int__() != 0

    def __repr__(self):
        return 'Number(%s) == %d' % (self._token, self._value)

