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
from hlakit.common.compiler import Compiler as CommonCompiler
from hlakit.common.label import Label
from hlakit.common.conditional import Conditional
from hlakit.common.function import Function
from hlakit.common.functiondecl import FunctionDecl
from hlakit.common.functioncall import FunctionCall
from hlakit.common.functionreturn import FunctionReturn
from hlakit.common.functiontype import FunctionType
from hlakit.common.scopemarkers import ScopeBegin, ScopeEnd
from hlakit.common.symboltable import SymbolTable
from instructionline import InstructionLine
from conditionaldecl import ConditionalDecl
from operand import Operand

class Compiler(CommonCompiler):

    @classmethod
    def first_exprs(klass):
        e = []

        # add in 6502 specific compiler parse rules
        e.append(('instructionline', InstructionLine.exprs()))
        e.append(('conditionaldecl', ConditionalDecl.exprs()))

        # start with the first base compiler rules 
        e.extend(CommonCompiler.first_exprs())
       
        return e

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
        L1 = Label(fn=cond.get_fn())
        st.new_symbol(L1, st.GLOBAL_NAMESPACE)
        
        # look up the opcode string
        opcode = ConditionalDecl.OPCODES[distance][modifier][test]

        # build the instruction lines
        if distance == ConditionalDecl.NEAR:
            # use relative addressing

            # if the test passes, it will branch over the if body
            tokens.append(InstructionLine.new(opcode, fn=cond.get_fn(), 
                                              mode=Operand.REL, value=L1.get_name()))
        else:
            # use a hard jmp instructions

            # create a label for the start of the if body
            L2 = Label(fn=cond.get_fn())
            st.new_symbol(L2, st.GLOBAL_NAMESPACE)

            # if the test passes, it will branch over the jmp to the start of the if body
            tokens.append(InstructionLine.new(opcode, fn=cond.get_fn(), 
                                              mode=Operand.REL, value=L2.get_name()))

            # if the test fails, it will execute this jmp to jump over the if body
            tokens.append(InstructionLine.new('jmp', fn=cond.get_fn(), 
                                              mode=Operand.ABS, addr=L1.get_name()))

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
        L1 = Label(fn=cond.get_fn())
        st.new_symbol(L1, st.GLOBAL_NAMESPACE)
 
        # look up the opcode string
        opcode = ConditionalDecl.OPCODES[distance][modifier][test]

        # build the instruction lines
        if distance == ConditionalDecl.NEAR:
            # use relative addressing

            # if the test passes, it will branch to the start of the else body
            tokens.append(InstructionLine.new(opcode, fn=cond.get_fn(), 
                                              mode=Operand.REL, value=L1.get_name()))
        else:
            # use a hard jmp instructions

            # create a label for the start of the if body
            L2 = Label(fn=cond.get_fn())
            st.new_symbol(L2, st.GLOBAL_NAMESPACE)

            # if the test passes, it will branch over the jmp to the start of the if body
            tokens.append(InstructionLine.new(opcode, fn=cond.get_fn(), 
                                              mode=Operand.REL, value=L2.get_name()))

            # if the above test fails, it will execute this jmp to jump over the if body
            # to the else body start   
            tokens.append(InstructionLine.new('jmp', fn=cond.get_fn(), 
                                              mode=Operand.ABS, addr=L1.get_name()))

            # add in the label for the start of the if body
            tokens.append(L2)

        # add in the if body
        tokens.extend(blocks[0].get_tokens())

        # create the label for after the else body
        L3 = Label(fn=cond.get_fn())
        st.new_symbol(L3, st.GLOBAL_NAMESPACE)

        # add in the branch/jmp over the else body
        tokens.append(InstructionLine.new('jmp', fn=cond.get_fn(), 
                                          mode=Operand.ABS, addr=L3.get_name()))

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
        L1 = Label(fn=cond.get_fn())
        st.new_symbol(L1, st.GLOBAL_NAMESPACE)

        # append the label for the start of the while loop
        tokens.append(L1)

        # create label for the end of while loop
        L2 = Label(fn=cond.get_fn())
        st.new_symbol(L2, st.GLOBAL_NAMESPACE)
        
        # look up the opcode string
        opcode = ConditionalDecl.OPCODES[distance][modifier][test]

        # build the instruction lines
        if distance == ConditionalDecl.NEAR:
            # use relative addressing

            # if the test passes, it will branch over the while body
            tokens.append(InstructionLine.new(opcode, fn=cond.get_fn(), 
                                              mode=Operand.REL, value=L2.get_name()))
        else:
            # use a hard jmp instructions

            # create a label for the start of the while body
            L3 = Label(fn=cond.get_fn())
            st.new_symbol(L3)

            # if the test passes, it will branch over the jmp to the start of the while body
            tokens.append(InstructionLine.new(opcode, fn=cond.get_fn(), 
                                              mode=Operand.REL, value=L3.get_name()))

            # if the test fails, it will execute this jmp to jump over the while body
            tokens.append(InstructionLine.new('jmp', fn=cond.get_fn(), 
                                              mode=Operand.ABS, addr=L2.get_name()))

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
        L1 = Label(fn=cond.get_fn())
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
            tokens.append(InstructionLine.new(opcode, fn=cond.get_fn(), 
                                              mode=Operand.REL, value=L1.get_name()))
        else:
            # use a hard jmp instructions

            # create a label for the start of the while body
            L2 = Label(fn=cond.get_fn())
            st.new_symbol(L2)

            # if the test passes, it will branch over the jmp to the start of the while body
            tokens.append(InstructionLine.new(opcode, fn=cond.get_fn(), 
                                              mode=Operand.REL, value=L2.get_name()))

            # if the test fails, it will execute this jmp to jump over the while body
            tokens.append(InstructionLine.new('jmp', fn=cond.get_fn(), 
                                              mode=Operand.ABS, addr=L1.get_name()))

            # add in the label for the start of the if body
            tokens.append(L2)

        # return the tokens and the number of tokens left to resolve
        return (tokens, len(tokens))

    def _resolve_forever(self, cond):
        tokens = []
        st = SymbolTable()

        # start the loop with a label
        L1 = Label(fn=cond.get_fn())
        st.new_symbol(L1, st.GLOBAL_NAMESPACE)
        tokens.append(L1)

        # get the conditional blocks
        blocks = cond.get_blocks()
        if len(blocks) != 1:
            raise ParseFatalException('invalid number of blocks in conditional')

        # append the tokens of the forever body
        tokens.extend(blocks[0].get_tokens())

        # then append the hard jmp (6502 doesn't have 'bra')
        tokens.append(InstructionLine.new('jmp', fn=cond.get_fn(), 
                                          mode=Operand.ABS, addr=L1.get_name()))

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
        L1 = Label(fn=cond.get_fn())
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
                tokens.append(InstructionLine.new(compare_opcode, fn=cond.get_fn(), 
                                                  mode=Operand.IMM, value=imm))

                # create a label for the beginning of the next case
                L2 = Label(fn=cond.get_fn())
                st.new_symbol(L2, st.GLOBAL_NAMESPACE)

                # add in the branch instruction.  if the Z flag is set, the case
                # body will get executed, otherwise it will branch to the beginning
                # of the next case block
                tokens.append(InstructionLine.new('bne', fn=cond.get_fn(), 
                                                  mode=Operand.REL, value=L2.get_name()))

                # append the case block body
                tokens.extend(block.get_tokens())

                # append a jmp to the label just after the last case/default block
                tokens.append(InstructionLine.new('jmp', fn=cond.get_fn(), 
                                                  mode=Operand.ABS, addr=L1.get_name()))

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

    def _get_fn_return(self, fn):
        # for subroutines, we return with rts
        if fn.get_type() == FunctionType.SUBROUTINE:
            return InstructionLine.new('rts', fn=fn.get_name())

        # for interrupts, we return with rti
        elif fn.get_type() == FunctionType.INTERRUPT:
            return InstructionLine.new('rti', fn=fn.get_name())

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
                    i = InstructionLine.new('jsr', fn=token.get_fn(), 
                                            mode=Operand.ABS, addr=fn.get_name())
                else:
                    # if it has a start label, then transform it into an InstructionLine
                    # with an Immediate with the name of the label that it be resolved
                    # to an address later.
                    i = InstructionLine.new('jsr', fn=token.get_fn(), 
                                            mode=Operand.ABS, addr=start_label.get_name())

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
                tokens.append(InstructionLine.new('rts', fn=token.get_fn()))

            # for interrupts, we return with rti
            elif token.get_type() == FunctionType.INTERRUPT:
                tokens.append(InstructionLine.new('rti', fn=token.get_fn()))

            return (tokens, len(tokens))

        # if the token wasn't an InstructionLine, then call the base class to
        # handle the token.
        return super(Compiler, self)._resolve_token(token)


