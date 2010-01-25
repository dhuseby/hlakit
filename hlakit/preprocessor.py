import os

from pyparsing import *
from exprs import Exprs

class IncBin(object):
    """
    This is a wrapper class around some binary data included
    directly into the final binary from the code.
    """
    def __init__(self, f):
        self._data = f.read()

    def get_data(self):
        return self._data

class Preprocessor(Exprs):

    FILE_NAME_CHARS = '0123456789' + \
                      'abcdefghijklmnopqrstuvwxyz' + \
                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
                      '!"#$%&\\\'()*+,-./:;=?@[]^_`{|}~'

    def __init__(self, parser):

        # init the base class
        super(Preprocessor, self).__init__(parser)

        # varibles for storing the state as we recursively parse files
        self._state = []
        self._file = None

        # initialize the map of expressions
        self._exprs = {}

        # build the preprocessor expressions
        self._init_preprocessor_exprs()

    def get_exprs(self):
        return self._exprs

    def _init_preprocessor_exprs(self):
        self._init_defines_exprs()
        self._init_messages_exprs()
        self._init_files_exprs()
        self._init_memory_exprs()

    def _init_defines_exprs(self):
        # define the preprocessor conditional compile keywords
        d_define = Keyword('#define')
        d_undef = Keyword('#undef')
        d_ifdef = Keyword('#ifdef')
        d_ifndef = Keyword('#ifndef')
        d_else = Keyword('#else')
        d_endif = Keyword('#endif')

        # define label
        label = Word(alphas, alphanums + '-_').setResultsName('label')

        # define value
        value = Word(printables).setResultsName('value')

        # ==> #define label [value]
        define_line = Suppress(d_define) + \
                      label + \
                      Optional(value) + \
                      Suppress(LineEnd())
        define_line.setParseAction(self._define_line)

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
        self._exprs['define_line'] = define_line
        self._exprs['undef_line'] = undef_line
        self._exprs['ifdef_line'] = ifdef_line
        self._exprs['ifndef_line'] = ifndef_line
        self._exprs['else_line'] = else_line
        self._exprs['endif_line'] = endif_line

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
        self._exprs['todo_line'] = todo_line
        self._exprs['warning_line'] = warning_line
        self._exprs['error_line'] = error_line
        self._exprs['fatal_line'] = fatal_line

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
        self._exprs['literal_include_line'] = literal_include_line
        self._exprs['implied_include_line'] = implied_include_line
        self._exprs['literal_incbin_line'] = literal_incbin_line

    def _init_memory_exprs(self):
        pass

    #
    # Parse Action Callbacks
    #

    def _define_line(self, pstring, location, tokens):
        # check to see if there is a value
        value = None
        if hasattr(tokens, 'value'):
            value = tokens.value

        # define the symbol
        self.get_parser().set_symbol(tokens.label, value)

        # return empty list to eat tokens
        return []

    def _undef_line(self, pstring, location, tokens):
        # delete the symbol
        self.get_parser().delete_symbol(tokens.label)

    def _ifdef_line(self, pstring, location, tokens):
        # use skipTo to skip to the next #else, #endif OR #ifdef
        # if we hit another #ifdef, then recurse
        # if we hit an #endif, unwind
        pass

    def _ifndef_line(self, pstring, location, tokens):
        pass

    def _else_line(self, pstring, location, tokens):
        pass

    def _endif_line(self, pstring, location, tokens):
        pass

    def _todo_message(self, pstring, location, tokens):
        print "TODO: %s" % tokens.message
        # return an empty list to that the todo message token
        # gets deleted from the token stream
        return []

    def _warning_message(self, pstring, location, tokens):
        print "WARNING: %s" % tokens.message
        # return an empty list to that the todo message token
        # gets deleted from the token stream
        return []

    def _error_message(self, pstring, location, tokens):
        print "ERROR: %s" % tokens.message
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
        
        if len(tokens) != 1:
            raise ParseFatalException ('invalid include file path length')

        # build a list of paths to search
        search_paths = []
        search_paths.append(self.get_parser().get_cur_script_dir())

        # calculate the full path to the included file
        include_file = self.get_parser().get_options().get_file_path(tokens.file_path, search_paths)

        # check for error
        if not include_file:
            raise ParseFatalException('included file does not exist: %s' % include_file)

        # open the file
        inf = open(include_file, 'r')

        # recursively parse the file
        recursive_tokens = self.get_parser().parse(inf)

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

        if len(tokens) != 1:
            raise ParseFatalException('invalid include file path length')

        # calculate the path
        include_paths = self.get_parser().get_options().get_include_dirs()
        if len(include_paths) == 0:
            raise ParseFatalException('no include directories specified')
      
        # search for the file in the include directories
        search_paths = self.get_parser().get_options().get_include_dirs()
        include_file = self.get_parser().get_options().get_file_path(tokens.file_path, search_paths)

        # check for error
        if not include_file:
            raise ParseFatalException('included file does not exist: %s' % include_file)
        
        # open the file
        inf = open(include_file, 'r')

        # recursively parse the file
        recursive_tokens = self.get_parser().parse(inf)

        # close the file
        inf.close()

        return recursive_tokens

    def _include_literal_incbin(self, pstring, location, tokens):
        """
        We want to load up the binary data into a blob and inject
        it into the token stream to be included into the final
        binary.
        """
        
        if len(tokens) != 1:
            raise ParseFatalException ('invalid include file path length')

        # build a list of paths to search
        search_paths = []
        search_paths.append(self.get_parser().get_cur_script_dir())

        # calculate the full path to the included file
        include_file = self.get_parser().get_options().get_file_path(tokens.file_path, search_paths)

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

