"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

from pyparsing import *

class Number(object):
    """
    This is a wrapper class that contains a number token.  Numbers in HLAKit can
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

    def __init__(self, token, value):
        self._token = token
        self._value = value

    def __int__(self):
        return self._value

    def __str__(self):
        return self._token

    def __repr__(self):
        return 'Number(%s) == %d' % (self._token, self._value)

    @classmethod
    def parse(klass, pstring, location, token):
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
        decimal_with_K_ = Combine(Word(nums) + Suppress('K')).setResultsName('decimal_with_k')
        hex_ = Combine(Suppress('0x') + Word(hexnums)).setResultsName('hex')
        asmhex_ = Combine(Suppress('$') + Word(hexnums)).setResultsName('asmhex')
        binary_ = Combine(Suppress('%') + Word('01')).setResultsName('binary')
        true_ = Keyword('true').setResultsName('boolean')
        TRUE_ = Keyword('TRUE').setResultsName('boolean')
        false_ = Keyword('false').setResultsName('boolean')
        FALSE_ = Keyword('FALSE').setResultsName('boolean')
        number_ = hex_ | asmhex_ | binary_ | decimal_with_K_ | decimal_ | true_ | TRUE_ | false_ | FALSE_
        number_.setParseAction(klass.parse)
        return number_

