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

class MOS6502(CPU):

    def __init__(self, options = None, logger = None):

        # init the base class 
        super(MOS6502, self).__init__()

        # store the options object
        self._options = options

        # store the logger
        self._logger = logger

        # initialize the expressions lists
        self._preprocessor_exprs = []

        # CPU specific values for binary generation
        self._start_symbol = None
        self._nmi_symbol = None
        self._irq_symbol = None

        # build the expressions
        self._init_preprocessor_exprs()
        
    def get_preprocessor_exprs(self):
        return self._preprocessor_exprs

    def get_compiler_exprs(self):
        return None

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


