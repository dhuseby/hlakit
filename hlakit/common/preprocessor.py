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

import os
import sys
from pyparsing import *
from define import Define
from undef import Undef
from ifdef import Ifdef
from ifndef import Ifndef
from else_ import Else
from endif import Endif
from todo import Todo
from warning import Warning
from error import Error
from tell import TellBank, TellBankOffset, TellBankSize, TellBankFree, TellBankType
from include import Include
from incbin import Incbin
from usepath import Usepath
from rom import RomOrg, RomEnd, RomBanksize, RomBank
from ram import RamOrg, RamEnd
from setpad import SetPad
from align import Align
from codeline import CodeLine
from codeblock import CodeBlock
from filemarkers import FileBegin, FileEnd

class Preprocessor(object):
    
    FILE_NAME_CHARS = '0123456789' + \
                      'abcdefghijklmnopqrstuvwxyz' + \
                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
                      '!"#$%&\\\'()*+,-./:;=?@[]^_`{|}~'

    class StateFrame(object):
        """
        Helper class that holds an entire state frame
        """
        def __init__(self, f, exprs):
            # the current file name
            self._file = f

            # initialize the pyparsing parser as ZeroOrMore(Or())
            # of all of the expressions 
            expr_or = Or([])
            for e in exprs:
                expr_or.append(e[1])
           
            # build final parser
            self._parser = ZeroOrMore(expr_or)

            # add in comment ignoring
            self._parser.ignore(cStyleComment | cppStyleComment)

        def parse(self):
            tokens = self._parser.parseFile(self._file, parseAll=True)
            return tokens

        def get_file_path(self):
            return getattr(self._file, 'name', None)

    @classmethod
    def exprs(klass):
        e = []
        e.extend(klass.first_exprs())
        e.extend(klass.last_exprs())
        return e

    @classmethod
    def first_exprs(klass):
        e = []
        e.append(('define', Define.exprs()))
        e.append(('undef', Undef.exprs()))
        e.append(('ifdef', Ifdef.exprs()))
        e.append(('ifndef', Ifndef.exprs()))
        e.append(('else', Else.exprs()))
        e.append(('endif', Endif.exprs()))
        e.append(('todo', Todo.exprs()))
        e.append(('warning', Warning.exprs()))
        e.append(('error', Error.exprs()))
        e.append(('tellbank', TellBank.exprs()))
        e.append(('tellbankoffset', TellBankOffset.exprs()))
        e.append(('tellbanksize', TellBankSize.exprs()))
        e.append(('tellbankfree', TellBankFree.exprs()))
        e.append(('tellbanktype', TellBankType.exprs()))
        e.append(('include', Include.exprs()))
        e.append(('incbin', Incbin.exprs()))
        e.append(('usepath', Usepath.exprs()))
        e.append(('romorg', RomOrg.exprs()))
        e.append(('romend', RomEnd.exprs()))
        e.append(('rombanksize', RomBanksize.exprs()))
        e.append(('rombank', RomBank.exprs()))
        e.append(('ramorg', RamOrg.exprs()))
        e.append(('ramend', RamEnd.exprs()))
        e.append(('setpad', SetPad.exprs()))
        e.append(('align', Align.exprs()))
        return e

    @classmethod
    def last_exprs(klass):
        e = []
        e.append(('codeline', CodeLine.exprs()))
        return e

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def __init__(self):
        if not hasattr(self, '_exprs'):
            self.set_exprs(self.__class__.exprs())
        if not hasattr(self, '_symbols'):
            self._symbols = {}
        if not hasattr(self, '_ignore_stack'):
            self._ignore_stack = [False]
        if not hasattr(self, '_state_stack'):
            self._state_stack = []
        if not hasattr(self, '_tokens'):
            self._tokens = []

    def reset_state(self):
        self.set_exprs(self.__class__.exprs())
        self._symbols = {}
        self._ignore_stack = [False]
        self._state_stack = []
        self._tokens = []

    def get_exprs(self):
        return self._exprs

    def set_exprs(self, value):
        self._exprs = value

    def _get_tokens(self):
        return self._tokens

    def _append_tokens(self, tokens):
        self._tokens.extend(tokens)

    def get_symbols(self):
        return self._symbols

    def set_symbol(self, label, value = None):
        self._symbols[label] = value

    def get_symbol(self, label):
        return self.get_symbols().get(label, None)

    def has_symbol(self, label):
        return self.get_symbols().has_key(label)

    def delete_symbol(self, label):
        self.get_symbols().pop(label, None)     

    def expand_symbols(self, line):
        expanded_line = line
        for (symbol, value) in self.get_symbols().iteritems():
            if value == None:
                value = ''
            expanded_line = expanded_line.replace(symbol, value)
        return expanded_line

    def get_ignore_stack(self):
        return self._ignore_stack

    def ignore_stack_push(self, value):
        self._ignore_stack.append(value)

    def ignore_stack_pop(self):
        return self._ignore_stack.pop()

    def ignore_stack_top(self):
        return self.get_ignore_stack()[-1]

    def ignore(self):
        if self.get_ignore_stack()[-1] == True or \
           self.get_ignore_stack()[-1] == None:
            return True
        return False
    
    def get_state_stack(self):
        return self._state_stack

    def state_stack_push(self, frame):

        self._state_stack.append(frame)

    def state_stack_pop(self):
        return self._state_stack.pop()

    def state_stack_top(self):
        if len(self.get_state_stack()):
            return self.get_state_stack()[-1]
        return None

    def parse(self, f):
        # inject file begin token
        fname = getattr(f, 'name', 'DummyFile')
        self._append_tokens([FileBegin(fname)])

        # set up a new context
        self.state_stack_push(Preprocessor.StateFrame(f, self.get_exprs()))

        # do the parse
        tokens = self.state_stack_top().parse()
        if len(tokens):
            self._append_tokens(tokens)
 
        # restore previous state if there is one
        self.state_stack_pop()

        # inject file begin token
        self._append_tokens([FileEnd(fname)])

    def get_output(self):
        # get the tokens 
        tokens = self._get_tokens()

        # it's time to merge un-processed lines into code blocks for
        # parsing by the compiler pass.
        pp_tokens = []
        current_block = CodeBlock([])
        for token in tokens:
            if isinstance(token, CodeLine):
                current_block.append(token)
            else:
                # if the current code block has lines in it, then
                # push it into the pp_tokens list and start a new
                # CodeBlock...
                if current_block.num_lines() > 0:
                    pp_tokens.append(current_block)
                    current_block = CodeBlock([])

                # append the non-CodeLine token to the pp_tokens list
                pp_tokens.append(token)

        # make sure we append the last code block
        if current_block.num_lines() > 0:
            pp_tokens.append(current_block)

        # the output here is a list of tokens like CodeBlock, IncBin, CodeBlock etc
        # that way the compiler can translate each CodeBlock into a series of tokens
        # that the linker and code generator can understand.
        return pp_tokens
    

