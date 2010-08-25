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
    
    here's how version 1 headers are defined in the make_lnx code:

    typedef struct
    {
      UBYTE   magic[4];
      UWORD   page_size_bank0;
      UWORD   page_size_bank1;
      UWORD   version;
      char    cartname[32];
      char    manufname[16];
      UBYTE   rotation;
      UBYTE   spare[6];
    }LYNX_HEADER_NEW;

    here's how the proposed version 2 headers are defined:

    typedef struct
    {
      UBYTE   magic[4];
      UBYTE   num_banks;
      UBYTE   use_cart_strobe;
      UWORD   save_game_size;
      UWORD   version;
      char    cartname[32];
      char    manufname[16];
      UBYTE   rotation;
      UBYTE   spare[6];
    }LYNX_HEADER_NEW;

    """

    ROTATE_NONE, ROTATE_LEFT, ROTATE_RIGHT = range(3)

    def __init__(self):
        # version 1 specific
        self._page_size_bank0 = None
        self._page_size_bank1 = None

        # version 2 specific
        self._num_banks = None
        self._use_cart_strobe = None
        self._save_game_size = None

        # common
        self._version = None
        self._cart_name = ''
        self._manufacturer_name = ''
        self._rotation = self.ROTATE_NONE

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


