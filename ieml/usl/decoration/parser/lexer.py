import ply.lex as lxr
import logging
import re
from ieml.usl.constants import NAMES_TO_ADDRESS_WITH_VALENCE_IN_PROCESS, ROLE_NAMES_TO_SCRIPT, NAMES_TO_ADDRESS

logger = logging.getLogger(__name__)

ROLE_NAMES = list(ROLE_NAMES_TO_SCRIPT)
ROLE_NAMES_REGEX = r"({})".format('|'.join(map(re.escape, map(str, ROLE_NAMES))))

ROLES_SCRIPTS = list(NAMES_TO_ADDRESS)
ROLES_SCRIPTS_REGEX = r"({})".format('|'.join(map(re.escape, map(str, ROLES_SCRIPTS))))


tokens = (
    'SEPARATOR',
    'ROLE_TOKEN',
    'ROLE_NAME',
    'ROLE_MORPHEME',
    'LEXEME_POSITION',
    'POLYMORPHEME_POSITION',
    'MORPHEME',
    # 'BROAD_SEPARATOR'
)

# ROLE_SUFFIX_REGEX = r"(\s|\>|$)"
TERM_REGEX = r'([EUASBTOMFIacbedgfihkjmlonpsutwyx]\:?\.?\-?\'?\,?\’?\_?\;?\+?)+'
# TERM_REGEX = r'([EUASBTOMFIacbedgfihkjmlonpsutwyx][\:\.\-\'\’\,\_\;\+]+)+'
# t_BROAD_SEPARATOR = ROLE_SUFFIX_REGEX
# t_ROLE_MORPHEME  = ROLES_SCRIPTS_REGEX + ROLE_SUFFIX_REGEX
# + r'|{})'.format(TERM_REGEX, r'({}){}'.format('|'.join(map(re.escape, map(str, ROLES_SCRIPTS))), TERM_REGEX))

def get_lexer(module=None):
    t_SEPARATOR = r'\>'

    t_ROLE_TOKEN = r'role'

    t_LEXEME_POSITION  = r'(flexion|content)'
    t_POLYMORPHEME_POSITION = r'(group_\d|constant)'

    t_ROLE_NAME  = ROLE_NAMES_REGEX

    t_MORPHEME = r'(?!(flexion|content|group_\d|constant|role|{}))'.format('|'.join(map(re.escape, map(str, ROLE_NAMES)))) + TERM_REGEX
    t_ignore  = ' \t\n'

    # Error handling rule
    def t_error(t):
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging, debug=True, debuglog=logging, optimize=False,)
