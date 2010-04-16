"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""
from pyparsing import *

class Label(object):
    """
    encapsulates a label
    """
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return '%s:' % self._name

    __repr__ = __str__

    @classmethod
    def parse(klass, pstring, location, tokens):
        if 'label' not in tokens.keys():
            raise ParseFatalException('label missing name')

        return Label(tokens.label)

    @classmethod
    def exprs(klass):
        label_ = Word(alphas, alphanums + '_').setResultsName('label') + Suppress(':')
        label_.setParseAction(klass.parse)
        return label_

class Value(object):
    """
    value base class
    """
    @classmethod
    def parse(klass, pstring, location, tokens):
        if 'number' in tokens.keys():
            return tokens.number
        elif 'array' in tokens.keys():
            return tokens.array

        raise ParseFatalException('unrecognized value expression')

    @classmethod
    def exprs(klass):
        value_ = NumericValue.exprs().setResultsName('number') | \
                 ArrayValue.exprs().setResultsName('array')
        value_.setParseAction(klass.parse)
        return value_

class NumericValue(Value):
    """
    Encapsulates a numeric value. Numbers in HLAKit can
    be specified with in many different ways:

    decimal:
        100
        2K      <-- the K means "kilo" and multiplies the number by 1024

    hexidecimal:
        0x1A30
        $1A30

    binary:
        %11011011

    """

    def __init__(self, token, value):
        self._token = token
        self._value = value

    def __len__(self):
        return 1

    def __int__(self):
        return self._value

    def __str__(self):
        return self._token

    def __repr__(self):
        return 'Number(%s) == %d' % (self._token, self._value)

    @classmethod
    def parse(klass, pstring, location, token):
        # figure out which type of number we got
        if len(token.decimal):
            return klass(token.decimal, int(token.decimal, 10))
        elif len(token.decimal_with_k):
            value = int(token.decimal_with_k, 10) * 1024
            return klass(token.decimal_with_k + 'K', value)
        elif len(token.hex):
            return klass('0x' + token.hex, int(token.hex, 16))
        elif len(token.asmhex):
            return klass('$' + token.asmhex, int(token.asmhex, 16))
        elif len(token.binary):
            return klass('%' + token.binary, int(token.binary, 2))
        elif len(token.boolean):
            value = 0
            if token.boolean.lower() == 'true':
                value = 1
            return klass(token.boolean, value)
           
        raise ParseFatalException('number value with none of the expected attributes')

    @classmethod
    def exprs(klass):
        decimal_ = Word(nums).setResultsName('decimal')
        decimal_with_K_ = Combine(Word(nums) + Suppress('K')).setResultsName('decimal_with_k')
        hex_ = Combine(Suppress('0x') + Word(hexnums)).setResultsName('hex')
        asmhex_ = Combine(Suppress('$') + Word(hexnums)).setResultsName('asmhex')
        binary_ = Combine(Suppress('%') + Word('01')).setResultsName('binary')
        true_ = Keyword('true').setResultsName('boolean')
        TRUE_ = Keyword('TRUE').setResultsName('boolean')
        false_ = Keyword('false').setResultsName('boolean')
        FALSE_ = Keyword('FALSE').setResultsName('boolean')
        number_ = hex_ | asmhex_ | binary_ | decimal_with_K_ | \
                  decimal_ | true_ | TRUE_ | false_ | FALSE_
        number_.setParseAction(klass.parse)
        return number_

class ArrayItem(Value):
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

class ArrayValue(Value):
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
            for i in range(0, len(self._items)):
                if i > 0:
                    s += ', '
                s += '%s' % self._items[i]

        return s

    __repr__ = __str__

    @classmethod
    def parse_string(klass, pstring, location, tokens):
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

        return ArrayValue(items, True)

    @classmethod
    def parse_item(klass, pstring, location, tokens):
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

        if 'value' not in tokens.keys():
            raise ParseFatalException('array declaration missing at least one value')

        items = [ tokens.value ]
        if 'value_list' in tokens.keys():
            items.extend([v for v in tokens.value_list])

        return ArrayValue(items)

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
        value_ = array_value | string_value
        return value_

