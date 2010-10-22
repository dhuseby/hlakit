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

from pyparsing import *
from functioncall import FunctionCall
from variable import Variable
from conditionaldecl import ConditionalDecl

class ConditionalBlock(object):

    def __init__(self, decl):
        self._decl = decl
        self._tokens = []
        self._open = True

    def append_token(self, token):
        self._tokens.append(token)

        # let functions and variables know what their scope is
        if isinstance(token, FunctionCall):
            token.set_scope(self.get_scope())
        elif isinstance(token, Variable):
            token.set_scope(self.get_scope())

    def get_tokens(self):
        return self._tokens

    def set_scope(self, name):
        self._scope_name = name

    def get_scope(self):
        return self._scope_name

    def get_mode(self):
        return self._decl.get_mode()

    def close(self):
        self._open = False

    def is_open(self):
        return self._open

    def get_decl(self):
        return self._decl


class Conditional(object):
    """
    This encapsulates a conditional block
    """

    # these are the different types of conditional blocks
    IF, IF_ELSE, WHILE, DO_WHILE, FOREVER, SWITCH, SWITCH_DEFAULT, CASE, DEFAULT, UNK = range(10)
    NAMES = [ 'IF', 'IF_ELSE', 'WHILE', 'DO_WHILE', 'FOREVER', 'SWITCH', 'SWITCH_DEFAULT', 'CASE', 'DEFAULT', 'UNKNOWN' ]

    def __init__(self, depth):
        self._type = self.UNK
        self._blocks = []
        self._depth = depth
        self._fn = None

    def get_depth(self):
        return self._depth

    def get_name(self):
        return self.NAMES[self._type]

    def append_token(self, token):
        token.set_fn(self._fn)
        self._blocks[0].append_token(token)

    def set_scope(self, name):
        self._blocks[0].set_scope(name)

    def get_scope(self):
        return self._blocks[0].get_scope()

    def new_block(self, token):
        if not isinstance(token, ConditionalDecl):
            raise ParseFatalException('can only start a conditional block with a ConditionalDecl')
        cb = ConditionalBlock(token)

        # put it at the front of the list
        self._blocks.insert(0, cb)

    def add_block(self, block):
        if not isinstance(block, ConditionalBlock):
            raise ParseFatalException('trying to add non conditional block to conditional')

        # set the block's scope properly
        block.set_scope(self.get_scope())

        # put the block in the list
        self._blocks.insert(0, block)

    def close_block(self):
        self._blocks[0].close()

    def is_block_open(self):
        if len(self._blocks) > 0:
            return self._blocks[0].is_open()
        return False

    def replace_block_decl(self, decl):
        self._blocks[0]._decl = decl

    def get_blocks(self):
        return self._blocks

    def get_tokens(self, block=0):
        return self._blocks[block]

    def set_type(self, type_):
        if type_ not in (self.IF, self.IF_ELSE, self.WHILE, 
                         self.DO_WHILE, self.FOREVER, self.SWITCH, 
                         self.SWITCH_DEFAULT, self.CASE, self.DEFAULT):
            raise ParseFatalException('invalid conditional type')
        self._type = type_

    def get_type(self):
        return self._type

    def set_fn(self, fn=None):
        self._fn = fn

        # cascade the fn setting...
        for b in self._blocks:
            for t in b.get_tokens():
                t.set_fn(fn)

    def get_fn(self):
        return self._fn

    def __str__(self):
        return self.NAMES[self.get_type()]

