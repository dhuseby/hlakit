"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

from pyparsing import *
from hlakit.common.session import Session
from hlakit.common.numericvalue import NumericValue

class Lnx(object):
    """
    This class encapsulates the .lnx header that will be written with
    the ROM image.
    """

    def __init__(self):
        pass

    def __str__(self):
        pass


class LnxOff(object):
    """
    This defines the rules for parsing a #lnx.off line 
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        return klass()

    @classmethod
    def exprs(klass):
        kw = Keyword('#lnx.off')

        expr = Suppress(kw) + \
               Suppress(LineEnd())
        expr.setParseAction(klass.parse)

        return expr

    def __str__(self):
        return 'LnxOff'

    __repr__ = __str__


