import ply.lex as lxr
import logging

tokens = (
   'IEML_OBJECT',
   # 'L_CURLY_BRACKET',
   # 'R_CURLY_BRACKET',
)


def get_lexer(module=None):
    t_IEML_OBJECT = r'.+'
    # t_L_CURLY_BRACKET = r'\{'
    # t_R_CURLY_BRACKET = r'\}'

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

