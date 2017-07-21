import ply.lex as lxr
import logging

logger = logging.getLogger(__name__)

tokens = (
   'PLUS',

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
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    return lxr.lex(module=module, errorlog=logging)

