"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

from preprocessor import Preprocessor
from compiler import Compiler
from symboltable import SymbolTable
from name import Name
from functiontype import FunctionType
from functionparameter import FunctionParameter
from function import Function, FunctionCall

class Target(object):

    def __init__(self):
        # we treat the sizeof, hi, lo, nyhi, and nylo operators just like
        # regular functions so we need to prime the pump by defining them in
        # the global symbol table before any files get compiled
        sizeof_     = Function(Name('sizeof'),  
                               FunctionType('operator'), 
                               [ FunctionParameter('imm') ])
        hi_         = Function(Name('hi'),
                               FunctionType('operator'),
                               [ FunctionParameter('imm') ])
        lo_         = Function(Name('lo'),
                               FunctionType('operator'),
                               [ FunctionParameter('imm') ])
        nyhi_       = Function(Name('nyhi'),
                               FunctionType('operator'),
                               [ FunctionParameter('imm') ])
        nylo_       = Function(Name('nylo'),
                               FunctionType('operator'),
                               [ FunctionParameter('imm') ])

        # get a handle to the global symbol table
        st = SymbolTable()

        # reset its state back to the global scope
        st.reset_state()
        
        # add the functions to the global scope
        st.new_symbol(sizeof_)
        st.new_symbol(hi_)
        st.new_symbol(lo_)
        st.new_symbol(nyhi_)
        st.new_symbol(nylo_)

    def preprocessor(self):
        return Preprocessor()

    def compiler(self):
        return Compiler()

    def linker(self):
        return None

