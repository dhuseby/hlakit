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

class Target(object):
    def preprocessor(self):
        return Preprocessor()

    def compiler(self):
        return Compiler()

    def linker(self):
        return None

