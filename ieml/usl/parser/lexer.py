import ply.lex as lxr
import logging

from ieml.constants import TERM_REGEX
from ieml.usl.constants import ROLE_REGEX

logger = logging.getLogger(__name__)


tokens = (
   'MORPHEME',
   'OLD_MORPHEME_GRAMMATICAL_CLASS',

   # 'PLUS',
   # 'TIMES',

   'LPAREN',
   'RPAREN',
   # 'LCHEVRON',
   'RCHEVRON',

   'LBRACKET',
   'RBRACKET',

   'GROUP_MULTIPLICITY',
   'EXCLAMATION_MARK',
   # 'HASH',
   'LITERAL',
   'USL_PATH',
   'DECORATION_VALUE'
   # 'L_CURLY_BRACKET',
   # 'R_CURLY_BRACKET',
   #
   # 'SLASH',
   # 'LITERAL',
)


def get_lexer(module=None):
    t_OLD_MORPHEME_GRAMMATICAL_CLASS = r'E:\.b\.E:[SBT]:\.-'

    t_MORPHEME = TERM_REGEX
    # t_PLUS   = r'\+'
    # t_TIMES   = r'\*'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    # t_LCHEVRON = r'\<'
    t_RCHEVRON = r'\>'

    t_LBRACKET = r'\['
    t_RBRACKET  = r'\]'
    t_EXCLAMATION_MARK  = r'\!'
    #

    t_LITERAL = r'\#(\\\#|[^\#])+\#'

    t_GROUP_MULTIPLICITY = r'm\d+'
    t_USL_PATH = r':({role_regex}(\s{role_regex})*:)?((flexion|content):)?(((group_\d|constant):)?{term_regex})?'.format(role_regex=ROLE_REGEX,
                                                                                                                        term_regex=TERM_REGEX)

    t_DECORATION_VALUE = r'"(\\"|[^"])+"'

    t_ignore  = '{} \t\n'

    # Error handling rule
    def t_error(t):
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)
