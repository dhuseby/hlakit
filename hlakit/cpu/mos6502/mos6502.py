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
from operand import Operand

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
       
        # switch decls start with an empty block that contains the switch decl
        cond.new_block(token)
        cond.close_block()

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
            if self._scope_depth() == 0: 
                return token
            else:
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

    def _resolve_if(self, cond):
        tokens = []

        # get the blocks from the conditional
        blocks = cond.get_blocks()
        if len(blocks) != 1:
            raise ParseFatalException('invalid number of conditional blocks')

        # get all of the details for the conditional test
        decl = blocks[0].get_decl()
        distance = decl.get_distance()
        modifier = decl.get_modifier()
        test = decl.get_condition()

        # create label L1 as the branch target after the if block
        L1 = Label()
        
        # look up the opcode string
        opcode = ConditionalDecl.OPCODES[distance][modifier][test]

        # build the instruction lines
        if distance == ConditionalDecl.NEAR:
            # use relative addressing

            # if the test passes, it will branch over the if body
            tokens.append(InstructionLine.new(opcode, Operand.REL, lbl=L1))
        else:
            # use a hard jmp instructions

            # create a label for the start of the if body
            L2 = Label()

            # if the test passes, it will branch over the jmp to the start of the if body
            tokens.append(InstructionLine.new(opcode, Operand.REL, lbl=L2))

            # if the test fails, it will execute this jmp to jump over the if body
            tokens.append(InstructionLine.new('jmp', Operand.ABS, lbl=L1))

            # add in the label for the start of the if body
            tokens.append(L2)

        # add in the if body
        tokens.extend(blocks[0].get_tokens())

        # add in the label for after the if body
        tokens.append(L1)

        # return the tokens and the number of tokens left to resolve
        return (tokens, len(tokens))

    def _resolve_if_else(self, cond):
        tokens = []

        # get the blocks from the conditional
        blocks = cond.get_blocks()
        if len(blocks) != 2:
            raise ParseFatalException('invalid number of conditional blocks')

        # get all of the details for the conditional test
        decl = blocks[0].get_decl()
        distance = decl.get_distance()
        modifier = decl.get_modifier()
        test = decl.get_condition()
       
        # L1 is the branch target at the start of the else block
        L1 = Label()
 
        # look up the opcode string
        opcode = ConditionalDecl.OPCODES[distance][modifier][test]

        # build the instruction lines
        if distance == ConditionalDecl.NEAR:
            # use relative addressing

            # if the test passes, it will branch to the start of the else body
            tokens.append(InstructionLine.new(opcode, Operand.REL, lbl=L1))
        else:
            # use a hard jmp instructions

            # create a label for the start of the if body
            L2 = Label()

            # if the test passes, it will branch over the jmp to the start of the if body
            tokens.append(InstructionLine.new(opcode, Operand.REL, lbl=L2))

            # if the above test fails, it will execute this jmp to jump over the if body
            # to the else body start   
            tokens.append(InstructionLine.new('jmp', Operand.ABS, lbl=L1))

            # add in the label for the start of the if body
            tokens.append(L2)

        # add in the if body
        tokens.extend(blocks[0].get_tokens())

        # create the label for after the else body
        L3 = Label()

        # add in the branch/jmp over the else body
        tokens.append(InstructionLine.new('jmp', Operand.ABS, lbl=L3))

        # add in the label for the start of the else body
        tokens.append(L1)

        # add in the else body
        tokens.extend(blocks[1].get_tokens())

        # add in the label for the end of the else body
        tokens.append(L3)

        # return the tokens and the number of tokens left to resolve
        return (tokens, len(tokens))

    def _resolve_while(self, cond):
        tokens = []

        # get the blocks from the conditional
        blocks = cond.get_blocks()
        if len(blocks) != 1:
            raise ParseFatalException('invalid number of conditional blocks')

        # get all of the details for the conditional test
        decl = blocks[0].get_decl()
        distance = decl.get_distance()
        modifier = decl.get_modifier()
        test = decl.get_condition()

        # create label for the start of the while loop
        L1 = Label()

        # append the label for the start of the while loop
        tokens.append(L1)

        # create label for the end of while loop
        L2 = Label()
        
        # look up the opcode string
        opcode = ConditionalDecl.OPCODES[distance][modifier][test]

        # build the instruction lines
        if distance == ConditionalDecl.NEAR:
            # use relative addressing

            # if the test passes, it will branch over the while body
            tokens.append(InstructionLine.new(opcode, Operand.REL, lbl=L2))
        else:
            # use a hard jmp instructions

            # create a label for the start of the while body
            L3 = Label()

            # if the test passes, it will branch over the jmp to the start of the while body
            tokens.append(InstructionLine.new(opcode, Operand.REL, lbl=L3))

            # if the test fails, it will execute this jmp to jump over the while body
            tokens.append(InstructionLine.new('jmp', Operand.ABS, lbl=L2))

            # add in the label for the start of the if body
            tokens.append(L3)

        # add in the while body
        tokens.extend(blocks[0].get_tokens())

        # add in the label for after the if body
        tokens.append(L2)

        # return the tokens and the number of tokens left to resolve
        return (tokens, len(tokens))

    def _resolve_do_while(self, cond):
        tokens = []

        # get the blocks from the conditional
        blocks = cond.get_blocks()
        if len(blocks) != 1:
            raise ParseFatalException('invalid number of conditional blocks')

        # get all of the details for the conditional test
        decl = blocks[0].get_decl()
        distance = decl.get_distance()
        modifier = decl.get_modifier()
        test = decl.get_condition()

        # create label for the start of the do..while loop
        L1 = Label()

        # append the label for the start of the do..while loop
        tokens.append(L1)

        # add in the do..while body
        tokens.extend(blocks[0].get_tokens())

        # look up the opcode string
        opcode = ConditionalDecl.OPCODES[distance][modifier][test]

        # build the instruction lines
        if distance == ConditionalDecl.NEAR:
            # use relative addressing

            # if the test passes, it will branch to the beginning of the while loop
            tokens.append(InstructionLine.new(opcode, Operand.REL, lbl=L1))
        else:
            # use a hard jmp instructions

            # create a label for the start of the while body
            L2 = Label()

            # if the test passes, it will branch over the jmp to the start of the while body
            tokens.append(InstructionLine.new(opcode, Operand.REL, lbl=L2))

            # if the test fails, it will execute this jmp to jump over the while body
            tokens.append(InstructionLine.new('jmp', Operand.ABS, lbl=L1))

            # add in the label for the start of the if body
            tokens.append(L2)

        # return the tokens and the number of tokens left to resolve
        return (tokens, len(tokens))

    def _resolve_forever(self, cond):
        tokens = []

        # start the loop with a label
        L1 = Label()
        tokens.append(L1)

        # get the conditional blocks
        blocks = cond.get_blocks()
        if len(blocks) != 1:
            raise ParseFatalException('invalid number of blocks in conditional')

        # append the tokens of the forever body
        tokens.extend(blocks[0].get_tokens())

        # then append the hard jmp (6502 doesn't have 'bra')
        tokens.append(InstructionLine.new('jmp', Operand.ABS, lbl=L1))

        # return the tokens and the number left to resolve
        return (tokens, len(tokens))

    def _resolve_switch(self, cond):
        """ switch statements resolve to a series of if/else if blocks """
        tokens = []

        # get the blocks from the conditional
        blocks = cond.get_blocks()

        # the first block of a switch/case statement is an empty block
        # with just the switch decl.  we need to get the register we're
        # switching on...
        decl = blocks[0].get_decl()
        reg = decl.get_condition()
        
        # get the comparison opcode, NOTE: there is no distance or modifiers 
        # with switches
        compare_opcode = ConditionalDecl.SWITCH_OPCODES[reg]

        # add in the case blocks
        for i in range(1, len(blocks)):
            block = blocks[i]

            # add the instruction to compare the reg with the immediate value
            # if the values are equal, the Z flag will be set
            imm = block.get_decl().get_condition()
            if not isinstance(imm, NumericValue):
                import pdb; pdb.set_trace()
            
            tokens.append(InstructionLine.new(compare_opcode, Operand.IMM, value=imm))

            # create a label for the beginning of the next case
            L1 = Label()

            # add in the branch instruction.  if the Z flag is set, the case
            # body will get executed, otherwise it will branch to the beginning
            # of the next case block
            tokens.append(InstructionLine.new('bne', Operand.REL, lbl=L1))

            # append the case block body
            tokens.extend(block.get_tokens())

            # append the label for the start of the next case
            tokens.append(L1)

        # return the tokens and the number of tokens left to resolve
        return (tokens, len(tokens))


    def _resolve_token(self, token):
        st = SymbolTable()

        if isinstance(token, InstructionLine):
            # TODO: resolve the instruction lines...
            return (token, 0)

        elif isinstance(token, Conditional):
            tokens = []
            cond = token

            if cond.get_type() == Conditional.IF:
                return self._resolve_if(cond)
           
            elif cond.get_type() == Conditional.IF_ELSE:
                return self._resolve_if_else(cond)

            elif cond.get_type() == Conditional.WHILE:
                return self._resolve_while(cond)

            elif cond.get_type() == Conditional.DO_WHILE:
                return self._resolve_do_while(cond)

            elif cond.get_type() == Conditional.FOREVER:
                return self._resolve_forever(cond)

            elif cond.get_type() in (Conditional.SWITCH,
                                     Conditional.SWITCH_DEFAULT):
                return self._resolve_switch(cond)
            else:
                raise ParseFatalException("unimplimented conditional type")

            return (token, 0)

        elif isinstance(token, Function):
            tokens = []
            fn = token

            # start all functions with a label
            tokens.append(Label(fn.get_name()))

            # then append it's tokens and count them as unresolved
            tokens.extend(fn.get_tokens())

            # add rts if the function isn't declared as 'noreturn'
            if not fn.get_noreturn():
                tokens.append(InstructionLine.new('rts'))

            # return the tokens and let
            return (tokens, len(tokens))

        elif isinstance(token, FunctionCall):
            tokens = []

            # look up the function call
            fn = st[token.get_name()]
            if fn is None:
                import pdb; pdb.set_trace()
            fn_type = fn.get_type().get_name()

            if fn_type == 'inline':
                # paste the body of the inline function here, alias
                # the function parameters to the function variables
                # so they can be resolved.
                import pdb; pdb.set_trace()
            elif fn_type == 'function':
                # create the label we want to jump to
                L1 = Label(fn.get_name())

                # create an instruction line that calls the function
                tokens.append(InstructionLine.new('jsr', Operand.ABS, lbl=L1))
            else:
                raise ParseFatalException('invalid function type called')
            
            return (tokens, len(tokens))


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



