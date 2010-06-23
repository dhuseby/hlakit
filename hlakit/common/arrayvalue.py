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
from label import Label
from numericvalue import NumericValue

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

        if 'array_' in tokens.keys():
            return ArrayItem(tokens.array, labels)

        if 'string_' in tokens.keys():
            return ArrayItem(tokens.string_, labels)

        raise ParseFatalException('array item malformed')

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        items = []
        if 'value_list' in tokens.keys():
            items.extend([v for v in tokens.value_list])

        return klass(items)

    @classmethod
    def exprs(klass):
        lbrace_ = Suppress('{')
        rbrace_ = Suppress('}')
        
        array_value = Forward()
        
        label_list = OneOrMore(Label.exprs()).setResultsName('label_list')
        array_item = Optional(label_list) + \
                     (NumericValue.exprs().setResultsName('number') | \
                     StringValue.exprs().setResultsName('string_') | \
                     array_value.setResultsName('array_'))
        array_item.setParseAction(klass.parse_item)

        array_value << lbrace_ + \
                       delimitedList(array_item).setResultsName('value_list') + \
                       rbrace_
        array_value.setParseAction(klass.parse)
        expr = array_value | StringValue.exprs()
        return expr

    def __init__(self, items=[]):
        self._items = items

    def __len__(self):
        l = 0
        for i in self._items:
            l += len(i)
        return l
    
    def __str__(self):
        s = '{ '
        for i in range(0, len(self._items)):
            if i > 0:
                s += ', '
            s += '%s' % self._items[i]
        s += ' }'
        return s

    __repr__ = __str__


class StringValue(ArrayValue):
    """
    Encapsulates a string value.
    """

    @classmethod
    def parse(klass, pstring, location, tokens):
        pp = Session().preprocessor()

        if pp.ignore():
            return []

        if 'string_' not in tokens.keys():
            raise ParseFatalException('malformed string value')

        s = removeQuotes(pstring, location, tokens)
        s = s.decode('string-escape')

        # convert the string to a list of NumericValue ArrayItems
        items = []
        for i in range(0, len(s)):
            items.append(ArrayItem(NumericValue(s[i], ord(s[i]))))

        return klass(items)

    @classmethod
    def exprs(klass):
        expr = quotedString(Word(printables)).setResultsName('string_')
        expr.setParseAction(klass.parse)
        return expr

    def __init__(self, value):
        self._value = value

    def __str__(self):
        return ''.join([str(item) for item in self._value])

    def __repr__(self):
        return 'String("%s")' % self._value



