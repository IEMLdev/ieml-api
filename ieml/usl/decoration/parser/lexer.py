import ply.lex as lxr
import logging

logger = logging.getLogger(__name__)

tokens = (
    'SEPARATOR',
    # 'ROLE',
    'LEXEME_POSITION',
    'POLYMORPHEME_POSITION',
    'MORPHEME',

)

TERM_REGEX = r'(?!E:\.b\.E:.:\.-)([EUASBTOMFIacbedgfihkjmlonpsutwyx]\:?\.?\-?\,?\'?\’?\_?\;?\+?)+'

def get_lexer(module=None):
    t_SEPARATOR = r'\:'

    t_LEXEME_POSITION  = r'(flexion|content)'
    t_POLYMORPHEME_POSITION = r'(group_\d|constant)'
    t_MORPHEME = r'(?!(flexion|content|group_\d|constant))' + TERM_REGEX

    # t_ROLE  = ROLE_REGEX


    t_ignore  = '{} \t\n'

    # Error handling rule
    def t_error(t):
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)
