"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

from values import *

class SetPad(object):
    """
    Token for setting the current padding contents
    """
    def __init__(self, padding):
        self._padding = padding

    def get_padding(self):
        return self._padding

    def __str__(self):
        return "<%s>" % self._padding

    __repr__ = __str__

class SetAlign(object):
    """
    Token for setting the current alignment value
    """
    def __init__(self, alignment):
        self._alignment = alignment

    def get_alignement(self):
        return self._alignment

    def __str__(self):
        return "<0x%x>" % self._alignment

    __repr__ = __str__

class AssignValue(object):
    """
    encapsulates an assignment AST
    """
    def __init__(self, lhs, rhs):
        self._lhs = lhs
        self._rhs = rhs

        if isinstance(self._rhs, ArrayValue):
            self._lhs.set_array_size(len(self._rhs))

    def __str__(self):
        return '%s = %s' % (self._lhs, self._rhs)

    __repr__ = __str__


