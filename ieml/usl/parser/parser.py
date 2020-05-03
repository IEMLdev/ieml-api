import logging, os
import ply.yacc as yacc

from ieml.constants import PARSER_FOLDER
from ieml.dictionary.script import script, Script, NullScript
from ieml.usl import Word, PolyMorpheme, USL
from ieml.exceptions import CannotParse
from ieml.usl.word import Lexeme
from ieml.usl.syntagmatic_function import SyntagmaticFunction, SyntagmaticRole
from .lexer import get_lexer, tokens
import threading

from ..decoration.instance import Decoration, InstancedUSL
from ..decoration.parser.parser import PathParser


class IEMLParserSingleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(IEMLParserSingleton, cls).__call__()

        return cls._instance


class IEMLParser():
    tokens = tokens
    lock = threading.Lock()

    def __init__(self, dictionary=None):
        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='proposition',
                                # debug=True,
                                optimize=False,
                                picklefile=os.path.join(PARSER_FOLDER, "ieml_parser.pickle"))
        self._ieml = None
        self.path_parser = PathParser()
        self.dictionary = dictionary

    def parse(self, s, factorize_script=False, auto_promote_to_USL=False):
        """Parses the input string, and returns a reference to the created AST's root"""
        if s == '':
            res = NullScript(0)
        else:
            if isinstance(s, (USL, Script)):
                s = str(s)

            with self.lock:
                self.factorize_script = factorize_script
                try:
                    res = self.parser.parse(s, lexer=self.lexer)
                except ValueError as e:
                    raise CannotParse(s, str(e))
                except CannotParse as e:
                    e.s = s
                    raise e

        if auto_promote_to_USL and isinstance(res, Script):
            res = PolyMorpheme(constant=[res])

        return res


    # Parsing rules
    def p_ieml_proposition(self, p):
        """proposition :  morpheme
                        | usl
                        | instanced_usl
                        """
        p[0] = p[1]

    def p_usl(self, p):
        """usl :  poly_morpheme
                | lexeme
                | word
                """
        p[0] = p[1]

    def p_instanced_usl(self, p):
        """instanced_usl : usl decoration_list"""
        p[0] = InstancedUSL(p[1], p[2])


    def p_morpheme(self, p):
        """morpheme : MORPHEME"""

        morpheme = script(p[1], factorize=self.factorize_script)

        if self.dictionary is not None and morpheme not in self.dictionary:
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

    def p_poly_morpheme(self, p):
        """ poly_morpheme : morpheme_sum group_list
                           | morpheme_sum
                           | group_list"""
        if len(p) == 3:
            p[0] = PolyMorpheme(constant=p[1], groups=p[2])
        elif isinstance(p[1][0], Script):
            p[0] = PolyMorpheme(constant=p[1], groups=())
        else:
            p[0] = PolyMorpheme(constant=[], groups=p[1])


    def p_lexeme(self, p):
        """lexeme : LPAREN poly_morpheme RPAREN LPAREN poly_morpheme RPAREN LPAREN poly_morpheme RPAREN
                  | LPAREN RPAREN LPAREN poly_morpheme RPAREN LPAREN poly_morpheme RPAREN
                  | LPAREN RPAREN LPAREN RPAREN LPAREN poly_morpheme RPAREN
                  | LPAREN poly_morpheme RPAREN LPAREN poly_morpheme RPAREN
                  | LPAREN RPAREN LPAREN poly_morpheme RPAREN
                  | LPAREN poly_morpheme RPAREN
                  | LPAREN RPAREN"""

        if len(p) == 10:
            p[0] = Lexeme(pm_flexion=PolyMorpheme(constant=p[2].constant + p[8].constant,
                                                  groups=p[2].groups + p[8].groups), pm_content=p[5])
        elif len(p) == 9:
            p[0] = Lexeme(pm_flexion=p[7], pm_content=p[4])
        elif len(p) == 8:
            p[0] = Lexeme(pm_flexion=p[6], pm_content=PolyMorpheme(constant=[]))
        elif len(p) == 7:
            p[0] = Lexeme(pm_flexion=p[2], pm_content=p[5])
        elif len(p) == 6:
            p[0] = Lexeme(pm_flexion=PolyMorpheme(constant=[]), pm_content=p[4])
        elif len(p) == 4:
            p[0] = Lexeme(pm_flexion=p[2], pm_content=PolyMorpheme(constant=[]))
        else:
            p[0] = Lexeme(pm_flexion=PolyMorpheme(constant=[]), pm_content=PolyMorpheme(constant=[]))

    def p_positioned_lexeme(self, p):
        """positioned_lexeme : morpheme_sum lexeme
                             | lexeme"""
        if len(p) == 3:
            p[0] = p[1], p[2]
        else:
            p[0] = [], p[1]

    def p_lexeme_list(self, p):
        """lexeme_list : lexeme_list RCHEVRON EXCLAMATION_MARK positioned_lexeme
                       | lexeme_list RCHEVRON positioned_lexeme
                       | EXCLAMATION_MARK positioned_lexeme
                       | positioned_lexeme"""
        if len(p) == 5:
            lex_list, _ = p[1]
            role, _ = p[4]
            p[0] = (lex_list + [p[4]], role)
        elif len(p) == 4:
            lex_list, address = p[1]
            p[0] = (lex_list + [p[3]], address)
        elif len(p) == 3:
            role, _ = p[2]
            p[0] = ([p[2]], role)
        else:
            p[0] = ([p[1]], None)

    def p_word(self, p):
        """word : LBRACKET OLD_MORPHEME_GRAMMATICAL_CLASS lexeme_list RBRACKET
                | LBRACKET lexeme_list RBRACKET"""

        if len(p) == 5:
            lex_list, role = p[3]
        else:
            lex_list, role = p[2]

        if not role:
            raise ValueError("No role specified in the syntagmatic function to build a word.")

        # try:
        ctx_type, sfun = SyntagmaticFunction.from_list(lex_list)
        # except IndexError as e:
        #     raise ValueError("Invalid lexeme parsed to create a word " + repr(e))

        p[0] = Word(syntagmatic_fun=sfun,
                    role=SyntagmaticRole(constant=role),
                    context_type=ctx_type)
        # check_word(p[0])
        # assert p[2] == p[0].grammatical_class


    def p_decoration_list(self, p):
        """decoration_list : decoration_list decoration
                            | decoration"""

        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]


    def p_decoration(self, p):
        """decoration : LBRACKET USL_PATH DECORATION_VALUE RBRACKET"""
        usl_path = self.path_parser.parse(p[2])
        p[0] = Decoration(usl_path, p[3][1:-1])


    def p_error(self, p):
        if p:
            msg = "Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos)
        else:
            msg = "Syntax error at EOF"

        raise CannotParse(None, msg)
