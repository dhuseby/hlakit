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

class LynxRomOrg(object):
    """
    This defines the rules for parsing a #lynx.rom.org <segment>[,counter][,maxsize] 
    line in a file
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'segment' not in tokens.keys():
            raise ParseFatalException('#lynx.rom.org without a segment address')

        segment = tokens.segment
        if not isinstance(segment, NumericValue):
            if not pp.has_symbol(segment):
                raise ParseFatalException('unknown preprocessor symbol: %s' % segment)
            segment = pp.get_symbol(segment)

        counter = None
        if 'counter' in tokens.keys():
            counter = tokens.counter
            if not isinstance(counter, NumericValue):
                if not pp.has_symbol(counter):
                    raise ParseFatalException('unknown preprocessor symbol: %s' % counter)
                counter = pp.get_symbol(counter)

        maxsize = None
        if 'maxsize' in tokens.keys():
            maxsize = tokens.maxsize
            if not isinstance(maxsize, NumericValue):
                if not pp.has_symbol(maxsize):
                    raise ParseFatalException('unknown preprocessor symbol: %s' % maxsize)
                maxsize = pp.get_symbol(maxsize)

        return klass(segment, counter, maxsize)

    @classmethod
    def exprs(klass):
        romorg = Keyword('#rom.org')
        label = Word(alphas + '_', alphanums + '_')
        segment = Or([label, NumericValue.exprs()]).setResultsName('segment')
        counter = Or([label, NumericValue.exprs()]).setResultsName('counter')
        maxsize = Or([label, NumericValue.exprs()]).setResultsName('maxsize')
        
        expr = Suppress(romorg) + \
               segment + \
               Optional(Literal(',') + counter + \
                        Optional(Literal(',') + maxsize))
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, segment, counter=None, maxsize=None):
        if (int(segment) < 0) or (int(segment) > 255):
            raise ParseFatalException('invalid Lynx ROM segment number')
        self._segment = int(segment)

        if counter != None:
            if (int(counter) < 0) or (int(counter) > 2047):
                raise ParseFatalException('invalid Lynx ROM counter number')
            self._counter = int(counter)
        else:
            self._counter = None

        if maxsize != None:
            if int(maxsize) < 0:
                raise ParseFatalException('invalid Lynx ROM maxsize')
            self._maxsize = int(maxsize)
        else:
            self._maxsize = None

    def get_segment(self):
        return self._segment

    def get_counter(self):
        if self._counter:
            return self._counter
        return 0

    def get_maxsize(self):
        return self._maxsize

    def __str__(self):
        s = "LynxRomOrg <0x%x>" % self._segment
        if self._counter != None:
            s += ',<0x%x>' % self._counter
        if self._maxsize != None:
            s += ',<0x%x>' % self._maxsize
        return s

    __repr__ = __str__


