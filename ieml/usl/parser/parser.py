import threading

from sly.yacc import YaccProduction

from .lexer import USLLexer
from .. import Word, PolyMorpheme
from ..decoration.instance import Decoration, InstancedUSL
from ..decoration.parser.parser import PathParser
from ..syntagmatic_function import SyntagmaticFunction, SyntagmaticRole
from ..word import Lexeme
from ...commons import BaseIEMLParser
from ...dictionary.script import script, NullScript
from ...exceptions import CannotParse


class USLParser(BaseIEMLParser):
    tokens = USLLexer.tokens
    lexer = USLLexer()
    start = "proposition"
    path_parser = PathParser()

    def __init__(self, dictionary=None):
        super().__init__()
        self.factorize_script = False
        self.dictionary = dictionary

    def parse(self, s: str, factorize_script: bool = False):
        """Parses the input string, and returns a reference to the created AST's root"""
        if s == '':
            return NullScript(0)

        with self.lock:
            self.factorize_script = factorize_script
            try:
                return super().parse(self.lexer.tokenize(s))
            except ValueError as e:
                raise CannotParse(s, str(e))
            except CannotParse as e:
                e.s = s
                raise e

    ### Parsing rules ###
    @_("morpheme",
       "usl",
       "instantiated_usl")
    def proposition(self, p: YaccProduction):
        return p[0]

    @_("poly_morpheme",
       "lexeme",
       "word")
    def usl(self, p: YaccProduction):
        return p[0]

    @_("usl decoration_list")
    def instantiated_usl(self, p):
        return InstancedUSL(p[1], p[2])

    @_("MORPHEME")
    def morpheme(self, p: YaccProduction):
        # TODO : ideally this should be in a lexer matching rule
        morpheme = script(p.MORPHEME, factorize=self.factorize_script)

        if self.dictionary is not None and morpheme not in self.dictionary:
            raise ValueError("Morpheme {} not defined in dictionary".format(morpheme))

        return morpheme

    @_("morpheme_sum morpheme",
       "morpheme")
    def morpheme_sum(self, p):
        if len(p) == 2:
            p.morpheme_sum.append(p.morpheme)
            return p.morpheme_sum
        else:
            return [p.morpheme]

    @_("GROUP_MULTIPLICITY LPAREN morpheme_sum RPAREN")
    def group(self, p: YaccProduction):
        return p.morpheme_sum, p.GROUP_MULTIPLICITY

    @_("group_list group",
       "group")
    def group_list(self, p: YaccProduction):
        if len(p) == 2:
            p.group_list.append(p.group)
            return p.group_list
        else:
            return [p.group]

    @_("group_list")
    def poly_morpheme(self, p: YaccProduction):
        return PolyMorpheme(constant=[], groups=p.group_list)

    @_("morpheme_sum group_list")
    def poly_morpheme(self, p: YaccProduction):
        return PolyMorpheme(constant=p.morpheme_sum, groups=p.group_list)

    @_("morpheme_sum")
    def poly_morpheme(self, p: YaccProduction):
        return PolyMorpheme(constant=p.morpheme_sum, groups=())

    @_("LPAREN poly_morpheme RPAREN")
    def filled_poly_morpheme(self, p: YaccProduction):
        """Wrapper for lexemes"""
        return p.poly_morpheme

    @_("LPAREN RPAREN")
    def empty_poly_morpheme(self, p: YaccProduction):
        """Wrapper for empty lexemes"""
        return PolyMorpheme(constant=[])

    @_("filled_poly_morpheme filled_poly_morpheme filled_poly_morpheme")
    def lexeme(self, p: YaccProduction):
        return Lexeme(pm_flexion=PolyMorpheme(constant=p[0].constant + p[2].constant,
                                              groups=p[0].groups + p[2].groups),
                      pm_content=p[1])

    @_("empty_poly_morpheme filled_poly_morpheme filled_poly_morpheme")
    def lexeme(self, p: YaccProduction):
        return Lexeme(pm_flexion=p[2], pm_content=p[1])

    @_("empty_poly_morpheme empty_poly_morpheme filled_poly_morpheme")
    def lexeme(self, p: YaccProduction):
        return Lexeme(pm_flexion=p[2], pm_content=PolyMorpheme(constant=[]))

    @_("filled_poly_morpheme filled_poly_morpheme")
    def lexeme(self, p: YaccProduction):
        return Lexeme(pm_flexion=p[0], pm_content=p[1])

    @_("empty_poly_morpheme filled_poly_morpheme")
    def lexeme(self, p: YaccProduction):
        return Lexeme(pm_flexion=PolyMorpheme(constant=[]), pm_content=p[1])

    @_("filled_poly_morpheme")
    def lexeme(self, p: YaccProduction):
        return Lexeme(pm_flexion=p[0], pm_content=PolyMorpheme(constant=[]))

    @_("empty_poly_morpheme")
    def lexeme(self, p: YaccProduction):
        return Lexeme(pm_flexion=PolyMorpheme(constant=[]), pm_content=PolyMorpheme(constant=[]))

    @_("morpheme_sum lexeme",
       "lexeme")
    def positioned_lexeme(self, p: YaccProduction):
        if len(p) == 2:
            return p.morpheme_sum, p.lexeme
        else:
            return [], p.lexeme

    @_("lexeme_list R_ANGLE_BRACKET EXCLAMATION_MARK positioned_lexeme")
    def lexeme_list(self, p: YaccProduction):
        lex_list, _ = p.lexeme_list
        role, _ = p.positioned_lexeme
        return lex_list + [p.positioned_lexeme], role

    @_("lexeme_list R_ANGLE_BRACKET positioned_lexeme")
    def lexeme_list(self, p: YaccProduction):
        lex_list, address = p.lexeme_list
        return lex_list + [p.positioned_lexeme], address

    @_("EXCLAMATION_MARK positioned_lexeme")
    def lexeme_list(self, p: YaccProduction):
        role, _ = p.positioned_lexeme
        return [p.positioned_lexeme], role

    @_("positioned_lexeme")
    def lexeme_list(self, p: YaccProduction):
        return [p.positioned_lexeme], None

    @_("LBRACKET OLD_MORPHEME_GRAMMATICAL_CLASS lexeme_list RBRACKET",
       "LBRACKET lexeme_list RBRACKET")
    def word(self, p: YaccProduction):
        lex_list, role = p.lexeme_list

        if not role:
            raise ValueError("No role specified in the syntagmatic function to build a word.")

        ctx_type, sfun = SyntagmaticFunction.from_list(lex_list)

        p[0] = Word(syntagmatic_fun=sfun,
                    role=SyntagmaticRole(constant=role),
                    context_type=ctx_type)

    @_("decoration_list decoration",
       "decoration")
    def decoration_list(self, p: YaccProduction):
        if len(p) == 2:
            p.decoration_list.append(p.decoration)
            return p.decoration_list
        else:
            return [p.decoration]

    @_("LBRACKET morpheme_sum DECORATION_VALUE RBRACKET")
    def decoration(self, p: YaccProduction):
        usl_path = self.path_parser.parse(p.morpheme_sum)
        p[0] = Decoration(usl_path, p.DECORATION[1:-1])

