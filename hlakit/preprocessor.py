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
from tokens import *

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
          
            # init the line number
            self._line_no = 0

            # the current file name
            self._file = f

            # initialize the pyparsing parser as ZeroOrMore(Or())
            # of all of the expressions 
            expr_or = Or([])
            for e in exprs:
                expr_or.append(e[1])
           
            # build final parser
            self._parser = ZeroOrMore(expr_or)

        def increment_line_no(self):
            self._line_no += 1

        def get_file(self):
            return os.path.basename(self._file.name)

        def get_line_no(self):
            return self._line_no

    def __init__(self, options = None, logger = None):

        # init the base class
        super(Preprocessor, self).__init__()

        # initialize the machine and cpu
        self._machine = options.get_machine(logger)
        self._cpu = options.get_cpu(logger)

        # store our options
        self._options = options

        # stack of parser states to enable recursive file parsing
        self._state_stack = []

        # current parser state
        self._state = None

        # the ignore state
        self._ignore_stack = [ False ]

        # initialize the map of expressions
        self._exprs = []

        # preprocessor symbols table
        self._symbols = {}

        # build the preprocessor expressions
        self._init_preprocessor_exprs()

    def get_exprs(self):
        return self._exprs

    def _log(self, s):
        # TODO: convert this to use the logger object
        indent = ""
        for i in range(0,len(self._state_stack)):
           indent += "    "

        print indent + s

    def _get_cur_script_dir(self):
        return os.path.dirname(self._state._file.name)

    def _do_parse(self):
        # parse the file
        self._log("Parsing: %s" % self._state._file.name)
        tokens = self._state._parser.parseFile(self._state._file, parseAll=True)
        self._log("Done parsing: %s" % self._state._file.name)
        return tokens

    def parse(self, f):
        # push our current state if we're recursively parsing
        if self._state:
            # push our current state on the stack
            self._state_stack.append(self._state)

        # set up a new context
        self._state = Preprocessor.StateFrame(f, self._exprs)

        # do the parse
        tokens = self._do_parse()

        # restore previous state if there is one
        if len(self._state_stack):
            self._state = self._state_stack.pop()
        else:
            # when we get here, we're done parsing everything...
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

            # make sure we return the pp_tokens
            tokens = pp_tokens

        return tokens

    def _init_preprocessor_exprs(self):
        self._init_defines_exprs()
        self._init_messages_exprs()
        self._init_files_exprs()
        self._init_memory_exprs()
        # add in the machine and cpu preprocessor exprs
        self._init_machine_exprs()
        self._init_cpu_exprs()
        # note that generic exprs must be last
        self._init_generic_exprs()

    def _init_machine_exprs(self):
        # this gets all of the preprocessor expressions from the machine
        # and adds them to the preprocessor expressions list
        if self._machine:
            self._exprs.extend(self._machine.get_preprocessor_exprs())

    def _init_cpu_exprs(self):
        # this gets all of the preprocessor expressions from the cpu
        # and adds them to the preprocessor expressions list
        if self._cpu:
            self._exprs.extend(self._cpu.get_preprocessor_exprs())

    def _init_generic_exprs(self):
        # this matches all lines that don't match any other rules
        generic_line = ZeroOrMore(~LineEnd() + Word(printables)) + Suppress(LineEnd())
        generic_line.setParseAction(self._generic_line)

        # add it to the expressions list
        self._exprs.append(('generic_line', generic_line))

    def _init_defines_exprs(self):
        # define the preprocessor conditional compile keywords
        d_define = Keyword('#define')
        d_undef = Keyword('#undef')
        d_ifdef = Keyword('#ifdef')
        d_ifndef = Keyword('#ifndef')
        d_else = Keyword('#else')
        d_endif = Keyword('#endif')

        # define label
        label = Word(alphas + '_', alphanums + '_').setResultsName('label')

        # define value
        value = OneOrMore(~LineEnd() + Word(printables)).setResultsName('value')

        # ==> #define label
        define_line = Suppress(d_define) + \
                      label + \
                      Suppress(LineEnd())
        define_line.setParseAction(self._define_line)
        
        # ==> #define label value
        define_line_value = Suppress(d_define) + \
                            label + \
                            value + \
                            Suppress(LineEnd())
        define_line_value.setParseAction(self._define_line_value)

        # ==> #undef label
        undef_line = Suppress(d_undef) + \
                     label + \
                     Suppress(LineEnd())
        undef_line.setParseAction(self._undef_line)

        # ==> #ifdef label
        ifdef_line = Suppress(d_ifdef) + \
                     label + \
                     Suppress(LineEnd())
        ifdef_line.setParseAction(self._ifdef_line)

        # ==> #ifndef label
        ifndef_line = Suppress(d_ifndef) + \
                      label + \
                      Suppress(LineEnd())
        ifndef_line.setParseAction(self._ifndef_line)

        # ==> #else
        else_line = Suppress(d_else) + \
                    Suppress(LineEnd())
        else_line.setParseAction(self._else_line)

        # ==> #endif
        endif_line = Suppress(d_endif) + \
                     Suppress(LineEnd())
        endif_line.setParseAction(self._endif_line)

        # put the conditional compile expressions in the top level map
        self._exprs.append(('define_line', define_line))
        self._exprs.append(('define_line_value', define_line_value))
        self._exprs.append(('undef_line', undef_line))
        self._exprs.append(('ifdef_line', ifdef_line))
        self._exprs.append(('ifndef_line', ifndef_line))
        self._exprs.append(('else_line', else_line))
        self._exprs.append(('endif_line', endif_line))

    def _init_messages_exprs(self):
        # define message literals
        todo = Keyword('#todo')
        warning = Keyword('#warning')
        error = Keyword('#error')
        fatal = Keyword('#fatal')

        # define quoted string for the messages
        message = Word(printables)
        message_string = quotedString(message)
        message_string.setParseAction(removeQuotes)
        message_string = message_string.setResultsName('message')

        # ==> #todo "message"
        todo_line = Suppress(todo) + message_string + Suppress(LineEnd())
        todo_line.setParseAction(self._todo_message)
        
        # ==> #warning "message"
        warning_line = Suppress(warning) + message_string + Suppress(LineEnd())
        warning_line.setParseAction(self._warning_message)

        # ==> #error "message"
        error_line = Suppress(error) + message_string + Suppress(LineEnd())
        error_line.setParseAction(self._error_message)

        # ==> #fatal "message"
        fatal_line = Suppress(fatal) + message_string + Suppress(LineEnd())
        # NOTE: error and fatal use the same parse action because I
        #       couldn't think of how they would differ in practice
        fatal_line.setParseAction(self._error_message)
        
        # put the message expressions in the top level map
        self._exprs.append(('todo_line', todo_line))
        self._exprs.append(('warning_line', warning_line))
        self._exprs.append(('error_line', error_line))
        self._exprs.append(('fatal_line', fatal_line))

    def _init_files_exprs(self):
        
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

        # build the "include" expression in the top level map of expressions
        self._exprs.append(('literal_include_line', literal_include_line))
        self._exprs.append(('implied_include_line', implied_include_line))
        self._exprs.append(('literal_incbin_line', literal_incbin_line))

    def _init_memory_exprs(self):
        pass

    def _set_symbol(self, label, value = None):
        self._symbols[label] = value

    def _get_symbol(self, label):
        return self._symbols[label]

    def _has_symbol(self, label):
        return self._symbols.has_key(label)

    def _delete_symbol(self, label):
        if self._symbols.haskey(label):
            self._symbols.pop(label)

    def _get_symbols(self):
        return self._symbols

    def _expand_symbols(self, line):
        expanded_line = line
        for (symbol, value) in self._symbols.iteritems():
            if value == None:
                value = ''
            expanded_line = expanded_line.replace(symbol, value)

        return expanded_line

    def _ignore(self):
        if self._ignore_stack[-1] == True or self._ignore_stack[-1] == None:
            return True

        return False

    #
    # Parse Action Callbacks
    #

    def _generic_line(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        if self._ignore():
            return []

        # merge the tokens back into a single line of text
        line = ' '.join(tokens)

        # return an appropriate array of tokens
        if not len(line):
            return []
        else:
            # do macro expansion here
            line = self._expand_symbols(line)
            
            # output some nice debug
            self._log("%s:%s: Generic line: %s" % (self._state.get_file(), self._state.get_line_no(), line))
            
            # return a CodeLine object ecapsulating the code 
            return [CodeLine(line, self._state.get_file(), self._state.get_line_no())]

    def _define_line(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        if self._ignore():
            return []

        # define the symbol
        self._log('Defining: %s' % tokens.label)
        self._set_symbol(tokens.label, None)

        # return empty list to eat tokens
        return []

    def _define_line_value(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        if self._ignore():
            return []

        # check to see if there is a value
        value = None
        if hasattr(tokens, 'value'):
            value = ' '.join(tokens.value)

        # do macro expansion here so that we support recursive macros
        value = self._expand_symbols(value)

        # define the symbol
        self._log('Defining: %s as %s' % (tokens.label, value))
        self._set_symbol(tokens.label, value)

        # return empty list to eat tokens
        return []

    def _undef_line(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        if self._ignore():
            return []

        # delete the symbol
        self._delete_symbol(tokens.label)

        # return empty list to eat tokens
        return []

    def _ifdef_line(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        # the top of the ignore stack is None if we're nested inside
        # of an ignored block of code.  we have to push another None
        # on the stack to track our nesting
        if self._ignore():
            self._ignore_stack.append(None)
            return []

        self._log("Ifdef %s is %s" % (tokens.label, self._has_symbol(tokens.label)))
        
        # check to see if we should turn ignore on
        if not self._has_symbol(tokens.label):
            self._ignore_stack.append(True)
        else:
            self._ignore_stack.append(False)

        return []

    def _ifndef_line(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        # the top of the ignore stack is None if we're nested inside
        # of an ignored block of code.  we have to push another None
        # on the stack to track our nesting
        if self._ignore():
            self._ignore_stack.append(None)
            return []

        self._log("Ifndef %s is %s" % (tokens.label, not self._has_symbol(tokens.label)))
        
        # check to see if we should turn ignore on
        if self._has_symbol(tokens.label):
            self._ignore_stack.append(True)
        else:
            self._ignore_stack.append(False)

        return []

    def _else_line(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        self._log("Else")

        # the top of the ignore stack is None if we're nested inside
        # of an ingnored block of code.  we don't do anything in that case.
        if self._ignore_stack[-1] == None:
            return []

        # so we're in an active block of code if we get here so we need
        # to check to see if we're in a block and if so, flip from active
        # to innactive.
        if len(self._ignore_stack) <= 1:
            raise ParseFatalException("#else outside of #ifdef/#ifndef block")

        # swap states
        if self._ignore():
            self._ignore_stack[-1] = False
        else:
            self._ignore_stack[-1] = True

        return []
    
    def _endif_line(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        self._log("Endif")

        if len(self._ignore_stack) <= 1:
            raise ParseFatalException("#endif without matching #ifdef/#ifndef")

        # pop the current ignore state off of the stack
        self._ignore_stack.pop()

        return []

    def _todo_message(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        if self._ignore():
            return []

        self._log("%s:%s: TODO: %s" % (self._state.get_file(), self._state.get_line_no(), tokens.message))
        # return an empty list to that the todo message token
        # gets deleted from the token stream
        return []

    def _warning_message(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        if self._ignore():
            return []

        self._log("%s:%s: WARNING: %s" % (self._state.get_file(), self._state.get_line_no(), tokens.message))
        # return an empty list to that the todo message token
        # gets deleted from the token stream
        return []

    def _error_message(self, pstring, location, tokens):
        # increment line number
        self._state.increment_line_no()

        if self._ignore():
            return []

        self._log("%s:%s: ERROR: %s" % (self._state.get_file(), self._state.get_line_no(), tokens.message))
        # raise a fatal exception to halt parsing
        raise ParseFatalException(tokens.message)

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
            raise ParseFatalException('included file does not exist: %s' % include_file)

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
            raise ParseFatalException('included file does not exist: %s' % include_file)
        
        # open the file
        inf = open(include_file, 'r')

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

        if len(tokens) != 1:
            raise ParseFatalException ('invalid include file path length')

        # build a list of paths to search
        search_paths = []
        search_paths.append(self._get_cur_script_dir())

        # calculate the full path to the included file
        include_file = self._options.get_file_path(tokens.file_path, search_paths)

        # check for error
        if not include_file:
            raise ParseFatalException('included file does not exist: %s' % include_file)

        # open the file
        inf = open(include_file, 'rb')

        # create the blob token
        blob = IncBin(inf)

        # close the file
        inf.close()

        return blob

