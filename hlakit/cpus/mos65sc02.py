"""
Copyright (c) 2010-2014 David Huseby. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDERS AND CONTRIBUTORS OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of copyright holders and contributors.
"""

CPU_CLASS = 'MOS65SC02'

class MOS65SC02(object):

    # 6502 conditional tokens 
    conditionals = {
        'is':           'IS',
        'has':          'HAS',
        'no':           'NO',
        'not':          'NOT',
        'plus' :        'POSITIVE',     # N = 0
        'positive':     'POSITIVE',     # N = 0
        'minus':        'NEGATIVE',     # N = 1
        'negative':     'NEGATIVE',     # N = 1
        'greater':      'GREATER',      # N = 0, Z = 0, C = 1
        'less':         'LESS',         # N = 1, Z = 0, C = 0
        'overflow':     'OVERFLOW',     # V = 1
        'carry':        'CARRY',        # C = 1
        'nonzero':      'TRUE',         # Z = 0
        'set':          'TRUE',         # Z = 0
        'true':         'TRUE',         # Z = 0
        '1':            'TRUE',         # Z = 0
        'zero':         'FALSE',        # Z = 1
        'unset':        'FALSE',        # Z = 1
        'false':        'FALSE',        # Z = 1
        '0':            'FALSE',        # Z = 1
        'clear':        'FALSE',        # Z = 1
        'equal':        'EQUAL'         # N = 0, Z = 1, C = 1
    }

    # opcodes
    reserved = {
        # atomic types
        'byte':         'TYPE',
        'char':         'TYPE',
        'bool':         'TYPE',
        'word':         'TYPE',
        'pointer':      'TYPE',

        # registers
        'reg':          'REG',
        'a':            'REG',
        'x':            'REG',
        'y':            'REG',

        # opcodes
        'adc':          'OPCODE', 
        'and':          'OPCODE', 
        'asl':          'OPCODE', 
        'bcc':          'OPCODE', 
        'bcs':          'OPCODE', 
        'beq':          'OPCODE', 
        'bit':          'OPCODE', 
        'bmi':          'OPCODE', 
        'bne':          'OPCODE', 
        'bpl':          'OPCODE', 
        'brk':          'OPCODE', 
        'bvc':          'OPCODE', 
        'bvs':          'OPCODE', 
        'clc':          'OPCODE', 
        'cld':          'OPCODE', 
        'cli':          'OPCODE', 
        'clv':          'OPCODE', 
        'cmp':          'OPCODE', 
        'cpx':          'OPCODE', 
        'cpy':          'OPCODE', 
        'dec':          'OPCODE', 
        'dex':          'OPCODE', 
        'dey':          'OPCODE', 
        'eor':          'OPCODE', 
        'inc':          'OPCODE', 
        'inx':          'OPCODE', 
        'iny':          'OPCODE', 
        'jmp':          'OPCODE', 
        'jsr':          'OPCODE', 
        'lda':          'OPCODE', 
        'ldx':          'OPCODE', 
        'ldy':          'OPCODE', 
        'lsr':          'OPCODE', 
        'nop':          'OPCODE', 
        'ora':          'OPCODE', 
        'pha':          'OPCODE', 
        'php':          'OPCODE', 
        'pla':          'OPCODE', 
        'plp':          'OPCODE', 
        'rol':          'OPCODE', 
        'ror':          'OPCODE', 
        'rti':          'OPCODE', 
        'rts':          'OPCODE', 
        'sbc':          'OPCODE', 
        'sec':          'OPCODE', 
        'sed':          'OPCODE', 
        'sei':          'OPCODE', 
        'sta':          'OPCODE', 
        'stx':          'OPCODE', 
        'sty':          'OPCODE', 
        'tax':          'OPCODE', 
        'tay':          'OPCODE', 
        'tsx':          'OPCODE', 
        'txa':          'OPCODE', 
        'txs':          'OPCODE', 
        'tya':          'OPCODE'
    }

    tokens = [ 
        'TYPE',
        'OPCODE',
        'REG'
    ]

    def __init__(self):
        pass

    @property
    def callbacks(self):
         return { ( 'NORESOLVE_ID',      self._ni_id ),
                  ( 'INITIAL_ID',        self._ni_id ) }

    @property
    def handlers(self):
        return {
            'TYPE': self._type,
            'OPCODE': self._opcode,
            'REG': self._reg
        }

    def _ni_id(self, l, t):
        t.type = self.reserved.get( t.value, 'ID' )
        if t.type != 'ID' and l.lexer.lexstate == 'INITIAL_ID':
            handler = self.handlers[t.type]
            return handler(l, t)

        # not one of our reserved words so we don't handle it
        return (False, t)

    def _type(self, l, t):
        return (True, t)

    def _opcode(self, l, t):
        return (True, t)

    def _reg(self, l, t):
        return (True, t)

