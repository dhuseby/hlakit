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
import copy
from cStringIO import StringIO
from pyparsing import *
from enum import Enum
from type_ import Type
from label import Label
from struct_ import Struct
from typedef import Typedef
from immediate import Immediate
from variable import Variable
from function import Function
from functiondecl import FunctionDecl
from functioncall import FunctionCall
from functionreturn import FunctionReturn
from conditional import Conditional
from conditionaldecl import ConditionalDecl
from instructionline import InstructionLine
from codeblock import CodeBlock
from filemarkers import FileBegin, FileEnd
from scopemarkers import ScopeBegin, ScopeEnd
from symboltable import SymbolTable
from variableinitializer import VariableInitializer

class BasicScope(object):

    def __init__(self):
        self._tokens = []
        self._scope = None

    def append_token(self, token):
        self._tokens.append(token)

    def get_tokens(self):
        return self._tokens

    def set_scope(self, scope):
        self._scope = scope

    def get_scope(self):
        return self._scope

class Compiler(object):

    @classmethod
    def exprs(klass):
        e = []
        e.extend(klass.first_exprs())
        e.extend(klass.last_exprs())
        return e

    @classmethod
    def first_exprs(klass):
        e = []
        e.append(('return', FunctionReturn.exprs()))
        e.append(('enum', Enum.exprs()))
        e.append(('label', Label.exprs()))
        e.append(('typedef', Typedef.exprs()))
        e.append(('variable', Variable.exprs()))
        e.append(('struct', Struct.exprs()))
        e.append(('functiondecl', FunctionDecl.exprs()))
        e.append(('functioncall', FunctionCall.exprs()))
        e.append(('scopebegin', ScopeBegin.exprs()))
        e.append(('scopeend', ScopeEnd.exprs()))
        e.append(('initializer', VariableInitializer.exprs()))
        return e

    @classmethod
    def last_exprs(klass):
        e = []
        return e

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def __init__(self):
        if not hasattr(self, '_exprs'):
            self.set_exprs(self.__class__.exprs())
        if not hasattr(self, '_tokens'):
            self._tokens = []

    def reset_state(self):
        self.set_exprs(self.__class__.exprs())
        self._tokens = []

    def get_exprs(self):
        return getattr(self, '_exprs', [])

    def set_exprs(self, value):
        self._exprs = value

    def _get_tokens(self):
        return getattr(self, '_tokens', [])

    def _append_tokens(self, tokens):
        if not hasattr(self, '_tokens'):
            self._tokens = []
        self._tokens.extend(tokens)

    def _scan(self, tokens):
        # build the parser phase rules
        expr_or = MatchFirst([])
        for e in self.get_exprs():
            expr_or.append(e[1])
        parser = ZeroOrMore(expr_or)
        parser.ignore(cStyleComment | cppStyleComment)

        # run the pre-processor tokens through the parser phase
        cc_tokens = []
        for token in tokens:
            if isinstance(token, CodeBlock):
                # compile the code block
                cc_tokens.extend(parser.parseFile(StringIO(str(token))))
            else:
                # pass the token on
                cc_tokens.append(token)

        return cc_tokens

    def _push_scope(self, scope):
        self._scope_stack.insert(0, [scope, 0])

    def _pop_scope(self):
        scope = self._scope_stack.pop(0)
        return (scope[0], scope[1])

    def _increment_depth(self):
        self._scope_stack[0][1] += 1

    def _decrement_depth(self):
        self._scope_stack[0][1] -= 1

    def _get_depth(self):
        return self._scope_stack[0][1]

    def _get_scope_context(self):
        return self._scope_stack[0][0]

    def _get_fn_context(self):
        for i in range(0, len(self._scope_stack)):
            if isinstance(self._scope_stack[i][0], Function):
                return self._scope_stack[i][0]
        return None

    def _append_token_to_scope(self, token):
        # append the token to the current scope container
        self._get_scope_context().append_token(token)

    def _scope_depth(self):
        return len(self._scope_stack)

    def _peek_token(self):
        if len(self._in_tokens):
            return self._in_tokens[0]
        return None

    def _get_token(self):
        return self._in_tokens.pop(0)

    def _put_token(self, token):
        self._in_tokens.insert(0, token)

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

        # NOTE: we handle adding the symbols to the symbol table here rather
        # than in the Variable/Function classes themeselve so that we can
        # define them in the proper scope.  This function uses a state machine
        # to track the scope and therefore properly define the symbols...

        # get the next token
        token = self._get_token()
        
        # get the current scope container
        ctx = self._get_scope_context()

        if isinstance(token, FunctionDecl):

            # make sure all functions are declared at file scope
            if self._scope_depth() != 1:
                raise ParseFatalError('cannot declare a function here')

            # create the function container
            fn = Function(token)

            self._push_scope(fn)

            # get the next token, it should be ScopeBegin
            token = self._get_token()
            if isinstance(token, ScopeBegin):
                self._append_token_to_scope(token)
                self._increment_depth()

                # set the current symbol table scope to the function
                st.scope_push(str(fn.get_name()))

                # set the function's full scope name to the current scope
                fn.set_scope(st.current_namespace())

                return
            else:
                s = 'function decl not followed by {\n'
                s += str(fn) + '\n'
                s += str(token)
                raise ParseFatalException(s)

        elif isinstance(token, FunctionReturn):
            fn = self._get_fn_context()
            if fn is None:
                raise ParseFatalException('return in non-function block')

            if not isinstance(fn, Function):
                raise ParseFatalException('return keyword in non-function')

            if fn.get_noreturn():
                raise ParseFatalException('function declared noreturn has return in it')

            # tell the FunctionReturn what the type of parent function
            # it is in.  this allows it to emit the correct opcode
            token.set_type(fn.get_type()) 

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

        elif isinstance(token, InstructionLine):
            # set the scope for the instruction line so that it can properly
            # resolve symbolic names later
            token.set_scope(ctx.get_scope())
 
        elif isinstance(token, Variable):
            st.new_symbol(token)

            # peek at the next token to see if it is an initializer
            next_token = self._peek_token()
            if isinstance(next_token, VariableInitializer):

                # assign the value to the variable
                token.set_value(next_token.get_value())

                # consume the initializer token
                self._get_token()

        elif isinstance(token, FileBegin):
            # set the symbol table scope to the file
            st.scope_push(str(token.get_name()))
            return
        
        elif isinstance(token, FileEnd):
            # end the file scope 
            st.scope_pop()
            return
       
        # this is a standalone { token to localize names
        elif isinstance(token, ScopeBegin):
            self._increment_depth()
            self._append_token_to_scope(token)

            # start a new symbol table scope but not a fn/cond scope
            st.scope_push()

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
            else:
                self._append_token_to_scope(token)
                self._decrement_depth()
                if self._get_depth() == 0:

                    # end the symbol table scope 
                    st.scope_pop()

                    (token, depth) = self._pop_scope()

                    # if we were defining a function, then add it as a symbol
                    if isinstance(token, Function):
                        st.new_symbol(token)

        elif isinstance(token, Label):
            # add the label to the global scope
            st.new_symbol(token, st.GLOBAL_NAMESPACE)

        self._append_token_to_scope(token)

    def _parse(self, tokens):
        """ go through the list of tokens looking for well structred functions
        """
        self._scope_stack = []
        self._in_tokens = copy.copy(tokens)
        self._parsed_tokens = []
        self._one_line_count = 0

        # create a basic scope
        bs = BasicScope()
        self._push_scope(bs)
        # push anonymous scope
        st = SymbolTable()
        st.scope_push()
        bs.set_scope(st.current_namespace())

        while len(self._in_tokens):
            self._parse_next()

        (scope, depth) = self._pop_scope()
        if depth != 0:
            raise ParseFatalException('scope not properly terminated')

        # get the tokens from the base scope
        self._parsed_tokens = copy.copy(scope.get_tokens())

    def _resolve_if(self, cond):
        return None

    def _resolve_if_else(self, cond):
        return None

    def _resolve_while(self, cond):
        return None

    def _resolve_do_while(self, cond):
        return None

    def _resolve_forever(self, cond):
        return None

    def _resolve_switch(self, cond):
        return None

    def _get_fn_return(self, fn):
        return None

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

        elif isinstance(token, Function):
            tokens = []
            fn = token

            # TODO: if the function has no other functions that call it
            # then exit out early and don't emit the function into the
            # resolver output, thus removing the dead code.

            # start all functions with a label
            L1 = Label(name=fn.get_name(), fn=fn.get_name())
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

                t = self._get_fn_return(fn)
                if t:
                    if isinstance(t, list):
                        tokens.extend(t)
                    else:
                        tokens.append(t)

            # return the tokens and let
            return (tokens, len(tokens))

        elif isinstance(token, ScopeBegin):
            # eat the token
            return ([], 0)

        elif isinstance(token, ScopeEnd):
            # eat the token
            return ([], 0)

        return (token, 0)


    def _resolve(self, tokens):
        """ go through the parsed tokens and convert to all instruction lines
        and iterate through, resolving references until everything is resolved
        as much as can be.
        """
        out_tokens = tokens
        while True:
            report = []
            left_to_resolve = 0
            round_tokens = []
            for t in out_tokens:
                # try to resolve the token
                (token, unresolved) = self._resolve_token(t)

                if unresolved > 0:
                    report.append((token, unresolved))

                # count how many are left to resolve
                left_to_resolve = left_to_resolve + unresolved

                # process what we get back
                if isinstance(token, list):
                    round_tokens.extend(token)
                else:
                    round_tokens.append(token)

            # if nothing left to resolve, then we are done
            if left_to_resolve == 0:
                return round_tokens

            # detect the case where we've resolved as far as we can
            if (left_to_resolve > 0) and \
               (out_tokens == round_tokens):
                return round_tokens

            # otherwise, go around for another pass 
            out_tokens = round_tokens

    def get_output(self):
        return self._get_tokens()

    def get_scanner_output(self):
        return self._scanned_tokens

    def get_parser_output(self):
        return self._parsed_tokens

    def get_resolver_output(self):
        return self._resolved_tokens

    def output_debug_def(self):
        out = ''
        pt = self.get_scanner_output()
        out += '        scanner = [\n'
        first = True
        for p in pt:
            t = str(type(p))
            ti = t.rfind('.')
            out += '            (%s, "%s"),\n' % (t[ti+1:-2], str(p))
        out += '        ]\n'

        pt = self.get_parser_output()
        out += '        parser = [\n'
        for p in pt:
            t = str(type(p))
            ti = t.rfind('.')
            out += '            (%s, "%s"),\n' % (t[ti+1:-2], str(p))
        out += '        ]\n'

        pt = self.get_resolver_output()
        out += '        resolver = [\n'
        for p in pt:
            t = str(type(p))
            ti = t.rfind('.')
            out += '            (%s, "%s"),\n' % (t[ti+1:-2], str(p))
        out += '        ]\n'
        return out

    def compile(self, tokens, debug=False):
        # first we tokenize
        self._scanned_tokens = self._scan(tokens)

        # now we need to run the parsed tokens to the structure builder
        # this populates the symbol table and builds complete functions
        self._parse(self._scanned_tokens)

        # now resolve all references and convert everything to instruction lines
        self._resolved_tokens = self._resolve(self._parsed_tokens)

        self._tokens = self._resolved_tokens

        return self._resolved_tokens
