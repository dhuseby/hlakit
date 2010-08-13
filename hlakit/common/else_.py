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

class Else(object):
    """
    This defines the rules for parsing a #else line in a file
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        # the top of the ignore stack is None if we're nested inside
        # of an ingnored block of code.  we don't do anything in that case.
        if pp.ignore_stack_top() == None:
            return []

        # so we're in an active block of code if we get here so we need
        # to check to see if we're in a block and if so, flip from active
        # to innactive.
        if len(pp.get_ignore_stack()) <= 1:
            raise ParseFatalException("#else outside of #ifdef/#ifndef block")

        # swap states
        ignore = pp.ignore()
        pp.ignore_stack_pop()
        if ignore:
            pp.ignore_stack_push(False)
        else:
            pp.ignore_stack_push(True)

        return []

    @classmethod
    def exprs(klass):
        else_ = Keyword('#else')

        expr = Suppress(else_)
        expr.setParseAction(klass.parse)

        return expr

