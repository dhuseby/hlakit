from pyparsing import *

class Exprs(object):

    def __init__(self, parser):

        # store a reference to the parser interface
        self._parser = parser

    def get_exprs(self):
        pass

    def get_parser(self):
        """
        This is used to get a reference to the parent parser
        that is driving the parse.  This allows parse actions
        to call back into the parser to have it do stuff like
        recursively parse an included file.
        """
        return self._parser

