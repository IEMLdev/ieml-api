import logging
import ply.yacc as yacc
from ply.lex import LexToken

from ieml.constants import MORPHEMES_GRAMMATICAL_MARKERS
from ieml.dictionary.script import script, Script
from ieml.dictionary.script.script import NULL_SCRIPTS
from ieml.exceptions import InvalidIEMLObjectArgument


from ieml.lexicon.syntax import Trait, Character, Word, MorphemeSerie
from ieml.exceptions import CannotParse

from .lexer import get_lexer, tokens
import threading


class IEMLParserSingleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        # dictionary = args[0] if len(args) > 0 else \
        #     kwargs['dictionary'] if 'dictionary' in kwargs else None

        # if dictionary is None:
        #     dictionary = Dictionary.load()

        # if not isinstance(dictionary, Dictionary):
        #     dictionary = Dictionary.load(dictionary)

        if cls._instance is None:
            # this code is to clean up duplicate class if we reload modules
            cls._instance = super(IEMLParserSingleton, cls).__call__()

        return cls._instance


class IEMLParser():
    tokens = tokens
    lock = threading.Lock()

    def __init__(self, dictionary=None):
        # from ieml.dictionary.tools import term

        # self._get_term = partial(term, dictionary=dictionary)

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='proposition',
                                debug=True, optimize=True,)
                                # picklefile=os.path.join(PARSER_FOLDER, "ieml_parser2.pickle"))
        self._ieml = None

        self.dictionary = dictionary
    def parse(self, s):
        """Parses the input string, and returns a reference to the created AST's root"""
        with self.lock:
            try:
                return self.parser.parse(s, lexer=self.lexer)
            except ValueError as e:
                raise CannotParse(s, str(e))
            except CannotParse as e:
                e.s = s
                raise e


    # Parsing rules
    def p_ieml_proposition(self, p):
        """proposition : morpheme_serie
                        | trait
                        | character
                        | word"""
        p[0] = p[1]

    # def p_literal_list(self, p):
    #     """literal_list : literal_list LITERAL
    #                     | LITERAL"""
    #
    #     if len(p) == 3:
    #         p[0] = p[1] + [p[2][1:-1]]
    #     else:
    #         p[0] = [p[1][1:-1]]


    def p_morpheme(self, p):
        """morpheme : MORPHEME"""
                    # | MORPHEME literal_list"""

        morpheme = script(p[1])
        if len(p) == 3:
            logging.error("Literals not supported on script for the moments, and are ignored.")

        if self.dictionary is not None and morpheme not in self.dictionary.scripts:
            raise ValueError("Morpheme {} not defined in dictionary".format(morpheme))

        p[0] = morpheme

    def p_morpheme_sum(self, p):
        """morpheme_sum : morpheme_sum morpheme
                        | morpheme"""

        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_group(self, p):
        """ group : GROUP_MULTIPLICITY LPAREN morpheme_sum RPAREN """
        p[0] = (p[3], int(p[1][1:]))

    def p_group_list(self, p):
        """ group_list : group group_list
                       | group """
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]

    def p_morpheme_serie(self, p):
        """ morpheme_serie : morpheme_sum group_list
                           | morpheme_sum
                           | group_list"""
        if len(p) == 3:
            p[0] = MorphemeSerie(constant=p[1], groups=p[2])
        elif isinstance(p[1][0], Script):
            p[0] = MorphemeSerie(constant=p[1], groups=())
        else:
            p[0] = MorphemeSerie(constant=[], groups=p[1])

    def p_trait(self, p):
        """trait : LCHEVRON LCHEVRON morpheme_serie RCHEVRON morpheme_serie RCHEVRON
                 | LCHEVRON LCHEVRON morpheme_serie RCHEVRON RCHEVRON"""

        if len(p) == 7:
            # full paradigm
            p[0] = Trait(core=p[3], periphery=p[5])
        else:
            p[0] = Trait(core=p[3], periphery=MorphemeSerie())

        #     # half paradigm
        #     if isinstance(p[5], LexToken):
        #         p[0] = Trait(content=p[3], groups_content=p[4], periphery=p[6])
        #     else:
        #         p[0] = Trait(content=p[3], periphery=p[5], groups_periphery=p[6])
        # elif len(p) == 7:
        #     # content and functions
        #     if isinstance(p[4], LexToken):
        #         p[0] = Trait(content=p[3], periphery=p[5])
        #     else:
        #         p[0] = Trait(content=p[3], groups_content=p[4], periphery=[])
        # else:
        #     p[0] = Trait(content=p[3], periphery=[])

    def p_trait_sum(self, p):
        """trait_sum : trait_sum trait
                     | trait"""

        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_class_trait(self, p):
        """ class_trait : LCHEVRON morpheme RCHEVRON"""
        morpheme = p[2]
        if str(morpheme) not in MORPHEMES_GRAMMATICAL_MARKERS:
            raise ValueError("Morpheme {} is not a valid grammatical class morpheme, must be taken from [{}] or "
                             "E: (empty trait)".format(str(p[2]), ', '.join(map(str, MORPHEMES_GRAMMATICAL_MARKERS))))

        p[0] = morpheme

    def p_character(self, p):
        """character : LBRACKET class_trait trait_sum RBRACKET
                     | LBRACKET class_trait RBRACKET"""
        if len(p) == 5:
            p[0] = Character(klass=p[2], content=p[3][0], functions=p[3][1:])
        else:
            if not p[2].empty:
                raise ValueError("Invalid grammatical class {}, the empty character must be noted [<E:>]"
                                 .format(str(p[2])))

            p[0] = Character(klass=p[2], content=Trait(core=MorphemeSerie(), periphery=MorphemeSerie()))

    def p_word(self, p):
        """word : LPAREN character TIMES character TIMES character RPAREN"""
        p[0] = Word(substance=p[2], attribute=p[4], mode=p[6])

    def p_error(self, p):
        if p:
            msg = "Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos)
        else:
            msg = "Syntax error at EOF"

        raise CannotParse(None, msg)
