import ply.lex as lxr
import logging

tokens = (
   'TERM',
   'PLUS',
   'TIMES',
   'LPAREN',
   'RPAREN',
   'LBRACKET',
   'RBRACKET',
)

def get_lexer(module=None):
    t_TERM = r'[a-zA-Z\.\-\;\:\,\'\’\_]+'
    t_PLUS   = r'\+'
    t_TIMES   = r'\*'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET  = r'\]'

    t_ignore  = ' \t\n'

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)


if __name__ == "__main__":
    # Test it out
    data = "[([a.i.-] + [i.i.-]) * ([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]"

    # Give the lexer some input
    lexer = get_lexer()
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)

