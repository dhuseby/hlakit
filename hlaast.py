class ASTNode(object):

    def __init__(self, lex_token = None):
        self._lex_token = lex_token

class ASTValue(ASTNode):

    def __init__(self, value, lex_token = None):
        self._value = value

    def __getattr__(self, key):
        return self._value.__getattr__(key)

    def __setattr__(self, key, value):
        return self._value.__setattr__(key, value)

class ASTInteger(ASTValue):

    def __init__(self, lex_token):
        assert lex_token.type in ('DECIMAL', 'KILO', 'HEXC', 'HEXS', 'BINARY'), 'Token is not a number value'

        if lex_token.type == 'DECIMAL':
            # 12345
            value = int(lex_token.value)
        elif lex_token.type == 'KILO':
            # 234K
            value = int(lex_token.value.strip('Kk')) * 1024
        elif lex_token.type == 'HEXC':
            # 0xA5F3
            value = int(lex_token.value[2:], 16)
        elif lex_token.type == 'HEXS':
            # $A5F3
            value = int(lex_token.value[1:], 16)
        elif lex_token.type == 'BINARY':
            # %10110110
            value = int(lex_token.value[1:], 2)

        super(ASTInteger, self).__init__(value, lex_token)

class ASTString(ASTValue):

    def __init__(self, lex_token):
        assert lex_token.type == 'STRING'

        value = lex_token.value.strip('"')
        super(ASTString, self).__init__(value, lex_token)



