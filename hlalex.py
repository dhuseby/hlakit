#!/usr/bin/env python
import sys

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
            'COMMENT' ] + list(set(reserved.values())) + list(set(conditionals.values()))

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
t_ignore_COMMENT = r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'

t_ignore = " \t"

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, None) # check for reserved words 
    if t.type is None:
        t.type = conditionals.get(t.value, 'ID') # check for conditionals
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

import ply.lex as lex
lex.lex()

fin = open(sys.argv[1], 'r')
s = fin.read()
fin.close()
lex.input(s)

for tok in iter(lex.token, None):
    print repr(tok.type), repr(tok.value)


