import logging
import threading
import os
from ply.yacc import yacc

from ieml.constants import PARSER_FOLDER
from ieml.dictionary.script import script
from ieml.exceptions import CannotParse
from ieml.usl.constants import ROLE_NAMES_TO_SCRIPT
from ieml.usl.decoration.parser.lexer import tokens, get_lexer
from ieml.usl.decoration.path import UslPath, RolePath, LexemePath, PolymorphemePath, LexemeIndex, GroupIndex, \
    FlexionPath
from ieml.usl.syntagmatic_function import SyntagmaticRole


class PathParser:
    tokens = tokens
    lock = threading.Lock()

    def __init__(self):
        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc(module=self, errorlog=logging, start='path',
                                  # debug=True, debuglog=logging,
                                  optimize=False,
                                  picklefile=os.path.join(PARSER_FOLDER, "path_parser.pickle"))

    def parse(self, s):
        if not isinstance(s, str):
            s = str(s)

        with self.lock:
            try:
                return self.parser.parse(s, lexer=self.lexer)
            except ValueError as e:
                raise CannotParse(s, str(e))
            except CannotParse as e:
                e.s = s
                raise e

    def p_path(self, p):
        """path : SEPARATOR
                | SEPARATOR role_path
                | SEPARATOR lexeme_path
                | SEPARATOR flexion_path
                | SEPARATOR polymorpheme_path"""

        if len(p) == 2:
            p[0] = UslPath()
        else:
            p[0] = p[2]

    def p_role_path_list(self, p):
        """role_path_list : role_path_list MORPHEME
                            | MORPHEME
                            | role_path_list ROLE_NAME
                            | ROLE_NAME"""
        if len(p) == 2:
            s = p[1]
            if s in ROLE_NAMES_TO_SCRIPT:
                s = ROLE_NAMES_TO_SCRIPT[s]
            else:
                s = script(s)

            p[0] = [s]
        else:
            s = p[2]
            if s in ROLE_NAMES_TO_SCRIPT:
                s = ROLE_NAMES_TO_SCRIPT[s]
            else:
                s = script(s)

            p[0] = p[1] + [s]

    def p_role_path(self, p):
        """role_path : ROLE_TOKEN SEPARATOR role_path_list
                     | ROLE_TOKEN SEPARATOR EXCLAMATION_MARK role_path_list
                     | ROLE_TOKEN SEPARATOR role_path_list SEPARATOR lexeme_path
                     | ROLE_TOKEN SEPARATOR EXCLAMATION_MARK role_path_list SEPARATOR lexeme_path"""
        if len(p) == 4:
            p[0] = RolePath(SyntagmaticRole(p[3]))
        elif len(p) == 5:
            p[0] = RolePath(SyntagmaticRole(p[4]), has_focus=True)
        elif len(p) == 6:
            p[0] = RolePath(SyntagmaticRole(p[3]), child=p[5])
        else:
            p[0] = RolePath(SyntagmaticRole(p[4]), has_focus=True, child=p[6])

    def p_lexeme_path(self, p):
        """lexeme_path : LEXEME_POSITION
                        | LEXEME_POSITION SEPARATOR polymorpheme_path
                        | LEXEME_POSITION SEPARATOR flexion_path """
        lex_index = LexemeIndex[p[1].upper()]
        if len(p) == 2:
            p[0] = LexemePath(lex_index)
        else:
            child = p[3]
            if lex_index == LexemeIndex.CONTENT and not isinstance(child, PolymorphemePath):
                raise CannotParse(None, "Invalid child of lexeme path in content position, expected a PolymorphemePath, not a " + child.__class__.__name__)

            if lex_index == LexemeIndex.FLEXION and not isinstance(child, FlexionPath):
                raise CannotParse(None, "Invalid child of lexeme path in flexion position, expected a FlexionPath, not a " + child.__class__.__name__)

            p[0] = LexemePath(lex_index, child=child)

    def p_flexion_path(self, p):
        """flexion_path : MORPHEME """
        p[0] = FlexionPath(script(p[1]))

    def p_polymorpheme_path(self, p):
        """polymorpheme_path : POLYMORPHEME_POSITION SEPARATOR MORPHEME
                             | POLYMORPHEME_POSITION MULTIPLICITY SEPARATOR MORPHEME"""
        if len(p) == 4:
            group_idx = GroupIndex[p[1].upper()]
            morpheme = script(p[3])
            p[0] = PolymorphemePath(group_idx, morpheme)
        else:
            group_idx = GroupIndex[p[1].upper()]
            morpheme = script(p[4])
            p[0] = PolymorphemePath(group_idx, morpheme, multiplicity=int(p[2]))



    def p_error(self, p):
        if p:
            msg = "Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos)
        else:
            msg = "Syntax error at EOF"

        raise CannotParse(None, msg)
