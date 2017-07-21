import ply.lex as lxr
import logging

from ..constants import COORDINATES_KINDS

logger = logging.getLogger(__name__)

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
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)
