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
from struct import Struct
from arrayvalue import ArrayValue, StringValue
from keywordoperator import KeywordOperator
from maskparameter import MaskParameter

class Lo(KeywordOperator):
    """
    The lo() keyword operator
    """

    @classmethod
    def _get_keyword(klass):
        return 'lo'

    @classmethod
    def _get_param(klass):
        return MaskParameter.exprs()

    def __init__(self, param):
        if isinstance(param, Struct) or \
           isinstance(param, ArrayValue) or \
           isinstance(param, StringValue):
               raise ParseFatalError('invalid parameter for lo() operator')

        super(Lo, self).__init__(param)

    def __int__(self):
        # TODO: look up the varaible and return the masked value
        return 0

    def __str__(self):
        return 'lo(%s)' % self.get_symbol() or self.get_value()

    __repr__ = __str__

