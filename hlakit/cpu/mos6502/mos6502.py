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

import os
from pyparsing import *
from hlakit.common.target import Target
from hlakit.common.preprocessor import Preprocessor
from hlakit.common.compiler import Compiler
from hlakit.common.generator import Generator
from hlakit.common.type_ import Type
from hlakit.common.label import Label
from hlakit.common.conditional import Conditional
from hlakit.common.function import Function
from hlakit.common.functiondecl import FunctionDecl
from hlakit.common.functioncall import FunctionCall
from hlakit.common.functionreturn import FunctionReturn
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd
from hlakit.common.symboltable import SymbolTable
from interrupt import InterruptStart, InterruptNMI, InterruptIRQ
from instructionline import InstructionLine
from conditionaldecl import ConditionalDecl
from opcode import Opcode

class MOS6502Preprocessor(Preprocessor):

    @classmethod
    def first_exprs(klass):
        e = []

        # start with the first base preprocessor rules 
        e.extend(Preprocessor.first_exprs())

        # add in 6502 specific preprocessor parse rules
        e.append(('interruptstart', InterruptStart.exprs()))
        e.append(('interruptnmi', InterruptNMI.exprs()))
        e.append(('interruptirq', InterruptIRQ.exprs()))
        
        return e

class MOS6502Compiler(Compiler):

    @classmethod
    def first_exprs(klass):
        e = []

        # add in 6502 specific compiler parse rules
        e.append(('instructionline', InstructionLine.exprs()))
        e.append(('conditionaldecl', ConditionalDecl.exprs()))

        # start with the first base compiler rules 
        e.extend(Compiler.first_exprs())
       
        return e

    def _open_scoped_block(self, cond, token):
        # it's a scoped block
        st = SymbolTable()
        self._append_token_to_scope(token)
        self._increment_depth()
        st.scope_push()
        cond.set_scope(st.current_scope_name())

    def _close_conditional(self, cond, token):
        # append the token and close the block
        self._append_token_to_scope(token)
        self._decrement_depth()
        cond.close_block()

        # this conditional is done
        (token, depth) = self._pop_scope()
        return token 

    def _close_if(self, cond, token):
        # check to see if the one line if block is followed by an else 
        next = self._peek_token()

        if isinstance(next, ConditionalDecl) and \
           next.get_mode == ConditionalDecl.ELSE:
            # yes it is, so close the if block and return None
            # so that the else block will be processed
            self._append_token_to_scope(token)
            cond.close_block()
            return None
        else:
            # close block and return conditional
            return self._close_conditional(cond, token)

    def _close_do(self, cond, token):
        # check for the while
        w = self._get_token()
        if isinstance(w, ConditionalDecl) and \
           w.get_mode() == ConditionalDecl.WHILE:
            # replace the block's decl
            cond.replace_block_decl(w)
            return self._close_conditional(cond, token)
        else:
            raise ParseFatalError('missing while after one-line do block')


    def _process_if(self, token):
        # start a new conditional
        cond = Conditional(self._get_depth())
        cond.set_type(Conditional.IF)
        self._push_scope(cond)
        
        # start a new conditional block
        cond.new_block(token)

        # we have to check the token following the decl to figure out what
        # to do next...
        token = self._get_token()
        if isinstance(token, ScopeBegin):
            # starting a scoped if block
            self._open_scoped_block(cond, token)
            return None

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._put_token(token)
            return None

        elif isinstance(token, InstructionLine):
            return self._close_if(cond, token)
        else:
            # invalid token
            raise ParseFatalError('invalid token following if declaration')


    def _process_else(self, token):
        # get the current context
        cond = self._get_scope_context()

        # so else decls can only happen immediately after an if block
        if (not isinstance(cond, Conditional)) or \
           (cond.get_type() != Conditional.IF):
            raise ParseFatalError('else block without preceding if block')
        
        # check to make sure the if block isn't still open 
        if cond.is_block_open():
            raise ParseFatalError('else block in open if block')

        # update the conditional type
        cond.set_type(Conditional.IF_ELSE)

        # the else block
        cond.new_block(token)

        # we have to check the token after the else decl to know what
        # to do next...
        token = self._get_token()
        if isinstance(token, ScopeBegin):
            # starting a scoped else block
            self._open_scoped_block(cond, token)
            return None

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._put_token(token)
            return None

        elif isinstance(token, InstructionLine):
            # one line else block so close it and return the conditional
            self._increment_depth()
            return self._close_conditional(cond, token)
        
        else:
            # invalid token...
            raise ParseFatalError('invalid token after else')


    def _process_do(self, token):
        # start a new conditional
        cond = Conditional(self._get_depth())
        cond.set_type(Conditional.DO_WHILE)
        self._push_scope(cond)
       
        # start a new conditional block
        cond.new_block(token)

        # now we have to check the next token to figure out what
        # to do next...
        token = self._get_token()
        if isinstance(token, ScopeBegin):
            # starting a scoped do block
            self._open_scoped_block(cond, token)
            return None

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._put_token(token)
            return None

        elif isinstance(token, InstructionLine):
            self._increment_depth()
            return self._close_do(cond, token)

    def _process_while(self, token):
        # start a new conditional
        cond = Conditional(self._get_depth())
        cond.set_type(Conditional.WHILE)
        self._push_scope(cond)
        
        # start a new conditional block
        cond.new_block(token)

        # now we have to check the next token to figure out what
        # to do next...
        token = self._get_token()
        if isinstance(token, ScopeBegin):
            # starting a scoped block
            self._open_scoped_block(cond, token)
            return None

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._put_token(token)
            return None

        elif isinstance(token, InstructionLine):
            self._increment_depth()
            return self._close_conditional(cond, token)

    def _process_forever(self, token):
        # start a new conditional
        cond = Conditional(self._get_depth())
        cond.set_type(Conditional.FOREVER)
        self._push_scope(cond)
        
        # start a new conditional block
        cond.new_block(token)

        # now we have to check the next token to figure out what
        # to do next...
        token = self._get_token()
        if isinstance(token, ScopeBegin):
            # starting a scoped block
            self._open_scoped_block(cond, token)
            return None

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._put_token(token)
            return None

        elif isinstance(token, InstructionLine):
            self._increment_depth()
            return self._close_conditional(cond, token)

    def _process_switch(self, token):
        # start a new conditional
        cond = Conditional(self._get_depth())
        cond.set_type(Conditional.SWITCH)
        self._push_scope(cond)
       
        # switch decls don't start a block...

        # now we have to check the next token to figure out what
        # to do next...
        token = self._get_token()

        if isinstance(token, ScopeBegin):
            # eat the token
            return None
        else:
            raise ParseFatalException('switch decl not followed by curly brace')

    def _process_case(self, token):
        # get the current context
        cond = self._get_scope_context()

        # so else decls can only happen immediately after an if block
        if (not isinstance(cond, Conditional)) or \
           (cond.get_type() != Conditional.SWITCH):
            raise ParseFatalError('case block not in a switch decl')
        
        # check to make sure the if block isn't still open 
        if cond.is_block_open():
            raise ParseFatalError('case block in an open conditional block')

        # the case block
        cond.new_block(token)

        # we have to check the token after the case decl to know what
        # to do next...
        token = self._get_token()
        if isinstance(token, ScopeBegin):
            # starting a scoped else block
            self._open_scoped_block(cond, token)
            return None

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._put_token(token)
            return None

        elif isinstance(token, InstructionLine):
            # one line case block so add the token and close the block
            self._append_token_to_scope(token)
            cond.close_block()

        else:
            # invalid token...
            raise ParseFatalError('invalid token after case')

    def _process_default(self, token):
        # get the current context
        cond = self._get_scope_context()

        # so else decls can only happen immediately after an if block
        if (not isinstance(cond, Conditional)) or \
           (cond.get_type() != Conditional.SWITCH):
            raise ParseFatalError('default block not in a switch decl')
        
        # check to make sure the if block isn't still open 
        if cond.is_block_open():
            raise ParseFatalError('default block in an open conditional block')

        # update the condtional type
        cond.set_type(Conditional.SWITCH_DEFAULT)

        # the case block
        cond.new_block(token)

        # we have to check the token after the case decl to know what
        # to do next...
        token = self._get_token()
        if isinstance(token, ScopeBegin):
            # starting a scoped else block
            self._open_scoped_block(cond, token)
            return None

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._put_token(token)
            return None

        elif isinstance(token, InstructionLine):
            # one line case block so add the token and close the block
            self._append_token_to_scope(token)
            cond.close_block()

        else:
            # invalid token...
            raise ParseFatalError('invalid token after case')

    def _parse_next(self):

        st = SymbolTable()

        # get the next token
        token = self._get_token()

        # add instruction lines to the current scope
        if isinstance(token, InstructionLine):
            self._append_token_to_scope(token)
            return None

        # handle the different types of conditional decls
        elif isinstance(token, ConditionalDecl):
            
            if token.get_mode() == ConditionalDecl.IF:
                return self._process_if(token)

            elif token.get_mode() == ConditionalDecl.ELSE:
                return self._process_else(token)

            elif token.get_mode() == ConditionalDecl.DO:
                return self._process_do(token)

            elif token.get_mode() == ConditionalDecl.WHILE:
                return self._process_while(token)

            elif token.get_mode() == ConditionalDecl.FOREVER:
                return self._process_forever(token)
                       
            elif token.get_mode() == ConditionalDecl.SWITCH:
                return self._process_switch(token)

            elif token.get_mode() == ConditionalDecl.CASE:
                return self._process_case(token)

            elif token.get_mode() == ConditionalDecl.DEFAULT:
                return self._process_default(token)

            else:
                raise ParseFatalException('unknown conditional decl type')
            
            return None

        elif isinstance(token, ScopeEnd):

            # handle closing braces on conditionals
            cond = self._get_scope_context()

            if isinstance(cond, Conditional) and \
               (self._get_depth() == 1):

                # we're closing a conditional
                if (cond.get_type() == Conditional.IF):
                    token = self._close_if(cond, token)

                elif cond.get_type() in (Conditional.IF_ELSE,
                                         Conditional.WHILE,
                                         Conditional.FOREVER):
                    token = self._close_conditional(cond, token)

                elif cond.get_type() == Conditional.DO_WHILE:
                    token = self._close_do(cond, token)

                elif cond.get_type() in (Conditional.SWITCH,
                                        Conditional.SWITCH_DEFAULT):

                    # if the current block is open, then this ScopeEnd just
                    # closes that block and not the entire switch statement
                    if cond.is_block_open():
                        # append the token and close the block
                        self._append_token_to_scope(token)
                        self._decrement_depth()
                        cond.close_block()
                        return None
                    else:
                        # we're closing the entire switch...
                        (token, depth) = self._pop_scope() 

                else:
                    raise ParseFatalException('unknown conditional type')

                if self._scope_depth() == 0:
                    return token
                else:
                    self._append_token_to_scope(token)
                    return None
                    
        # if we didn't handle the token, put it back on the queue and call the
        # base class to handle it
        self._put_token(token)
        return super(MOS6502Compiler, self)._parse_next()

    def _resolve_token(self, token):
        st = SymbolTable()

        if isinstance(token, InstructionLine):
            return (token, 0)
        elif isinstance(token, Conditional):
            tokens = []
            cond = token

            if cond.get_mode() == ConditionalDecl.FOREVER:
                # start the loop with a label
                lbl = Label.gen()
                tokens.append(lbl)

                # then append it's tokens and count them as unresolved
                tokens.extend(cond.get_tokens())

                # then append the hard jmp
                addr = Immediate(Immediate.TERMINAL, (Name(lbl.get_name())))
                tokens.append(InstructionLine.gen('jmp', Operand.ABS, addr=addr))

                return (tokens, len(cond.get_tokens()) + 1)
            else:
                raise ParseFatalException("unimplimented")

            return (token, 0)

        # if the token wasn't an InstructionLine, then call the base class to
        # handle the token.
        return super(MOS6502Compiler, self)._resolve_token(token)


class MOS6502Generator(Generator):

    def _process_instruction_line(self, line):
        output = []
        opcode = line.get_opcode()
        operand = line.get_operand()

        #output.append(opcode.emit(operand.get_mode()))

        # figure out the addressing mode
        if operand.get_mode() == Operand.IMP:
            pass
        if operand.get_mode() == Operand.ACC:
            pass
        if operand.get_mode() == Operand.IMM:
            pass
        if operand.get_mode() == Operand.ADDR:
            pass
        if operand.get_mode() == Operand.INDEXED:
            pass
        if operand.get_mode() == Operand.INDIRECT:
            pass
        if operand.get_mode() == Operand.IDX_IND:
            pass
        if operand.get_mode() == Operand.ZP_IND:
            pass

    def _process_token(self, token):

        # get the rom file
        romfile = self.romfile()

        # handle 6502 specific token
        if isinstance(token, InterruptStart):
            romfile.set_reset_interrupt(token.get_fn())
        elif isinstance(token, InterruptNMI):
            romfile.set_nmi_interrupt(token.get_fn())
        elif isinstance(token, InterruptIRQ):
            romfile.set_irq_interrupt(token.get_fn())
        elif isinstance(token, InstructionLine):
            self._process_instruction_line(token)
        elif isinstance(token, ConditionalDecl):
            pass
        else:
            # pass the token along to the generic generator
            super(MOS6502Generator, self)._process_token(token)

    def _initialize_rom(self):
        return super(MOS6502Generator, self)._initialize_rom()

    def _finalize_rom(self):
        pass

    def build_rom(self, tokens):

        # initialize the rom output pass
        self._initialize_rom()

        # process each of the tokens
        for t in tokens:
            self._process_token(t)

        # finalize the rom output pass
        self._finalize_rom()


class MOS6502(Target):

    BASIC_TYPES = [ 'byte', 'char', 'bool', 'word', 'pointer' ]

    def __init__(self):

        # init the base class 
        super(MOS6502, self).__init__()

    def opcodes(self):
        return Opcode.exprs()

    def keywords(self):
        return super(MOS6502, self).keywords()

    def basic_types(klass):
        # these are the basic type identifiers
        return [ Type(t) for t in MOS6502.BASIC_TYPES ]

    def basic_types_names(self):
        return MatchFirst([CaselessKeyword(t) for t in MOS6502.BASIC_TYPES])

    def conditions(self):
        return MatchFirst([CaselessKeyword(c) for c in ConditionalDecl.CONDITIONS])

    def preprocessor(self):
        return MOS6502Preprocessor()

    def compiler(self):
        return MOS6502Compiler()

    def generator(self):
        return MOS6502Generator()



