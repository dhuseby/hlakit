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
from hlakit.common.functiontype import FunctionType
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd
from hlakit.common.symboltable import SymbolTable
from hlakit.common.numericvalue import NumericValue
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
        st = SymbolTable()

        # it's a scoped block
        self._append_token_to_scope(token)
        self._increment_depth()

        # open the symbol table scope and tell the conditional
        # what the scope name is for the block
        st.scope_push(st.get_namespace(cond.get_name()))
        cond.set_scope(st.current_namespace())

    def _close_scoped_block(self, cond, token):
        # append the token and close the block
        self._append_token_to_scope(token)
        self._decrement_depth()
        cond.close_block()

        # close the symbol table scope
        st = SymbolTable()
        st.scope_pop()

    def _close_conditional(self, cond, token):
        # close the scoped block
        self._close_scoped_block(cond, token)
        
        # this conditional is done, so pop the conditional and add
        # it to the parent scope
        (token, depth) = self._pop_scope()
        self._append_token_to_scope(token)

        if self._one_line_count > 0:
            self._put_token(ScopeEnd())
            self._one_line_count -= 1

    def _close_if(self, cond, token):
        # check to see if the one line if block is followed by an else 
        next = self._peek_token()

        if isinstance(next, ConditionalDecl) and \
           next.get_mode() == ConditionalDecl.ELSE:
            # yes it is, so close the if block and return None
            # so that the else block will be processed
            self._close_scoped_block(cond, token)
        else:
            # close conditional
            self._close_conditional(cond, token)

    def _close_do(self, cond, token):
        # check for the while
        w = self._get_token()
        if isinstance(w, ConditionalDecl) and \
           w.get_mode() == ConditionalDecl.WHILE:
            # replace the block's decl
            cond.replace_block_decl(w)
            self._close_conditional(cond, token)
        else:
            raise ParseFatalException('missing while after one-line do block')

    def _close_switch(self, cond, token):
        # decrement depth
        self._decrement_depth()

        # close the symbol table scope
        st = SymbolTable()
        st.scope_pop()

        # this conditional is done, so pop the conditional and add
        # it to the parent scope
        (token, depth) = self._pop_scope()
        self._append_token_to_scope(token)

        if depth != 0:
            raise ParseFatalException('switch block not closed properly')

        if self._one_line_count > 0:
            raise ParseFatalException('switch block with one-line count > 0')

    def _close_case(self, cond, token):
        # close the scoped block
        self._close_scoped_block(cond, token)

        # need to pop the case off
        (case, depth) = self._pop_scope()

        if depth != 0:
            raise ParseFatalException('case block not closed properly')

        if self._one_line_count > 0:
            raise ParseFatalException('case block with one-line count > 0')

        if len(case.get_blocks()) != 1:
            raise ParseFatalException('case conditional has more than one block')

        # get the parent switch conditional
        switch = self._get_scope_context()

        # so else decls can only happen immediately after an if block
        if (not isinstance(switch, Conditional)) or \
           (switch.get_type() not in (Conditional.SWITCH, Conditional.SWITCH_DEFAULT)):
            raise ParseFatalException('case block not in a switch decl')
        
        # check to make sure the if block isn't still open 
        if switch.is_block_open():
            raise ParseFatalException('case block in an open conditional block')

        # add it to the switch conditional
        switch.add_block(case.get_blocks()[0])

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

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._open_scoped_block(cond, ScopeBegin())
            self._put_token(token)
            self._one_line_count += 1

        elif isinstance(token, InstructionLine):
            # it's a one-liner, so manually add the ScopeBegin and the ScopeEnd
            # tokens around the one line and then close the if conditional
            self._open_scoped_block(cond, ScopeBegin())
            self._append_token_to_scope(token)
            self._put_token(ScopeEnd())

        else:
            # invalid token
            raise ParseFatalException('invalid token following if declaration')


    def _process_else(self, token):
        # get the current context
        cond = self._get_scope_context()

        # so else decls can only happen immediately after an if block
        if (not isinstance(cond, Conditional)) or \
           (cond.get_type() != Conditional.IF):
            raise ParseFatalException('else block without preceding if block')
        
        # check to make sure the if block isn't still open 
        if cond.is_block_open():
            raise ParseFatalException('else block in open if block')

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

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._open_scoped_block(cond, ScopeBegin())
            self._put_token(token)
            self._one_line_count += 1

        elif isinstance(token, InstructionLine):
            # one line else block so open a scoped block, add the token
            # then push a ScopeEnd() back on the stack so that it will
            # get closed properly
            self._open_scoped_block(cond, ScopeBegin())
            self._append_token_to_scope(token)
            self._put_token(ScopeEnd())
        
        else:
            # invalid token...
            raise ParseFatalException('invalid token after else')


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

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._open_scoped_block(cond, ScopeBegin())
            self._put_token(token)
            self._one_line_count += 1

        elif isinstance(token, InstructionLine):
            self._open_scoped_block(cond, ScopeBegin())
            self._append_token_to_scope(token)
            self._put_token(ScopeEnd())

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

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._open_scoped_block(cond, ScopeBegin())
            self._put_token(token)
            self._one_line_count += 1

        elif isinstance(token, InstructionLine):
            self._open_scoped_block(cond, ScopeBegin())
            self._append_token_to_scope(token)
            self._put_token(ScopeEnd())

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

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._open_scoped_block(cond, ScopeBegin())
            self._put_token(token)
            self._one_line_count += 1

        elif isinstance(token, InstructionLine):
            self._open_scoped_block(cond, ScopeBegin())
            self._append_token_to_scope(token)
            self._put_token(ScopeEnd())

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

        if not isinstance(token, ScopeBegin):
            raise ParseFatalException('switch decl not followed by curly brace')

        # eat the token since there is no open block to append it to

        # increment the depth
        self._increment_depth()

        # open the symbol table scope and tell the conditional
        # what the scope name is for the block
        st = SymbolTable()
        st.scope_push(st.get_namespace(cond.get_name()))
        cond.set_scope(st.current_namespace())

    def _process_case(self, token):
        # get the current context
        cond = self._get_scope_context()

        # so else decls can only happen immediately after an if block
        if (not isinstance(cond, Conditional)) or \
           (cond.get_type() != Conditional.SWITCH):
            raise ParseFatalException('case block not in a switch decl')
        
        # check to make sure the if block isn't still open 
        if cond.is_block_open():
            raise ParseFatalException('case block in an open conditional block')

        # start a new conditional
        cond = Conditional(self._get_depth())
        cond.set_type(Conditional.CASE)
        self._push_scope(cond)

        # the case block
        cond.new_block(token)

        # we have to check the token after the case decl to know what
        # to do next...
        token = self._get_token()
        if isinstance(token, ScopeBegin):
            # starting a scoped else block
            self._open_scoped_block(cond, token)

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._open_scoped_block(cond, ScopeBegin())
            self._put_token(token)
            self._one_line_count += 1

        elif isinstance(token, InstructionLine):
            # one line case block so add the token and close the block
            self._open_scoped_block(cond, ScopeBegin())
            self._append_token_to_scope(token)
            self._put_token(ScopeEnd())

        else:
            # invalid token...
            raise ParseFatalException('invalid token after case')

    def _process_default(self, token):
        # get the current context
        cond = self._get_scope_context()

        # so else decls can only happen immediately after an if block
        if (not isinstance(cond, Conditional)) or \
           (cond.get_type() != Conditional.SWITCH):
            raise ParseFatalException('default block not in a switch decl')
        
        # check to make sure the if block isn't still open 
        if cond.is_block_open():
            raise ParseFatalException('default block in an open conditional block')

        # update the condtional type
        cond.set_type(Conditional.SWITCH_DEFAULT)

        # start a new conditional
        cond = Conditional(self._get_depth())
        cond.set_type(Conditional.DEFAULT)
        self._push_scope(cond)

        # the case block
        cond.new_block(token)

        # we have to check the token after the case decl to know what
        # to do next...
        token = self._get_token()
        if isinstance(token, ScopeBegin):
            # starting a scoped else block
            self._open_scoped_block(cond, token)

        elif isinstance(token, ConditionalDecl):
            # put the token back and go around for another pass
            self._open_scoped_block(cond, ScopeBegin())
            self._put_token(token)
            self._one_line_count += 1

        elif isinstance(token, InstructionLine):
            # one line case block so add the token and close the block
            self._open_scoped_block(cond, ScopeBegin())
            self._append_token_to_scope(token)
            self._put_token(ScopeEnd())

        else:
            # invalid token...
            raise ParseFatalException('invalid token after case')

    def _parse_next(self):

        st = SymbolTable()

        # get the next token
        token = self._get_token()

        # get the current scope container
        ctx = self._get_scope_context()

        if isinstance(token, InstructionLine):
            # set the scope for the instruction line so that it can properly
            # resolve symbolic names later
            token.set_scope(ctx.get_scope())

        # handle the different types of conditional decls
        elif isinstance(token, ConditionalDecl):
            
            if token.get_mode() == ConditionalDecl.IF:
                self._process_if(token)
                return

            elif token.get_mode() == ConditionalDecl.ELSE:
                self._process_else(token)
                return

            elif token.get_mode() == ConditionalDecl.DO:
                self._process_do(token)
                return

            elif token.get_mode() == ConditionalDecl.WHILE:
                self._process_while(token)
                return

            elif token.get_mode() == ConditionalDecl.FOREVER:
                self._process_forever(token)
                return
                       
            elif token.get_mode() == ConditionalDecl.SWITCH:
                self._process_switch(token)
                return

            elif token.get_mode() == ConditionalDecl.CASE:
                self._process_case(token)
                return

            elif token.get_mode() == ConditionalDecl.DEFAULT:
                self._process_default(token)
                return

            else:
                raise ParseFatalException('unknown conditional decl type')
            
        elif isinstance(token, ScopeEnd):

            # handle closing braces on conditionals
            cond = self._get_scope_context()

            if isinstance(cond, Conditional) and \
               (self._get_depth() == 1):

                # we're closing a conditional
                if (cond.get_type() == Conditional.IF):
                    self._close_if(cond, token)
                    return

                elif cond.get_type() in (Conditional.IF_ELSE,
                                         Conditional.WHILE,
                                         Conditional.FOREVER):
                    self._close_conditional(cond, token)
                    return

                elif cond.get_type() == Conditional.DO_WHILE:
                    self._close_do(cond, token)
                    return

                elif cond.get_type() in (Conditional.CASE,
                                         Conditional.DEFAULT):
                    self._close_case(cond, token)
                    return

                elif cond.get_type() in (Conditional.SWITCH,
                                        Conditional.SWITCH_DEFAULT):
                    self._close_switch(cond, token)
                    return

                else:
                    raise ParseFatalException('unknown conditional type')

                self._append_token_to_scope(token)
                return
               
                    
        # if we didn't handle the token, put it back on the queue and call the
        # base class to handle it
        self._put_token(token)
        super(MOS6502Compiler, self)._parse_next()

    def _parse(self, tokens):
        self._one_line_count = 0
        super(MOS6502Compiler, self)._parse(tokens)

    def _resolve_if(self, cond):
        tokens = []
        st = SymbolTable()

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
        st.new_symbol(L1, st.GLOBAL_NAMESPACE)
        
        # look up the opcode string
        opcode = ConditionalDecl.OPCODES[distance][modifier][test]

        # build the instruction lines
        if distance == ConditionalDecl.NEAR:
            # use relative addressing

            # if the test passes, it will branch over the if body
            tokens.append(InstructionLine.new(opcode, Operand.REL, value=L1.get_name()))
        else:
            # use a hard jmp instructions

            # create a label for the start of the if body
            L2 = Label()
            st.new_symbol(L2, st.GLOBAL_NAMESPACE)

            # if the test passes, it will branch over the jmp to the start of the if body
            tokens.append(InstructionLine.new(opcode, Operand.REL, value=L2.get_name()))

            # if the test fails, it will execute this jmp to jump over the if body
            tokens.append(InstructionLine.new('jmp', Operand.ABS, addr=L1.get_name()))

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
        st = SymbolTable()

        # get the blocks from the conditional
        blocks = cond.get_blocks()
        if len(blocks) != 2:
            raise ParseFatalException('invalid number of conditional blocks')

        # get all of the details for the conditional test
        decl = blocks[1].get_decl()
        distance = decl.get_distance()
        modifier = decl.get_modifier()
        test = decl.get_condition()
       
        # L1 is the branch target at the start of the else block
        L1 = Label()
        st.new_symbol(L1, st.GLOBAL_NAMESPACE)
 
        # look up the opcode string
        opcode = ConditionalDecl.OPCODES[distance][modifier][test]

        # build the instruction lines
        if distance == ConditionalDecl.NEAR:
            # use relative addressing

            # if the test passes, it will branch to the start of the else body
            tokens.append(InstructionLine.new(opcode, Operand.REL, value=L1.get_name()))
        else:
            # use a hard jmp instructions

            # create a label for the start of the if body
            L2 = Label()
            st.new_symbol(L2, st.GLOBAL_NAMESPACE)

            # if the test passes, it will branch over the jmp to the start of the if body
            tokens.append(InstructionLine.new(opcode, Operand.REL, value=L2.get_name()))

            # if the above test fails, it will execute this jmp to jump over the if body
            # to the else body start   
            tokens.append(InstructionLine.new('jmp', Operand.ABS, addr=L1.get_name()))

            # add in the label for the start of the if body
            tokens.append(L2)

        # add in the if body
        tokens.extend(blocks[0].get_tokens())

        # create the label for after the else body
        L3 = Label()
        st.new_symbol(L3, st.GLOBAL_NAMESPACE)

        # add in the branch/jmp over the else body
        tokens.append(InstructionLine.new('jmp', Operand.ABS, addr=L3.get_name()))

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
        st = SymbolTable()

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
        st.new_symbol(L1, st.GLOBAL_NAMESPACE)

        # append the label for the start of the while loop
        tokens.append(L1)

        # create label for the end of while loop
        L2 = Label()
        st.new_symbol(L2, st.GLOBAL_NAMESPACE)
        
        # look up the opcode string
        opcode = ConditionalDecl.OPCODES[distance][modifier][test]

        # build the instruction lines
        if distance == ConditionalDecl.NEAR:
            # use relative addressing

            # if the test passes, it will branch over the while body
            tokens.append(InstructionLine.new(opcode, Operand.REL, value=L2.get_name()))
        else:
            # use a hard jmp instructions

            # create a label for the start of the while body
            L3 = Label()
            st.new_symbol(L3)

            # if the test passes, it will branch over the jmp to the start of the while body
            tokens.append(InstructionLine.new(opcode, Operand.REL, value=L3.get_name()))

            # if the test fails, it will execute this jmp to jump over the while body
            tokens.append(InstructionLine.new('jmp', Operand.ABS, addr=L2.get_name()))

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
        st = SymbolTable()

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
        st.new_symbol(L1, st.GLOBAL_NAMESPACE)

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
            tokens.append(InstructionLine.new(opcode, Operand.REL, value=L1.get_name()))
        else:
            # use a hard jmp instructions

            # create a label for the start of the while body
            L2 = Label()
            st.new_symbol(L2)

            # if the test passes, it will branch over the jmp to the start of the while body
            tokens.append(InstructionLine.new(opcode, Operand.REL, value=L2.get_name()))

            # if the test fails, it will execute this jmp to jump over the while body
            tokens.append(InstructionLine.new('jmp', Operand.ABS, addr=L1.get_name()))

            # add in the label for the start of the if body
            tokens.append(L2)

        # return the tokens and the number of tokens left to resolve
        return (tokens, len(tokens))

    def _resolve_forever(self, cond):
        tokens = []
        st = SymbolTable()

        # start the loop with a label
        L1 = Label()
        st.new_symbol(L1, st.GLOBAL_NAMESPACE)
        tokens.append(L1)

        # get the conditional blocks
        blocks = cond.get_blocks()
        if len(blocks) != 1:
            raise ParseFatalException('invalid number of blocks in conditional')

        # append the tokens of the forever body
        tokens.extend(blocks[0].get_tokens())

        # then append the hard jmp (6502 doesn't have 'bra')
        tokens.append(InstructionLine.new('jmp', Operand.ABS, addr=L1.get_name()))

        # return the tokens and the number left to resolve
        return (tokens, len(tokens))

    def _resolve_switch(self, cond):
        """ switch statements resolve to a series of if/else if blocks """
        tokens = []
        st = SymbolTable()

        # get the blocks from the conditional
        blocks = cond.get_blocks()

        # the blocks are in reverse order of their declaration (FILO)
        # so reverse them to get them back in order
        blocks.reverse()

        # the first block of a switch/case statement is an empty block
        # with just the switch decl.  we need to get the register we're
        # switching on...
        decl = blocks[0].get_decl()
        reg = decl.get_condition()
        
        # get the comparison opcode, NOTE: there is no distance or modifiers 
        # with switches
        compare_opcode = ConditionalDecl.SWITCH_OPCODES[reg]

        # get a label to just after the last case/default block
        L1 = Label()
        st.new_symbol(L1, st.GLOBAL_NAMESPACE)

        # add in the case blocks
        for i in range(1, len(blocks)):
            block = blocks[i]

            if block.get_mode() == ConditionalDecl.CASE:
                # for case blocks we have to first add a compare instruction
                # to compare the case parameter with the register specified
                # in the switch decl.  if the reg and value don't match, it
                # will branch to the label just after to case block.  if they
                # do match, the case block will be executed and then it will
                # jump to the label after the last case/default block

                # add the instruction to compare the reg with the immediate value
                # if the values are equal, the Z flag will be set
                imm = block.get_decl().get_condition()
                tokens.append(InstructionLine.new(compare_opcode, Operand.IMM, value=imm))

                # create a label for the beginning of the next case
                L2 = Label()
                st.new_symbol(L2, st.GLOBAL_NAMESPACE)

                # add in the branch instruction.  if the Z flag is set, the case
                # body will get executed, otherwise it will branch to the beginning
                # of the next case block
                tokens.append(InstructionLine.new('bne', Operand.REL, value=L2.get_name()))

                # append the case block body
                tokens.extend(block.get_tokens())

                # append a jmp to the label just after the last case/default block
                tokens.append(InstructionLine.new('jmp', Operand.ABS, addr=L1.get_name()))

                # append the label for the start of the next case
                tokens.append(L2)

            elif block.get_mode() == ConditionalDecl.DEFAULT:
                # for default blocks, we don't need to have this comparison
                # and branch because the default block is always executed if
                # none of the case blocks are executed.

                # append the default block body
                tokens.extend(block.get_tokens())

        # append the label after the end of the last case/switch block
        tokens.append(L1)

        # return the tokens and the number of tokens left to resolve
        return (tokens, len(tokens))

    def _resolve_token(self, token):
        st = SymbolTable()

        if isinstance(token, InstructionLine):
            if (not token.is_resolved()) and (not token.resolve()):
                return (token, 1)
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

            # TODO: if the function has no other functions that call it
            # then exit out early and don't emit the function into the
            # resolver output, thus removing the dead code.

            # start all functions with a label
            L1 = Label(fn.get_name())
            st.new_symbol(L1, st.GLOBAL_NAMESPACE)
            tokens.append(L1)

            # tell the function which label starts the function
            # this lets us later look up a function by name, then
            # get the start label and its address to know the address
            # to give to the jsr instruction
            fn.set_start_label(L1)

            # then append it's tokens and count them as unresolved
            tokens.extend(fn.get_tokens())

            # if the function isn't declared as 'noreturn', then
            # we need to add in the proper return instruction
            if not fn.get_noreturn():

                # for subroutines, we return with rts
                if fn.get_type() == FunctionType.SUBROUTINE:
                    tokens.append(InstructionLine.new('rts'))

                # for interrupts, we return with rti
                elif fn.get_type() == FunctionType.INTERRUPT:
                    tokens.append(InstructionLine.new('rti'))

            # return the tokens and let
            return (tokens, len(tokens))

        elif isinstance(token, FunctionCall):
            tokens = []

            # look up the function call
            fn = st.lookup_symbol(token.get_name(), token.get_scope())
            if fn is None:
                raise ParseFatalException('unknown function reference: %s' % token.get_name())
            fn_type = fn.get_type()

            if fn_type == FunctionType.MACRO:
                # paste the body of the inline function here, alias
                # the function parameters to the function variables
                # so they can be resolved.
                pass
            elif fn_type == FunctionType.SUBROUTINE:
                # see if the function has already been emitted and has a start label
                start_label = fn.get_start_label()
                if start_label is None:
                    # if it doesn't have a start label, then it hasn't been seen yet and
                    # it hasn't been been converted to InstructionLines and Labels.  So
                    # we need to convert the FunctionCall into an InstructionLine with
                    # an Immediate the references the name of the function that will later
                    # be resolved into an Immediate the references the function's
                    # start label by name.
                    i = InstructionLine.new('jsr', Operand.ABS, fn.get_name())
                else:
                    # if it has a start label, then transform it into an InstructionLine
                    # with an Immediate with the name of the label that it be resolved
                    # to an address later.
                    i = InstructionLine.new('jsr', Operand.ABS, start_label.get_name())

                # add the instruction line to the list
                tokens.append(i)

            # everything else, including interrupts, is an error
            else:
                raise ParseFatalException('invalid function type called')
            
            return (tokens, len(tokens))

        elif isinstance(token, FunctionReturn):
            tokens = []
            # for subroutines, we return with rts
            if token.get_type() == FunctionType.SUBROUTINE:
                tokens.append(InstructionLine.new('rts'))

            # for interrupts, we return with rti
            elif token.get_type() == FunctionType.INTERRUPT:
                tokens.append(InstructionLine.new('rti'))

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



