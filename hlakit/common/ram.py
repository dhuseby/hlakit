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

        if not hasattr(tokens, 'address'):
            raise ParseFatalException('#ram.org without an address')

        maxsize = getattr(tokens, 'maxsize', None)

        return klass(tokens.address, maxsize)

    @classmethod
    def exprs(klass):
        ramorg = Keyword('#ram.org')
        address = NumericValue.exprs().setResultsName('address')
        maxsize = NumericValue.exprs().setResultsName('maxsize')

        expr = Suppress(ramorg) + \
               address + \
               Optional(Literal(',') + maxsize) + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, address, maxsize=None):
        self._address = address
        self._maxsize = maxsize

    def get_address(self):
        return self._address

    def get_maxsize(self):
        return self._maxsize

    def __str__(self):
        s = "RamOrg <0x%x>" % self._address
        if self._maxsize:
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

