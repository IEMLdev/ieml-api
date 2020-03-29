import logging

from sly import Lexer
from sly.lex import Token

from ..constants import ROLE_REGEX
from ...constants import TERM_REGEX

logger = logging.getLogger(__name__)


class USLLexer(Lexer):
    tokens = (
        'MORPHEME',
        'OLD_MORPHEME_GRAMMATICAL_CLASS',

        'LPAREN',
        'RPAREN',
        'RCHEVRON',

        'LBRACKET',
        'RBRACKET',

        'GROUP_MULTIPLICITY',
        'EXCLAMATION_MARK',
        'LITERAL',
        'USL_PATH',
        'DECORATION_VALUE'
    )
    OLD_MORPHEME_GRAMMATICAL_CLASS = r'E:\.b\.E:[SBT]:\.-'

    MORPHEME = TERM_REGEX
    LPAREN  = r'\('
    RPAREN  = r'\)'
    # TODO : change to "ANGLE_BRACKET"
    CHEVRON = r'\>'

    LBRACKET = r'\['
    RBRACKET  = r'\]'
    EXCLAMATION_MARK  = r'\!'

    LITERAL = r'\#(\\\#|[^\#])+\#'

    GROUP_MULTIPLICITY = r'm\d+'
    USL_PATH = r':({role_regex}(\s{role_regex})*:)?((flexion|content):)?(((group_\d|constant):)?{term_regex})?'.format(role_regex=ROLE_REGEX,
                                                                                                                        term_regex=TERM_REGEX)

    DECORATION_VALUE = r'"(\\"|[^"])*"'

    ignore = '{} \t\n'

    # Error handling rule
    def error(self, t: Token):
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

