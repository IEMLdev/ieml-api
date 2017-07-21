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
        logger = logging.getLogger(__name__)
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)
