"""
HLAKit
Copyright (C) David Huseby <dave@linuxprogrammer.org>

This software is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 3.0 License.  You may read the full text of the license in the 
included LICENSE file or by visiting here: 
<http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode>
"""

class IncBin(object):
    """
    This is a wrapper class around some binary data included
    directly into the final binary from the code.
    """
    def __init__(self, f, label = None):
        self._name = f.name
        self._data = f.read()
        self._label = label

    def get_data(self):
        return self._data

    def get_label(self):
        return self._label

    def __str__(self):
        if self._label is None:
            return "<%s>" % self._name
        return "<%s: %s>" % (self._label, self._name)

    __repr__ = __str__

class SetPad(object):
    """
    Token for setting the current padding contents
    """
    def __init__(self, padding):
        self._padding = padding

    def get_padding(self):
        return self._padding

    def __str__(self):
        return "<%s>" % self._padding

    __repr__ = __str__

class SetAlign(object):
    """
    Token for setting the current alignment value
    """
    def __init__(self, alignment):
        self._alignment = alignment

    def get_alignement(self):
        return self._alignment

    def __str__(self):
        return "<0x%x>" % self._alignment

    __repr__ = __str__

class CodeLine(object):
    """
    This is a wrapper class around a line of code that contains
    it's origin file and line number before preprocessing.
    """
    def __init__(self, code, f, line_no):
        self._code = code
        self._f = f
        self._line_no = line_no

    def get_code(self):
        return self._code

    def get_file(self):
        return self._f

    def get_line_no(self):
        return self._line_no

    def __str__(self):
        return self._code

    __repr__ = __str__

class CodeBlock(object):
    """
    This encapsulates a list of CodeLine objects into a cohesive
    code block that can be translated back into plain text.
    """
    def __init__(self):
        self._lines = []

    def append(self, line):
        self._lines.append(line)

    def num_lines(self):
        return len(self._lines)

    def __str__(self):
        out = "\n"
        for line in self._lines:
            out += str(line) + "\n"
        return out + "\n"

    __repr__ = __str__


