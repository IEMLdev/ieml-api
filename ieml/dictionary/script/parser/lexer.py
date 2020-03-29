import ply.lex as lxr
from sly import Lexer
import logging

logger = logging.getLogger(__name__)




class ScriptLexer(Lexer):
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

    ignore_whitespace = ' \t\n'

    LAYER0_MARK = r'\:'
    LAYER1_MARK = r'\.'
    LAYER2_MARK = r'\-'
    LAYER3_MARK = r'[\'\’]'
    LAYER4_MARK = r'\,'
    LAYER5_MARK = r'\_'
    LAYER6_MARK = r'\;'

    PRIMITIVE = r'[EUASBT]'
    REMARKABLE_ADDITION = r'[OMFI]'
    REMARKABLE_MULTIPLICATION = r'wo|wa|y|o|e|wu|we|u|a|i|j|g|s|b|t|h|c|k|m|n|p|x|d|f|l'
    PLUS = r'\+'


    # Error handling rule
    def error(self, t):
        logger.log(logging.ERROR, "Illegal character '%s'" % t.value[0])
        # TODO change skipping rule
        t.lexer.skip(1)

