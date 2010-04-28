"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

class CPU(object):

    def __init__(self, options = None, logger = None):
        pass
       
    def get_cpu(self):
        return None

    def get_preprocessor_exprs(self):
        return None

    def get_assembly_line_expr(self):
        return None

    def get_file_writer(self):
        return None

    def init_compiler_types(self):
        pass
