"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

import os
from pyparsing import *
from cpu import CPU
from hlakit.number import Number

class Variable(object):
    def __init__(self, type, name, value = None, shared = False, address = None):
        self._type = type
        self._name = name
        self._value = value
        self._shared = shared
        self._address = address

    def set_shared(self, shared):
        self._shared = shared

    def set_value(self, value):
        self._value = value

    def set_address(self, address):
        self._address = address

    def __repr__(self):
        s = 'Variable('
        if self._shared:
            s += 'shared '
        s += self._type + ' '
        s += self._name
        if self._address:
            s += ' @ ' + str(self._address)
        s += ')'
        if self._value:
            s += ' == ' + str(self._value)
        return s

class MOS6502(CPU):

    def __init__(self, options = None, logger = None):

        # init the base class 
        super(MOS6502, self).__init__()

        # store the options object
        self._options = options

        # store the logger
        self._logger = logger

        # initialize the preprocessor expressions lists
        self._preprocessor_exprs = []

        # initialize the compiler expressions list
        self._compiler_exprs = []

        # CPU specific values for binary generation
        self._start_symbol = None
        self._nmi_symbol = None
        self._irq_symbol = None

        # build the preprocessor expressions
        self._init_preprocessor_exprs()

        # build the compiler expressions
        self._init_compiler_exprs()
        
    def get_preprocessor_exprs(self):
        return self._preprocessor_exprs

    def get_compiler_exprs(self):
        return self._compiler_exprs

    def get_file_writer(self):
        # the file writer is the cpu specific binary creator.  
        # in this case it handles converting the 6502 mnemonics
        # into 6502 opcode binary data.
        return None

    def _init_preprocessor_exprs(self):
        # 6502 specific preprocessor directives
        start = Keyword('#interrupt.start')
        nmi = Keyword('#interrupt.nmi')
        irq = Keyword('#interrupt.irq')

        # define the value
        value = Word(printables).setResultsName('value')

        # start interrupt line
        start_line = Suppress(start) + \
                     value + \
                     Suppress(LineEnd())
        start_line.setParseAction(self._start_line)

        # nmi interrupt line
        nmi_line = Suppress(nmi) + \
                   value + \
                   Suppress(LineEnd())
        nmi_line.setParseAction(self._nmi_line)

        # irq interrupt line
        irq_line = Suppress(irq) + \
                   value + \
                   Suppress(LineEnd())
        irq_line.setParseAction(self._irq_line)

        # put the expressions in the top level map
        self._preprocessor_exprs.append(('start_line', start_line))
        self._preprocessor_exprs.append(('nmi_line', nmi_line))
        self._preprocessor_exprs.append(('irq_line', irq_line))

    def _init_compiler_exprs(self):

        ### variable declarations ###
       
        # numbers
        number_ = Number.exprs()

        # keywords
        shared_ = Keyword('shared')
        typedef_ = Keyword('typedef')

        # name
        name_ = Word(alphas, alphanums + '_')

        # types
        byte_ = Keyword('byte')
        BYTE_ = Keyword('BYTE')
        char_ = Keyword('char')
        CHAR_ = Keyword('CHAR')
        bool_ = Keyword('bool')
        BOOL_ = Keyword('BOOL')
        word_ = Keyword('word')
        WORD_ = Keyword('WORD')
        pointer_ = Keyword('pointer')
        POINTER_ = Keyword('POINTER')
        type_ = byte_ | BYTE_ | char_ | CHAR_ | bool_ | BOOL_ | word_ | WORD_ | pointer_ | POINTER_
        #struct_ = Combine(Suppress(Keyword('struct')) + name_).setResultsName('type')

        # punctuation
        equal_ = Suppress('=')
        colon_ = Suppress(':')
        lbrace = Suppress('{')
        rbrace = Suppress('}')
        lbracket = Suppress('[')
        rbracket = Suppress(']')

        # simple variable
        simple_variable_ = type_.setResultsName('type') + \
            Group(name_ + Optional(ZeroOrMore(Suppress(',') + name_))).setResultsName('names')
        simple_variable_.setParseAction(self._simple_variable)

        # full variable
        variable_ = Optional(shared_.setResultsName('shared')) + \
                    Group(simple_variable_).setResultsName('vars') + \
                    Optional(colon_ + number_.setResultsName('address')) + \
                    Optional(equal_ + number_.setResultsName('value'))
        variable_.setParseAction(self._variable)

        # array
        #varlist_ = OneOrMore(type_ + name_
        #array_ = Optional(shared_.setResultsName('shared')) + \
        #         type_.setResultsName('type') + \
        #         name_.setResultsName('name') + \
        #         lbracket + \
        #         Optional(number_.setResultsName('size')) + \
        #         rbracket + \
        #         Optional(colon_ + number_.setResultsName('address')) + \
        #         equal_ + \
        #         lbrace + \


        # put the expressions in the compiler exprs
        self._compiler_exprs.append(('variable', variable_))

    #
    # Parse Action Callbacks
    #

    def _start_line(self, pstring, location, tokens):
        if len(tokens.value) == 0:
            raise ParseFatalException('#interrupt.start must have exactly 1 argument')

        self._start_symbol = tokens.value

        return []

    def _nmi_line(self, pstring, location, tokens):
        if len(tokens.value) == 0:
            raise ParseFatalException('#interrupt.nmi must have exactly 1 argument')

        self._nmi_symbol = tokens.value

        return []

    def _irq_line(self, pstring, location, tokens):
        if len(tokens.value) == 0:
            raise ParseFatalException('#interrupt.irq must have exactly 1 argument')

        self._irq_symbol = tokens.value

        return []

    def _variable(self, pstring, location, tokens):
        shared = False
        if len(tokens.shared):
            shared = True
        value = None
        if bool(tokens.value):
            value = tokens.value
        address = None
        if bool(tokens.address):
            address = tokens.address

        if (len(tokens.vars) > 1) and address:
            raise ParseFatalException('cannot assign address to multi-variable declaration')
        if (len(tokens.vars) > 1) and value:
            raise ParseFatalException('cannot assign value to multi-variable declaration')

        # set the attributes of the single variable
        if len(tokens.vars) == 1:
            var = tokens.var[0]
            var.set_shared(shared)
            var.set_value(value)
            var.set_address(address)
            return var

        # set the shared attribute on all of the variables
        toks = []
        for var in tokens.vars:
            var.set_shared(shared)
            toks.append(var)
        return toks

    def _simple_variable(self, pstring, location, tokens):
        # build the list of variables to return
        import pdb; pdb.set_trace()
        toks = []
        for name in tokens.names:
            toks.append(Variable(tokens.type, name))
        return toks
