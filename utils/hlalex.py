#!/usr/bin/env python
import sys
import re
import ply.lex as lex

preprocessor = {
    'define': 'PP_DEFINE',
    'undef': 'PP_UNDEF',
    'ifdef': 'PP_IFDEF',
    'ifndef': 'PP_IFNDEF',
    'else': 'PP_ELSE',
    'endif': 'PP_ENDIF',
    'include': 'PP_INCLUDE',
    'incbin': 'PP_INCBIN',
    'todo': 'PP_TODO',
    'warning': 'PP_WARNING',
    'error': 'PP_ERROR',
    'fatal': 'PP_FATAL',
    'ram': 'PP_RAM',
    'rom': 'PP_ROM',
    'org': 'PP_ORG',
    'end': 'PP_END',
    'banksize': 'PP_BANKSIZE',
    'bank': 'PP_BANK',
    'setpad': 'PP_SET_PAD',
    'align': 'PP_ALIGN'
    }

reserved = {
    'byte': 'TYPE',
    'char': 'TYPE',
    'bool': 'TYPE',
    'word': 'TYPE',
    'dword': 'TYPE',
    'pointer': 'TYPE',
    'struct': 'STRUCT',
    'typedef': 'TYPEDEF',
    'shared': 'SHARED',
    'noreturn': 'NORETURN',
    'return': 'RETURN',
    'inline': 'INLINE',
    'function': 'FUNCTION',
    'interrupt': 'INTERRUPT',
    'lo': 'LO',
    'hi': 'HI',
    'nylo': 'NYLO',
    'nyhi': 'NYHI',
    'sizeof': 'SIZEOF',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'forever': 'FOREVER',
    'switch': 'SWITCH',
    'case': 'CASE',
    'default': 'DEFAULT',
    'reg': 'REG',
    'near': 'NEAR',
    'far': 'FAR'
    }

conditionals = {
    'is': 'IS',
    'has': 'HAS',
    'no': 'NO',
    'not': 'NOT',
    'plus' : 'POSITIVE',
    'positive': 'POSITIVE',
    'minus': 'NEGATIVE',
    'negative': 'NEGATIVE',
    'greater': 'GREATER',
    'less': 'LESS',
    'overflow': 'OVERFLOW',
    'carry': 'CARRY',
    'nonzero': 'TRUE',
    'set': 'TRUE',
    'true': 'TRUE',
    '1': 'TRUE',
    'zero': 'FALSE',
    'unset': 'FALSE',
    'false': 'FALSE',
    '0': 'FALSE',
    'clear': 'FALSE',
    'equal': 'EQUAL'
    }
    
tokens = [  'STRING', 
            'DECIMAL', 
            'KILO', 
            'HEXC', 
            'HEXS', 
            'BINARY', 
            'RSHIFT',
            'LSHIFT',
            'GTE',
            'LTE',
            'NE',
            'EQ',
            'ID',
            'WS',
            'NL',
            'COMMENT' ] \
            + list(set(preprocessor.values())) \
            + list(set(reserved.values())) \
            + list(set(conditionals.values()))

literals = '.+-*/~!%><=&^|{}()[]#:,'

t_STRING    = r'\"(\\.|[^\"])*\"'
t_DECIMAL   = r'(0|[1-9][0-9]*)'
t_KILO      = r'(0|[1-9][0-9]*)[kK]'
t_HEXC      = r'0x[0-9a-fA-F]+'
t_HEXS      = r'\$[0-9a-fA-F]+'
t_BINARY    = r'%[01]+'
t_RSHIFT    = r'>>'
t_LSHIFT    = r'<<'
t_GTE       = r'>='
t_LTE       = r'<='
t_NE        = r'!='
t_EQ        = r'=='

class HLAToken(lex.LexToken):

    def __init__(self, tok):
        self.lexer = tok.lexer
        self.lexpos = tok.lexpos
        self.lineno = tok.lineno
        self.type = tok.type
        self.value = tok.value

    def __hash__(self):
        return self.value.__hash__()
    def __eq__(self, other):
        if isinstance(other, HLAToken) or isinstance(other, lex.LexToken):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        else:
            return self.value == str(other)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __gt__(self, other):
        if isinstance(other, HLAToken) or isinstance(other, lex.LexToken):
            return self.value > other.value
        elif isinstance(other, str):
            return self.value > other
        else:
            return self.value > str(other)
    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __cmp__(self, other):
        if self.__eq__(other):
            return 0
        elif self.__gt__(other):
            return 1
        else:
            return -1

def t_WS(t):
    r'[\r\t ]+'
    pass

def t_NL(t):
    r'\n'
    t.lexer.lineno += 1
    return HLAToken(t)
        
def t_COMMENT(t):
    r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
    t.lexer.lineno += t.value.count("\n")
    return HLAToken(t)

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = preprocessor.get(t.value.lower(), None) # check for preprocessor words
    if t.type != None:
        t.value = t.value.lower()
    else:
        t.type = reserved.get(t.value.lower(), None) # check for reserved words
        if t.type != None:
            t.value = t.value.lower()
        else:
            t.type = conditionals.get(t.value.lower(), None) # check for conditionals
            if t.type != None:
                t.value = t.value.lower()
            else:
                t.type = 'ID'
    return HLAToken(t)

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

class InputLine(object):
    def __init__(self, f, no, s):
        self._file = f
        self._pieces = [ (no, s) ]

    def add_piece(self, no, s):
        self._pieces.append((no, s))

    def rstrip(self, chars):
        

        return self.__str__().rstrip()

    def __str__(self):
        s = ''
        for (no, piece) in self._pieces:
            s += piece
        return s

    def __repr__(self):
        s = self._file + ':\n'
        for (no, piece) in self._pieces:
            s += "\t%d: %s\n" % (no, piece)
        return s

class InputFile(object):

    def __init__(self, f):
        self._file = f
        inf = open(f, 'r')
        self._cur_line = 0
        self._lines = inf.readlines()
        inf.close()

    def get_line(self):
        line = None
        done = False
        while not done:
            if self.eof():
                return line

            # get the current line
            l = InputLine(self._file, self._cur_line, self._lines[self._cur_line])

            # strip off slash
            l_strip = l.rstrip()
            if l_strip.endswith('\\'):
                l = l_strip.rstrip('\\')
            else:
                # no slash so we're done
                if len(l) > 0:
                    done = True

            if len(l) > 0:
                if line is None:
                    line = l
                else:
                    line += l

            self._cur_line += 1

        return line

    def eof(self):
        return self._cur_line >= len(self._lines)

    def __str__(self):
        return self._ifile


class Compiler(object):

    def __init__(self, lexer):
        self._pp = {}
        self._files = []
        self._lexer = lexer
        self._tokens = []
        self._cur_token = 0
        self._ignore_state = []
        self._pp_rule = None
        self._pp_prefix = re.compile(r'^\s*#[a-zA-Z_][a-zA-Z0-9_]*')

    def _start_file(self, ifile):
        print 'STARTING FILE: %s' % ifile
        self._files.append(InputFile(ifile))

    def _is_pp_line(self, line):
        return re.match(self._pp_prefix, line) != None

    def _scan_next_line(self):
        while True:
            line = self._files[-1].get_line()
            if line != None:
                break
            while self._files[-1].eof():
                print 'ENDING FILE: %s' % self._files[-1]
                self._files.pop()
                if len(self._files) == 0:
                    return None

        # do macro expansion of non-preprocessor lines here before feeding the line 
        # into the lexer
        if not self._is_pp_line(line) and self._pp_rule:
            matches = re.finditer(self._pp_rule, line)
            expanded_line = ''
            i = 0
            for match in matches:
                expanded_line += line[i:match.start()]
                if self._pp[match.group()] != None:
                    expanded_line += str(self._pp[match.group()])
                i = match.end()
            expanded_line += line[i:]
            line = expanded_line

        self._lexer.input(line)
        tokens = []
        for tok in iter(self._lexer.token, None):
            print "%s" % tok
            tokens.append(tok)

        return tokens

    def _peek_next_token(self):
        if self._tokens is None or (self._cur_token >= len(self._tokens)):
            tokens = self._scan_next_line()
            if tokens is None:
                return None
            self._tokens.extend(tokens)

        return self._tokens[self._cur_token]

    def _next_token(self, expect_type=None, expect_value=None):
        if self._tokens is None or (self._cur_token >= len(self._tokens)):
            tokens = self._scan_next_line()
            if tokens is None:
                return None
            self._tokens.extend(tokens)

        tok = self._tokens[self._cur_token]
        
        if expect_type != None:
            if isinstance(expect_type, tuple) or isinstance(expect_type, list):
                assert tok.type in expect_type, 'expected token one of "%s"' % expect_type
            else:
                assert tok.type == expect_type, 'expecting token type "%s"' % expect_type
        if expect_value != None:
            assert tok.value == expect_value, 'expecting token value "%s"' % expect_value

        self._cur_token += 1

        return tok

    def _get_next_token(self, expect_type=None, expect_value=None):
        if expect_type == 'NL':
            return self._next_token(expect_type, expect_value)
        else:
            # eat the newlines
            p = self._peek_next_token()
            if p is None:
                return None
            while p.type == 'NL':
                self._next_token('NL', None)
                p = self._peek_next_token()
                if p is None:
                    return None

            # finally get the next token with the expect type and value
            return self._next_token(expect_type, expect_value)

    def _ignore(self):
        if len(self._ignore_state) > 0:
            return self._ignore_state[-1]
        return False

    def compile(self, start_file):

        # open up the first file
        self._start_file(start_file)

        # kick off the parser
        self._parse_program()

        if len(self._ignore_state) > 0:
            raise Exception('unclosed #ifdef/#ifndef/#else')

    def _update_pp_rule(self):
        if len(self._pp.keys()):
            rule = '('
            for i in xrange(0, len(self._pp.keys())):
                if i > 0:
                    rule += '|'
                rule += r'\b' + "%s" % self._pp.keys()[i].value + r'\b'
            rule += ')'
            print "RULE: %s" % rule
            self._pp_rule = re.compile(rule)
        else:
            self._pp_rule = None

    def define(self, name, value):
        if value != None:
            print 'DEFINE %s = %s' % (name, value)
        else:
            print 'DEFINE %s' % name
        self._pp[name] = value
        self._update_pp_rule()

    def undef(self, name):
        if name in self._pp.keys():
            print 'UNDEF %s' % name
        del self._pp[name]
        self._update_pp_rule()

    def include(self, fname):
        # TODO: calculate absolute file path and call start file on it
        pass

    def dump_pp(self):
        for (k,v) in self._pp.iteritems():
            print "%s = %s" % (k, v)

    def _parse_program(self):
        '''
        program ::= pp_stmnt |
                    var_stmnt |
                    fn_stmnt
        '''

        self.ast = []

        while True:
            tok = self._peek_next_token()
            if tok is None:
                break
            elif tok.type == 'NL':
                # eat the NL's
                self._get_next_token('NL')
                continue

            #import pdb; pdb.set_trace()
            if tok.type == '#':
                ast = self._parse_pp_stmnt()
                if ast != None:
                    self.ast.append(ast)
            elif self._ignore():
                self._get_next_token()
            else:
                if tok.type in ('TYPE', 'STRUCT', 'SHARED', 'TYPEDEF'):
                    ast = self._parse_var_stmnt()
                    if ast != None:
                        self.ast.append(ast)
                elif tok.type in ('INLINE', 'FUNCTION', 'INTERRUPT'):
                    ast = self._parse_fn_stmnt()
                    if ast != None:
                        self.ast.append(ast)
                else:
                    #TODO: make the error output better
                    raise Exception('Invalid token: %s' % tok.value)

    def _parse_pp_stmnt(self):
        '''
        pp_stmnt ::= '#'  ( define_expr |
                            undef_expr |
                            pp_cond_expr |
                            include_expr |
                            incbin_expr |
                            msg_expr |
                            ram_expr |
                            rom_expr |
                            pad_expr |
                            align_expr )

        '''
        
        tok = self._get_next_token('#')

        tok = self._peek_next_token()
        if tok.type == 'PP_DEFINE':
            return self._parse_define_expr()
        elif tok.type == 'PP_UNDEF':
            return self._parse_undef_expr()
        elif tok.type in ('PP_IFDEF', 'PP_IFNDEF'):
            return self._parse_pp_cond_expr()
        elif tok.type == 'PP_ELSE':
            return self._parse_pp_else_expr()
        elif tok.type == 'PP_ENDIF':
            return self._parse_pp_endif_expr()
        elif tok.type == 'PP_INCLUDE':
            return self._parse_include_expr()
        elif tok.type == 'PP_INCBIN':
            return self._parse_incbin_expr()
        elif tok.type in ('PP_TODO', 'PP_WARNING', 'PP_ERROR', 'PP_FATAL'):
            return self._parse_msg_expr()
        elif tok.type == 'PP_RAM':
            return self._parse_ram_expr()
        elif tok.type == 'PP_ROM':
            return self._parse_rom_expr()
        elif tok.type == 'PP_SET_PAD':
            return self._parse_pad_expr()
        elif tok.type == 'PP_ALIGN':
            return self._parse_align_expr()
        else:
            raise Exception('Invalid preprocessor directive: %s' % tok.value)
  
    def _parse_var_stmnt(self):
        return None

    def _parse_fn_stmnt(self):
        return None

    def _parse_define_expr(self):
        '''
        define_expr ::= 'define' ID value_expr
        '''
        tok = self._get_next_token('PP_DEFINE', 'define')
        name = self._get_next_token('ID')
        value = None

        # check for new line
        tok = self._peek_next_token()
        if tok.type != 'NL':
            # try to parse the value expression
            value = self._parse_value_expr()
        else:
            # eat the new line
            self._get_next_token('NL')

        # define the pp variable
        if not self._ignore():
            self.define(name, value)
        return None

    def _parse_undef_expr(self):
        '''
        undef_expr ::= 'undef' ID
        '''
        tok = self._get_next_token('PP_UNDEF', 'undef')
        name = self._get_next_token('ID')
        if not self._ignore():
            self.undef(name)
        return None

    def _parse_pp_cond_expr(self):
        '''
        pp_cond_expr ::= 'ifdef'
        '''
        tok = self._get_next_token(['PP_IFDEF', 'PP_IFNDEF'])
        value = self._parse_value_expr()
        if tok.type == 'PP_IFDEF':
            if value:
                self._ignore_state.append(False)
            else:
                self._ignore_state.append(True)
        else:
            if value:
                self._ignore_state.append(True)
            else:
                self._ignore_state.append(False)
        return None

    def _parse_pp_else_expr(self):
        tok = self._get_next_token('PP_ELSE')
        if len(self._ignore_state) <= 0:
            raise Exception('unmatched #else')
        # flip the current ignore flag
        self._ignore_state[-1] = not self._ignore_state[-1]

    def _parse_pp_endif_expr(self):
        '''
        pp_endif_expr ::= 'endif'
        '''
        tok = self._get_next_token('PP_ENDIF')
        if len(self._ignore_state) <= 0:
            raise Exception('unmatched #endif')
        self._ignore_state.pop()

    def _parse_include_expr(self):
        '''
        include_expr ::= 'include' STRING
        '''
        tok = self._get_next_token('PP_INCLUDE', 'include')
        fname = self._parse_value_expr()
        if not self._ignore():
            self._start_file(fname)
        return None

    def _parse_incbin_expr(self):
        '''
        incbin_expr ::= 'incbin' STRING
        '''
        tok = self._get_next_token('PP_INCBIN', 'incbin')
        fname = self._parse_value_expr()
        if not self._ignore():
            # TODO return an ASTBlob
            pass
        return None

    def _parse_msg_expr(self):
        tok = self._get_next_token(['PP_TODO', 'PP_WARNING', 'PP_ERROR', 'PP_FATAL'])
        msg = ''
        if self._peek_next_token().type != 'NL':
            msg = self._parse_value_expr()

        if not self._ignore():
            if tok.type == 'PP_TODO':
                print 'TODO: %s' % msg
            elif tok.type == 'PP_WARNING':
                print 'WARNING: %s' % msg
            elif tok.type == 'PP_ERROR':
                print 'ERROR: %s' % msg
            else:
                raise Exception('FATAL: %s' % msg)

    def _parse_ram_expr(self):
        pass

    def _parse_rom_expr(self):
        pass

    def _parse_pad_expr(self):
        pass

    def _parse_align_expr(self):
        pass

    def _parse_value_expr(self):
        '''
        value_expr ::= value_term { + value_term }* |
                       value_term { - value_term }*
        '''
        l = self._parse_value_term()
        while(self._peek_next_token().type in ('+', '-')):
            op = self._get_next_token(['+', '-'])
            r = self._parse_value_term()
            if op.type == '+':
                l = l + r
            elif op.type == '-':
                l = l - r
        return l

    def _parse_value_term(self):
        '''
        value_term ::= value_factor { * value_factor }* |
                       value_factor { / value_factor }*
        '''
        l = self._parse_value_factor()
        while(self._peek_next_token().type in ('*', '/')):
            op = self._get_next_token()
            r = self._parse_value_factor()
            if op.type == '*':
                l = l * r
            elif op.type == '/':
                l = l / r
        return l

    def _parse_value_factor(self):
        '''
        value_factor ::= immediate_value |
                         "(" value_expr ")"
        '''
        tok = self._peek_next_token()
        if tok.type == '(':
            # parse parenthesized sub-expression
            self._get_next_token('(')
            tok = self._parse_value_expr()
            self._get_next_token(')')
            return tok
        else:
            if tok.type == '#':
                # parse #sizeof, #nylo, #nyhi, #lo, #hi
                self._get_next_token('#')
                return self._parse_immediate_expr()
            elif tok.type in ('STRING', 'DECIMAL', 'KILO', 'HEXC', 'HEXS', 'BINARY'):
                return self._parse_immediate_value()
            elif tok.type == 'ID':
                if tok.value in self._pp.keys():
                    self._get_next_token('ID')
                    return self._pp[tok.value]
                else:
                    raise Exception('Undefined macro expansion: %s' % tok.value)
            else:
                raise Exception('Invalid value: %s' % tok.value)

    def _parse_immediate_expr(self):
        '''
        immediate_expr ::= LO "(" value_expr ")" |
                           HI "(" value expr ")" |
                           NYLO "(" value_expr ")" |
                           NYHI "(" value_expr ")" |
                           SIZEOF "(" value_expr ")"
        '''
        self._get_next_token(['LO', 'HI', 'NYLO', 'NYHI', 'SIZEOF'])
        self._get_next_token('(')
        tok = self._parse_value_expr()
        self._get_next_token(')')

        # TODO apply the function and return the value
        return tok

    def _parse_immediate_value(self):
        '''
        immediate_value ::= string |
                            decimal |
                            kilo |
                            hexc |
                            hexs |
                            binary
        '''
        tok = self._get_next_token(['STRING', 'DECIMAL', 'KILO', 'HEXC', 'HEXS', 'BINARY'])
        if tok.type == 'STRING':
            return tok.value.strip('"')
            #value = ASTString(tok)
            #return str(value)
        else:
            return int(tok.value)
            #value = ASTInteger(tok)
            #return int(value)

if __name__ == "__main__":
    lexer = lex.lex()
    c = Compiler(lexer)
    c.compile(sys.argv[1])
    c.dump_pp()

