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

class ArrayItem(object):
    """
    Encapsulates an array item
    """
    def __init__(self, item, labels = []):
        self._item = item
        self._labels = labels

    def __len__(self):
        return len(self._item)

    def __str__(self):
        s = ''
        for l in self._labels:
            s += '%s ' % l
        s += '%s' % self._item
        return s

    __repr__ = __str__

class ArrayValue(object):
    """
    Encapsulates an array value
    """
    def __init__(self, items=[], is_string=False):
        self._items = items
        self._string = is_string

    def __len__(self):
        l = 0
        for i in self._items:
            l += len(i)
        return l
    
    def __str__(self):
        s = ''
        if self._string:
            s += '"'
            for i in self._items:
                s += '%s' % i
            s += '"'
        else:
            s += '{ '
            for i in range(0, len(self._items)):
                if i > 0:
                    s += ', '
                s += '%s' % self._items[i]
            s += ' }'

        return s

    __repr__ = __str__

    @classmethod
    def parse_string(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'string' not in tokens.keys():
            raise ParseFatalException('malformed string value')

        s = removeQuotes(pstring, location, tokens)
        s = s.decode('string-escape')

        # convert the string to a list of NumericValue ArrayItems
        items = []
        for i in range(0, len(s)):
            items.append(ArrayItem(NumericValue(s[i], ord(s[i]))))

        # zero terminate the string
        items.append(ArrayItem(NumericValue('\0', 0)))

        return klass(items, True)

    @classmethod
    def parse_item(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        labels = []
        if 'label_list' in tokens.keys():
            labels = [ l for l in tokens.label_list ]
            
        if 'number' in tokens.keys():
            return ArrayItem(tokens.number, labels)

        if 'array' in tokens.keys():
            return ArrayItem(tokens.array, labels)

        if 'string' in tokens.keys():
            return ArrayItem(tokens.string, labels)

        raise ParseFatalException('array item malformed')

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'value' not in tokens.keys():
            raise ParseFatalException('array declaration missing at least one value')

        items = [ tokens.value ]
        if 'value_list' in tokens.keys():
            items.extend([v for v in tokens.value_list])

        return klass(items)

    @classmethod
    def exprs(klass):
        lbrace_ = Suppress('{')
        rbrace_ = Suppress('}')
        string_value = quotedString(Word(printables)).setResultsName('string')
        string_value.setParseAction(klass.parse_string)
        
        array_value = Forward()
        
        label_list = OneOrMore(Label.exprs()).setResultsName('label_list')
        array_item = Optional(label_list) + \
                     (NumericValue.exprs().setResultsName('number') | \
                     string_value | \
                     array_value.setResultsName('array'))
        array_item.setParseAction(klass.parse_item)

        array_value << lbrace_ + \
                       array_item.setResultsName('value') + \
                       ZeroOrMore(Suppress(',') + array_item).setResultsName('value_list') + \
                       rbrace_
        array_value.setParseAction(klass.parse)
        expr = array_value | string_value
        return expr

