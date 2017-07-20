import ply.lex as lxr
import logging

TERM_REGEX = r'[EUASBTOMFIacbedgfihkjmlonpsutwyx][EUASBTOMFIacbedgfihkjmlonpsutwyx\.\-\;\:\,\'\’\_\+]+'

tokens = (
   'TERM',
   'PLUS',
   'TIMES',
   'LPAREN',
   'RPAREN',
   'LBRACKET',
   'RBRACKET',
   'L_CURLY_BRACKET',
   'R_CURLY_BRACKET',
   'SLASH',
   'LITERAL',
)


def get_lexer(module=None):
    t_TERM = TERM_REGEX
    t_PLUS   = r'\+'
    t_TIMES   = r'\*'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET  = r'\]'
    t_L_CURLY_BRACKET = r'\{'
    t_R_CURLY_BRACKET = r'\}'
    t_SLASH = r'\/'
    t_LITERAL = r'\<(\\\>|[^\>])+\>'
#    t_USL_TAG = r'([A-Za-z0-9 _\./\\-]+)'

    t_ignore  = ' \t\n'

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)


if __name__ == "__main__":
    # Test it out
    data = '{/[([a.i.-] + [i.i.-]) * ([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]/' \
           '/[([a.i.-] + [i.i.-]) * ([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]/<sup dude>}'

    # Give the lexer some input
    lexer = get_lexer()
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)

