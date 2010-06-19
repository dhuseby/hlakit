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

class Interrupt(object):
    """
    This defines the base class for all #interrupt lines
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'fn' not in tokens.keys():
            raise ParseFatalException('missing #interrupt parameter')

        return klass(tokens.fn)

    @classmethod
    def exprs(klass):
        kw = Keyword(klass._get_keyword())
        fn = Word(alphas + '_', alphanums + '_').setResultsName('fn')
        expr = Suppress(kw) + \
               fn + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __init__(self, fn):
        self._fn = fn

    def get_fn(self):
        return self._fn

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self._fn)

    __repr__ = __str__


class InterruptStart(Interrupt):
    """
    This defines the rules for parsing a #interrupt.start <fn name> line
    """

    @classmethod
    def _get_keyword(klass):
        return '#interrupt.start'


class InterruptNMI(Interrupt):
    """
    This defines the rules for parsing a #interrupt.nmi <fn name> line
    """

    @classmethod
    def _get_keyword(klass):
        return '#interrupt.nmi'


class InterruptIRQ(Interrupt):
    """
    This defines the rules for parsing a #interrupt.irq <fn name> line
    """

    @classmethod
    def _get_keyword(klass):
        return '#interrupt.irq'


