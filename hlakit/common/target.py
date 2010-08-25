"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

from pyparsing import *
from preprocessor import Preprocessor
from compiler import Compiler
from symboltable import SymbolTable

class Target(object):

    KEYWORDS = [ 'typedef', 'struct', 'function', 'inline', 'interrupt', 
                 'noreturn', 'return', 'near', 'far', 'is', 'has', 'no',
                 'not', 'if', 'else', 'while', 'do', 'forever', 'switch',
                 'case', 'default', 'shared' ]
    
    def __init__(self):
        # get a handle to the global symbol table
        st = SymbolTable()

        # reset its state back to the global scope
        st.reset_state()

    def opcodes(self):
        return None

    def keywords(self):
        return MatchFirst([CaselessKeyword(kw) for kw in Target.KEYWORDS])

    def basic_types(self):
        return None

    def basic_types_names(self):
        return None

    def conditions(self):
        return None

    def preprocessor(self):
        return Preprocessor()

    def compiler(self):
        return Compiler()

    def generator(self):
        return None

