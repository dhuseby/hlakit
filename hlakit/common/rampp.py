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
from hlakit.common.session import Session
from hlakit.common.numericvalue import NumericValue

class RamOrg(object):
    """
    This defines the rules for parsing a #ram.org <blockaddress>[,maxsize] line 
    in a file
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'address' not in tokens.keys():
            raise ParseFatalException('#rom.org without an address')
        
        address = tokens.address
        if not isinstance(address, NumericValue):
            if not pp.has_symbol(address):
                raise ParseFatalException('unknown preprocessor symbol: %s' % address)
            address = NumericValue(pp.get_symbol(address))

        maxsize = None
        if 'maxsize' in tokens.keys():
            maxsize = tokens.maxsize
        if maxsize is not None:
            if not isinstance(maxsize, NumericValue):
                if not pp.has_symbol(maxsize):
                    raise ParseFatalException('unknown preprocessor symbol: %s' % maxsize)
                maxsize = pp.get_symbol(maxsize)

        return klass(address, maxsize)

    @classmethod
    def exprs(klass):
        ramorg = Keyword('#ram.org')
        label = Word(alphas + '_', alphanums + '_')
        address = Or([label, NumericValue.exprs()]).setResultsName('address')
        maxsize = Or([label, NumericValue.exprs()]).setResultsName('maxsize')

        expr = Suppress(ramorg) + \
               address + \
               Optional(Literal(',') + maxsize)
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, address, maxsize=None):
        self._address = int(address)
        if maxsize != None:
            if int(maxsize) < 0:
                raise ParseFatalException('invalid RAM maxsize')
            self._maxsize = int(maxsize)
        else:
            self._maxsize = None

    def get_address(self):
        return self._address

    def get_maxsize(self):
        return self._maxsize

    def __str__(self):
        s = "RamOrg <0x%x>" % self._address
        if self._maxsize != None:
            s += ',<0x%x>' % self._maxsize
        return s

    __repr__ = __str__


class RamEnd(object):
    """
    This defines the rules for parsing a #ram.end line in a file
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        return klass()

    @classmethod
    def exprs(klass):
        ramorg = Keyword('#ram.end')
        expr = Suppress(ramorg) + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __str__(self):
        return 'RamEnd'

    __repr__ = __str__

