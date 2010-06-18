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
from include import Include
from incbin import Incbin
from codeline import CodeLine
from codeblock import CodeBlock

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

        def parse(self):
            return self._parser.parseFile(self._file, parseAll=True)

        def get_file_path(self):
            return getattr(self._file, 'path', None)

    @classmethod
    def exprs(klass):
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
        e.append(('include', Include.exprs()))
        e.append(('incbin', Incbin.exprs()))
        e.append(('codeline', CodeLine.exprs()))
        return e

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def __init__(self):
        self.set_exprs(Preprocessor.exprs())

    def reset_state(self):
        self.set_exprs(Preprocessor.exprs())
        self._symbols = {}
        self._ignore_stack = [False]
        self._state_stack = []

    def get_exprs(self):
        return getattr(self, '_exprs', [])

    def set_exprs(self, value):
        self._exprs = value

    def _get_tokens(self):
        return getattr(self, '_tokens', [])

    def _append_tokens(self, tokens):
        if not hasattr(self, '_tokens'):
            self._tokens = []
        self._tokens.append(tokens)

    def get_symbols(self):
        return getattr(self, '_symbols', {})

    def set_symbol(self, label, value = None):
        if not hasattr(self, '_symbols'):
            self._symbols = {}
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
        return getattr(self, '_ignore_stack', [False])

    def ignore_stack_push(self, value):
        if not hasattr(self, '_ignore_stack'):
            self._ignore_stack = [False]
        self._ignore_stack.append(value)

    def ignore_stack_pop(self):
        if not hasattr(self, '_ignore_stack'):
            self._ignore_stack = [False]
        return self._ignore_stack.pop()

    def ignore_stack_top(self):
        return self.get_ignore_stack()[-1]

    def ignore(self):
        if self.get_ignore_stack()[-1] == True or \
           self.get_ignore_stack()[-1] == None:
            return True
        return False
    
    def get_state_stack(self):
        return getattr(self, '_state_stack', [])

    def state_stack_push(self, frame):
        if not hasattr(self, '_state_stack'):
            self._state_stack = []
        self._state_stack.append(frame)

    def state_stack_pop(self):
        if not hasattr(self, '_state_stack'):
            self._state_stack = []
        return self._state_stack.pop()

    def state_stack_top(self):
        if len(self.get_state_stack()):
            return self.get_state_stack()[-1]
        return None

    def parse(self, f):
        # set up a new context
        self.state_stack_push(Preprocessor.StateFrame(f, self.get_exprs()))

        # do the parse
        self._append_tokens(self.state_stack_top().parse())

        # restore previous state if there is one
        self.state_stack_pop()

    def get_output(self):
        # get the tokens 
        tokens = self._get_tokens()

        # it's time to merge un-processed lines into code blocks for
        # parsing by the compiler pass.
        pp_tokens = []
        current_block = CodeBlock()
        for token in tokens:
            if type(token) is CodeLine:
                current_block.append(token)
            else:
                # if the current code block has lines in it, then
                # push it into the pp_tokens list and start a new
                # CodeBlock...
                if current_block.num_lines() > 0:
                    pp_tokens.append(current_block)
                    current_block = CodeBlock()

                # append the non-CodeLine token to the pp_tokens list
                pp_tokens.append(token)

        # make sure we append the last code block
        if current_block.num_lines() > 0:
            pp_tokens.append(current_block)

        # the output here is a list of tokens like CodeBlock, IncBin, CodeBlock etc
        # that way the compiler can translate each CodeBlock into a series of tokens
        # that the linker and code generator can understand.
        return pp_tokens
    
'''
    def _init_preprocessor_exprs(self):
        self._init_files_exprs()
        self._init_memory_exprs()

    def _init_files_exprs(self):
        
        # define label
        label = Word(alphas + '_', alphanums + '_').setResultsName('label')

        # define include and incbin literals
        include = Keyword('#include')
        incbin = Keyword('#incbin')

        # ==> #include "foo.h"

        # define a quoted file path 
        literal_file_path = quotedString(Word(Preprocessor.FILE_NAME_CHARS))
        literal_file_path.setParseAction(removeQuotes)
        literal_file_path = literal_file_path.setResultsName('file_path')

        # define a literal include line
        literal_include_line = Suppress(include) + literal_file_path + Suppress(LineEnd())
        literal_include_line.setParseAction(self._include_literal_file)

        # ==> #include <foo.h>

        # define an angle bracketed file path
        implied_file_path = Suppress(Literal('<')) + \
                            Word(Preprocessor.FILE_NAME_CHARS).setResultsName('file_path') + \
                            Suppress(Literal('>'))
        #implied_file_path = implied_file_path.setResultsName('file_path')
        
        # define an implied include line
        implied_include_line = Suppress(include) + implied_file_path + Suppress(LineEnd())
        implied_include_line.setParseAction(self._include_implied_file)

        # ==> #incbin "foo.bin"
        literal_incbin_line = Suppress(incbin) + literal_file_path + Suppress(LineEnd())
        literal_incbin_line.setParseAction(self._include_literal_incbin)

        # ==> sprite_pal: #incbin "palettes/spr_pal0.pal"
        symbol_incbin_line = label + \
                             Suppress(':') + \
                             Suppress(incbin) + \
                             literal_file_path + \
                             Suppress(LineEnd())
        symbol_incbin_line.setParseAction(self._include_literal_incbin)

        # build the "include" expression in the top level map of expressions
        self._exprs.append(('literal_include_line', literal_include_line))
        self._exprs.append(('implied_include_line', implied_include_line))
        self._exprs.append(('literal_incbin_line', literal_incbin_line))
        self._exprs.append(('symbol_incbin_line', symbol_incbin_line))

    def _init_memory_exprs(self):
        
        # define setpad and align keywords
        setpad = Keyword('#setpad')
        align = Keyword('#align')

        # define quoted string for the messages
        message = Word(printables)
        message_string = quotedString(message)
        message_string.setParseAction(removeQuotes)
        message_string = message_string.setResultsName('message')

        # setpad line
        setpad_number_line = Suppress(setpad) + \
                             NumericValue.exprs().setResultsName('value') + \
                             Suppress(LineEnd())
        setpad_number_line.setParseAction(self._setpad_line)
        setpad_string_line = Suppress(setpad) + \
                             message_string + \
                             Suppress(LineEnd())
        setpad_string_line.setParseAction(self._setpad_line)

        # align line
        align_line = Suppress(align) + \
                     NumericValue.exprs().setResultsName('value') + \
                     Suppress(LineEnd())
        align_line.setParseAction(self._align_line)

        # build the expression map
        self._exprs.append(('setpad_number_line', setpad_number_line))
        self._exprs.append(('setpad_string_line', setpad_string_line))
        self._exprs.append(('align_line', align_line))

    #
    # Parse Action Callbacks
    #

    def _include_literal_file(self, pstring, location, tokens):
        """
        We want to recursively parse included files so we have to
        search for the file, open it, and then have the parser
        recursively parse the included file.  We will return the
        tokens from the parsed included file so that they get
        injected into the overall token map of the overall parse.
        """

        # increment line number
        self._state.increment_line_no()

        if self._ignore():
            return []

        if len(tokens) != 1:
            raise ParseFatalException ('invalid include file path length')

        # build a list of paths to search
        search_paths = []
        search_paths.append(self._get_cur_script_dir())

        # calculate the full path to the included file
        include_file = self._options.get_file_path(tokens.file_path, search_paths)

        # check for error
        if not include_file:
            raise ParseFatalException('included file does not exist: %s [%s]' % (tokens.file_path, search_paths))

        # open the file
        inf = open(include_file, 'r')

        # output some nice info
        self._log("%s:%s: including: %s" % (self._state.get_file(), self._state.get_line_no(), os.path.basename(inf.name)))
        
        # recursively parse the file
        recursive_tokens = self.parse(inf)

        # close the file
        inf.close()

        return recursive_tokens

    def _include_implied_file(self, pstring, location, tokens):
        """
        We want to recursively parse included files so we have to
        search for the file, open it, and then have the parser
        recursively parse the included file.  We will return the
        tokens from the parsed included file so that they get
        injected into the overall token map of the overall parse.
        """

        # increment line number
        self._state.increment_line_no()

        if self._ignore():
            return []

        if len(tokens) != 1:
            raise ParseFatalException('invalid include file path length')

        # calculate the path
        include_paths = self._options.get_include_dirs()
        if len(include_paths) == 0:
            raise ParseFatalException('no include directories specified')
      
        # search for the file in the include directories
        search_paths = self._options.get_include_dirs()
        include_file = self._options.get_file_path(tokens.file_path, search_paths)

        # check for error
        if not include_file:
            raise ParseFatalException('included file does not exist: %s [%s]' % (tokens.file_path, search_paths))
        
        # open the file
        inf = open(include_file, 'r')

        # output some nice info
        self._log("%s:%s: including: %s" % (self._state.get_file(), self._state.get_line_no(), os.path.basename(inf.name)))

        # recursively parse the file
        recursive_tokens = self.parse(inf)

        # close the file
        inf.close()

        return recursive_tokens

    def _include_literal_incbin(self, pstring, location, tokens):
        """
        We want to load up the binary data into a blob and inject
        it into the token stream to be included into the final
        binary.
        """
        
        # increment line number
        self._state.increment_line_no()

        if self._ignore():
            return []

        label = None
        if 'label' in tokens.keys():
            label = tokens.label

        # build a list of paths to search
        search_paths = []
        search_paths.append(self._get_cur_script_dir())

        # calculate the full path to the included file
        include_file = self._options.get_file_path(tokens.file_path, search_paths)

        # check for error
        if not include_file:
            raise ParseFatalException('included file does not exist: %s [%s]' % (tokens.file_path, search_paths))

        # open the file
        inf = open(include_file, 'rb')

        # create the blob token
        blob = IncBin(inf, label)

        # close the file
        inf.close()

        return blob

    def _setpad_line(self, pstring, location, tokens):

        if 'message' in tokens.keys():
            return SetPad(tokens.message)
        elif 'value' in tokens.keys():
            return SetPad(tokens.value)

        raise ParseFatalExpression('invalid padding value')

    def _align_line(self, pstring, location, tokens):
        
        if 'value' in tokens.keys():
            return SetAlign(tokens.value)

        raise ParseFatalExpression('invalid alignment value')
'''

