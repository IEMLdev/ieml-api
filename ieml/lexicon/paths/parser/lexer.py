import ply.lex as lxr
from sly import Lexer
import logging

from ..constants import COORDINATES_KINDS

logger = logging.getLogger(__name__)


class PathLexer(Lexer):
    tokens = (
        'COORD_KIND',
        'COORD_INDEX',
        'PLUS',
        'LPAREN',
        'RPAREN',
        'COLON'
    )

    ignore_whitespace = ' \t\n'

    COORD_KIND = r'[%s]' % ''.join(COORDINATES_KINDS)
    COORD_INDEX = r'\d+'
    PLUS = r'\+'
    LPAREN = r'\('
    RPAREN = r'\)'
    COLON = r':'

    # Error handling rule
    def error(self, t):
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        # TODO change skipping rule
        t.lexer.skip(1)
