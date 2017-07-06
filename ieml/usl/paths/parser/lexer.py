import ply.lex as lxr
import logging

from ..constants import COORDINATES_KINDS

tokens = (
   'COORD_KIND',
   'COORD_INDEX',
   'PLUS',
   'LPAREN',
   'RPAREN',
   'COLON'
)


def get_lexer(module=None):
    t_COORD_KIND = r'[%s]'%''.join(COORDINATES_KINDS)
    t_COORD_INDEX = r'\d+'
    t_PLUS   = r'\+'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_COLON = r':'
    t_ignore  = ' \t\n'

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)


if __name__ == "__main__":
    # Test it out
    data = "t:sa:sa0:f"


    # Give the lexer some input
    lexer = get_lexer()
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)

