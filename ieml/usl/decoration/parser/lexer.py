import ply.lex as lxr
import logging

from ieml.usl.constants import ROLE_REGEX
from ieml.usl.parser.lexer import TERM_REGEX

logger = logging.getLogger(__name__)

tokens = (
    'SEPARATOR',
    'ROLE',
    'LEXEME_POSITION',
    'POLYMORPHEME_POSITION',
    'MORPHEME',

)


def get_lexer(module=None):
    t_SEPARATOR = r'\:'

    t_LEXEME_POSITION  = r'(flexing|content)'
    t_POLYMORPHEME_POSITION = r'(group_\d|constant)'
    t_ROLE  = ROLE_REGEX

    t_MORPHEME = r'(?!(flexing|content|group_\d|constant))' + TERM_REGEX

    t_ignore  = '{} \t\n'

    # Error handling rule
    def t_error(t):
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)
