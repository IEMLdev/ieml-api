import ply.lex as lxr
import logging

logger = logging.getLogger(__name__)

TERM_REGEX = r'[EUASBTOMFIacbedgfihkjmlonpsutwyx][EUASBTOMFIacbedgfihkjmlonpsutwyx\.\-\;\:\,\'\’\_\+]+'

tokens = (
   'MORPHEME',

   'PLUS',
   'TIMES',

   'LPAREN',
   'RPAREN',
   'LCHEVRON',
   'RCHEVRON',

   'LBRACKET',
   'RBRACKET',

    'GROUP_MULTIPLICITY'

   # 'L_CURLY_BRACKET',
   # 'R_CURLY_BRACKET',
   #
   # 'SLASH',
   # 'LITERAL',
)


def get_lexer(module=None):
    t_MORPHEME = TERM_REGEX
    t_PLUS   = r'\+'
    t_TIMES   = r'\*'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_LCHEVRON = r'\<'
    t_RCHEVRON = r'\>'

    t_LBRACKET = r'\['
    t_RBRACKET  = r'\]'
    # t_L_CURLY_BRACKET = r'\{'
    # t_R_CURLY_BRACKET = r'\}'
    # t_SLASH = r'\/'
    # t_LITERAL = r'\<(\\\>|[^\>])+\>'

    t_GROUP_MULTIPLICITY = r'm\d+'

    t_ignore  = '{} \t\n'

    # Error handling rule
    def t_error(t):
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)
