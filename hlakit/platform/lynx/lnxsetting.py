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
from hlakit.common.arrayvalue import StringValue

class bind1(object):

    def __init__(self, fn, type):
        self._fn = fn
        self._type = type

    def get_type(self):
        return self._type

    def __call__(self, pstring, location, tokens):
        return self._fn(pstring, location, tokens, self._type)

class LnxSetting(object):
    """
    This defines the rules for parsing a #lnx.* preprocessor settings
    """

    OFF, PSB0, PSB1, VERSION, CART_NAME, MANU_NAME, ROTATION = range(7)
    TYPE = [ 'off', 'page_size_bank0', 'page_size_bank1', 'version',
             'cart_name', 'manufacturer_name', 'rotation' ]
    KEYNAMES = [ None, 'size', 'size', 'version', 'cname', 'mname', 'rotation' ]

    @classmethod
    def get_numeric_parameter(klass, tokens, keyname):
        pp = Session().preprocessor() 
        if keyname not in tokens.keys():
            raise ParseFatalException('#lnx.* missing %s' % keyname)

        value = getattr(tokens, keyname)
        if not isinstance(value, NumericValue):
            if not pp.has_symbol(value):
                raise ParseFatalException('unknown preprocessor symbol: %s' % value)
            value = pp.get_symbol(value)

        return value

    @classmethod
    def get_string_parameter(klass, tokens, keyname):
        pp = Session().preprocessor() 
        if keyname not in tokens.keys():
            raise ParseFatalException('#lnx.* missing %s' % keyname)

        value = getattr(tokens, keyname)
        if not isinstance(value, StringValue):
            if not pp.has_symbol(value):
                raise ParseFatalException('unknown preprocessor symbol: %s' % value)
            value = pp.get_symbol(value)

        return value

    @classmethod
    def parse(klass, pstring, location, tokens, type_):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if type_ == klass.OFF:
            return klass(type_)
        
        elif type_ in (klass.PSB0, klass.PSB1, klass.VERSION):
            return klass(type_, klass.get_numeric_parameter(tokens, klass.KEYNAMES[type_]))

        elif type_ in (klass.CART_NAME, klass.MANU_NAME, klass.ROTATION):
            return klass(type_, klass.get_string_parameter(tokens, klass.KEYNAMES[type_]))

        raise ParseFatalException('invalid #lnx expression')

    @classmethod
    def exprs(klass):
        label = Word(alphas + '_', alphanums + '_')

        #lnx.off
        off = Suppress(Keyword('#lnx.off'))
        off.setParseAction(bind1(klass.parse, klass.OFF))

        #lnx.page_size_bank0 <value>
        psb0 = Suppress(Keyword('#lnx.page_size_bank0')) + \
               Or([label, NumericValue.exprs()]).setResultsName('size')
        psb0.setParseAction(bind1(klass.parse, klass.PSB0))

        #lnx.page_size_bank1 <value>
        psb1 = Suppress(Keyword('#lnx.page_size_bank1')) + \
               Or([label, NumericValue.exprs()]).setResultsName('size')
        psb1.setParseAction(bind1(klass.parse, klass.PSB1))

        #lnx.version <value>
        ver = Suppress(Keyword('#lnx.version')) + \
               Or([label, NumericValue.exprs()]).setResultsName('version')
        ver.setParseAction(bind1(klass.parse, klass.VERSION))

        #lnx.cart_name <string value>
        cname = Suppress(Keyword('#lnx.cart_name')) + \
               Or([label, StringValue.exprs()]).setResultsName('cname')
        cname.setParseAction(bind1(klass.parse, klass.CART_NAME))

        #lnx.manufacturer_name <string value>
        mname = Suppress(Keyword('#lnx.manufacturer_name')) + \
               Or([label, StringValue.exprs()]).setResultsName('mname')
        mname.setParseAction(bind1(klass.parse, klass.MANU_NAME))

        #lnx.rotation <string value>
        rot = Suppress(Keyword('#lnx.rotation')) + \
               Or([label, StringValue.exprs()]).setResultsName('rotation')
        rot.setParseAction(bind1(klass.parse, klass.ROTATION))

        expr = MatchFirst([off, psb0, psb1, ver, cname, mname, rot])

        return expr


    def __init__(self, type_, *args_):
        self._type = type_

        self._size = None
        self._version = None
        self._name = None
        self._rotation = None

        if type_ in (self.PSB0, self.PSB1):
            self._size = args_[0]
        elif type_ == self.VERSION:
            self._version = args_[0]
        elif type_ in (self.CART_NAME, self.MANU_NAME):
            self._name = args_[0]
        elif type_ == self.ROTATION:
            self._rotation = args_[0]

    def get_type(self):
        return self._type

    def get_size(self):
        return self._size

    def get_version(self):
        return self._version

    def get_name(self):
        return self._name

    def get_rotation(self):
        return self._rotation

    def __str__(self):
        s_ = '#lnx.%s' % self.TYPE[self._type]
        if self._size:
            s_ += ' %s' % self._size
        elif self._version:
            s_ += ' %s' % str(self._version)
        elif self._name:
            s_ += ' "%s"' % self._name
        elif self._rotation: 
            s_ += ' %s' % self._rotation
        return s_

    __repr__ = __str__


