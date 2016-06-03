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
   'L_CURLY_BRACKET',
   'R_CURLY_BRACKET',
   'SLASH',
   'L_ANGLE_BRACKET',
   'R_ANGLE_BRACKET',
   'LITERAL',

    # Script specific
    'LAYER0_MARK',
    'LAYER1_MARK',
    'LAYER2_MARK',
    'LAYER3_MARK',
    'LAYER4_MARK',
    'LAYER5_MARK',
    'LAYER6_MARK',

    'PRIMITIVE',
    'REMARKABLE_ADDITION',
    'REMARKABLE_MULTIPLICATION'
)


def get_script_lexer(module=None):
    t_LAYER0_MARK = r'\:'
    t_LAYER1_MARK = r'\.'
    t_LAYER2_MARK = r'\-'
    t_LAYER3_MARK = r'[\'\’]'
    t_LAYER4_MARK = r'\,'
    t_LAYER5_MARK = r'\_'
    t_LAYER6_MARK = r'\;'

    t_PRIMITIVE = r'[EUASBT]'
    t_REMARKABLE_ADDITION = r'[OMFI]'
    t_REMARKABLE_MULTIPLICATION = r'wo|wa|y|o|e|wu|we|u|a|i|j|g|s|b|t|h|c|k|m|n|p|x|d|f|l'
    t_PLUS = r'\+'

    t_ignore = ' \t\n'

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging, debug=1)


def get_lexer(module=None):
    t_TERM = r'[EUASBTOMFIacbedgfihkjmlonpsutwyx\.\-\;\:\,\'\’\_][EUASBTOMFIacbedgfihkjmlonpsutwyx\.\-\;\:\,\'\’\_\+]+'
    t_PLUS   = r'\+'
    t_TIMES   = r'\*'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET  = r'\]'
    t_L_CURLY_BRACKET = r'\{'
    t_R_CURLY_BRACKET = r'\}'
    t_SLASH = r'\/'
    t_LITERAL = r'\<.*\>'
#    t_USL_TAG = r'([A-Za-z0-9 _\./\\-]+)'

    t_ignore  = ' \t\n'

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)


if __name__ == "__main__":
    # Test it out
    data = '$/[([a.i.-] + [i.i.-]) * ([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]/' \
           '/[([a.i.-] + [i.i.-]) * ([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]/<"sup dude">$'

    # Give the lexer some input
    lexer = get_lexer()
    lexer.input(data)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)

